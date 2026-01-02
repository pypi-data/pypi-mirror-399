"""Rich renderer - Markdown-formatted output using Rich library."""

from .base import BaseRenderer


class RichRenderer(BaseRenderer):
    """Markdown renderer using Rich library with live streaming."""

    def __init__(self, style: str = "github-dark", **kwargs):
        """Initialize Rich renderer.

        Args:
            style: Pygments code theme for syntax highlighting
            **kwargs: Additional arguments passed to BaseRenderer
        """
        super().__init__(**kwargs)
        self.style = style

        # Import Rich components
        import time
        from rich.console import Console
        from rich.live import Live
        from rich.markdown import Markdown

        self._get_time = lambda: time.time()
        self._markdown_clz = Markdown
        self._live_clz = Live
        self._console = Console()

    def render_ai_info(self, model: str) -> None:
        """Render AI model information using Rich console."""
        self._console.print(f"[bold green]({model})[/bold green] {self.ai_emoji}")

    def render_user_info(self, status: str) -> None:
        """Render user input prompt in blue color."""
        self._console.print(f"[bold blue]({status})[/bold blue] {self.user_emoji}")

    def render_user_input(self, user_input: str) -> None:
        """Render user input using markdown."""
        self._console.print(self._markdown_clz(user_input, code_theme=self.style))

    def stream_response(self, response, ignore_think: bool) -> str:
        """Stream AI response with live markdown rendering."""
        console = self._console
        has_thinking = False

        # Full content buffer for final output
        full_buffer: list[str] = [""]

        # Visible content buffer (limited to terminal height)
        visible_lines: list[str] = [""]

        char_queue: list[str] = []
        render_interval = 0.02
        last_render = 0.0

        def push_char(buf: list[str], ch: str):
            """Append a character to a buffer, handling newlines."""
            if not buf:
                buf.append("")
            if ch == "\n":
                buf.append("")
            else:
                buf[-1] += ch

        def sync_visible():
            """Sync visible content to terminal height."""
            height = console.size.height
            # Leave 1 line buffer to avoid jitter
            max_lines = max(3, height - 1)
            return "\n".join(visible_lines[-max_lines:])

        with self._live_clz(
            "",
            console=console,
            refresh_per_second=30,
            vertical_overflow="crop",
            transient=True,
        ) as live:
            for chunk in response:
                delta = chunk.choices[0].delta

                # Regular content
                if hasattr(delta, "content") and delta.content:
                    if has_thinking:
                        has_thinking = False
                        char_queue.extend(f"\n> {self.think_end_emoji}\n\n")

                    char_queue.extend(delta.content)

                # Thinking content
                if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                    if not ignore_think:
                        if not has_thinking:
                            has_thinking = True
                            char_queue.extend(f"\n> {self.think_start_emoji}\n\n")
                        char_queue.extend(delta.reasoning_content)

                # Flush characters to output
                now = self._get_time()
                if char_queue and (now - last_render) >= render_interval:
                    burst = 5
                    for _ in range(min(burst, len(char_queue))):
                        ch = char_queue.pop(0)
                        push_char(full_buffer, ch)
                        push_char(visible_lines, ch)

                    live.update(
                        self._markdown_clz(
                            sync_visible(),
                            code_theme=self.style,
                        )
                    )
                    last_render = now

            # Flush remaining characters
            while char_queue:
                ch = char_queue.pop(0)
                push_char(full_buffer, ch)
                push_char(visible_lines, ch)

            live.update(
                self._markdown_clz(
                    sync_visible(),
                    code_theme=self.style,
                )
            )

            live.update("")

        ai_reply = "\n".join(full_buffer).strip()

        # Print final formatted output
        self._console.print(
            self._markdown_clz(
                ai_reply,
                code_theme=self.style,
            )
        )

        return ai_reply
