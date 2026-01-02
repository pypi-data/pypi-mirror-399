"""Stdout renderer - plain text output to terminal."""

from .base import BaseRenderer


class StdoutRenderer(BaseRenderer):
    """Plain text renderer for terminal output."""

    def render_ai_info(self, model: str) -> None:
        """Render AI model information in green color."""
        self.output_io.write(f"\033[32m({model})\033[0m {self.ai_emoji}\n")

    def render_user_info(self, status: str) -> None:
        """Render user input prompt in blue color."""
        self.output_io.write(f"\033[94m({status})\033[0m {self.user_emoji}\n")

    def render_user_input(self, user_input: str) -> None:
        """Render user input text."""
        self.output_io.write(f"{user_input}\n")

    def stream_response(self, response, ignore_think: bool) -> str:
        """Stream AI response with basic ANSI colors."""
        ai_reply = ""
        has_thinking = False

        for chunk in response:
            delta = chunk.choices[0].delta

            # Regular content
            if hasattr(delta, "content") and delta.content:
                if has_thinking:
                    has_thinking = False
                    self.output_io.write(
                        f"\033[0m\n\033[1;36m{self.think_end_emoji}\033[0m\n"
                    )

                content = delta.content
                self.output_io.write(content)
                ai_reply += content

            # Thinking/reasoning content
            if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                if ignore_think:
                    continue

                if not has_thinking:
                    has_thinking = True
                    self.output_io.write(
                        f"\033[1;36m{self.think_start_emoji}\033[0m\n\033[3m"
                    )
                self.output_io.write(delta.reasoning_content)

            self.output_io.flush()

        self.output_io.write("\n")
        return ai_reply
