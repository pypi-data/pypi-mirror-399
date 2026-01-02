"""Base renderer with shared functionality."""

import sys
from abc import ABC, abstractmethod
from typing import TextIO


class BaseRenderer(ABC):
    """Base class for all UI renderers."""

    def __init__(
        self,
        user_emoji: str = "💬:",
        ai_emoji: str = "🤖:",
        think_start_emoji: str = "🤔 [Start Thinking]",
        think_end_emoji: str = "💡 [End Thinking]",
    ):
        """Initialize the renderer.

        Args:
            user_emoji: Emoji for user messages
            ai_emoji: Emoji for AI messages
            think_start_emoji: Emoji for thinking start
            think_end_emoji: Emoji for thinking end
        """
        self.output_io = sys.stdout
        self.user_emoji = user_emoji
        self.ai_emoji = ai_emoji
        self.think_start_emoji = think_start_emoji
        self.think_end_emoji = think_end_emoji

        # State for user input handling
        self._pipe_consumed = False
        self._tty_file: TextIO | None = None

    @abstractmethod
    def render_ai_info(self, model: str) -> None:
        """Render AI model information.

        Args:
            model: Model name to display
        """
        pass

    @abstractmethod
    def render_user_info(self, status: str) -> None:
        """Render user input prompt.

        Args:
            status: Status text to display
        """
        pass

    @abstractmethod
    def render_user_input(self, user_input: str) -> None:
        """Render user input text.

        Args:
            user_input: User input text to display
        """
        pass

    @abstractmethod
    def stream_response(self, response, ignore_think: bool) -> str:
        """Stream AI response to output.

        Args:
            response: OpenAI streaming response object
            ignore_think: Whether to ignore thinking content

        Returns:
            The complete AI reply as a string
        """
        pass

    def flush(self) -> None:
        """Flush the output buffer."""
        self.output_io.flush()

    def get_user_input(self, cli_args, need_user_input: bool = True) -> str:
        """
        获取用户输入（用于 stdout 和 rich 模式）：
        - Enter = 换行
        - Ctrl+D = 发送
        - Ctrl+C = 中断
        - Backspace 支持中文 / emoji / ZWJ emoji

        Args:
            cli_args: Command line arguments
            need_user_input: Whether user input is needed

        Returns:
            User input string
        """
        import tty
        import termios
        from wcwidth import wcswidth

        def append_grapheme(buffer: list[str], ch: str):
            """将字符追加为"用户感知字符（grapheme）"，支持 ZWJ emoji"""
            ZWJ = "\u200d"
            if buffer and (ch == ZWJ or buffer[-1].endswith(ZWJ)):
                buffer[-1] += ch
            else:
                buffer.append(ch)

        try:
            if not need_user_input:
                return sys.stdin.read().strip() if not sys.stdin.isatty() else ""

            # ===== 提示 =====
            if not cli_args.ignore_user:
                status = "Use ^D to send" if sys.stdin.isatty() else "Pipe-Prompt"
                self.render_user_info(status)

            # ===== 非 TTY（管道输入）=====
            if not sys.stdin.isatty():
                if not self._pipe_consumed:
                    need_return = True
                    user_input = sys.stdin.read().strip()
                    if not user_input:
                        if cli_args.conversation:
                            need_return = False
                        else:
                            return ""

                    self._pipe_consumed = True
                    if need_return:
                        self.render_user_input(user_input)
                        self.flush()
                        return user_input

                if not cli_args.conversation:
                    return ""

                if self._tty_file is None:
                    try:
                        self._tty_file = open("/dev/tty", "r")
                    except Exception:
                        return ""
            else:
                self._tty_file = sys.stdin

            fd = self._tty_file.fileno()

            # ===== TTY 交互模式 =====
            old_settings = termios.tcgetattr(fd)
            user_buffer: list[list[str]] = [[]]

            try:
                tty.setraw(fd)
                while ch := self._tty_file.read(1):
                    # ===== Ctrl+D：发送 =====
                    if ch == "\x04":
                        self.output_io.write("\r\n")
                        self.output_io.flush()
                        break

                    # ===== Ctrl+C：中断 =====
                    elif ch == "\x03":
                        self.output_io.write("^C\r\n")
                        self.output_io.flush()
                        return ""

                    # ===== Enter：换行（不发送）=====
                    elif ch in ("\r", "\n"):
                        user_buffer.append([])
                        self.output_io.write("\r\n")
                        self.output_io.flush()

                    # ===== Backspace =====
                    elif ch in ("\x7f", "\x08"):
                        if user_buffer[-1]:
                            last = user_buffer[-1].pop()
                            width = max(1, wcswidth(last))
                            self.output_io.write(
                                "".join(i * width for i in ("\b", " ", "\b"))
                            )
                        elif len(user_buffer) > 1:
                            user_buffer.pop()
                            prev_line = user_buffer[-1]
                            # 上移一行并清空当前行显示
                            self.output_io.write("\x1b[F\x1b[2K")
                            # 重新打印上一行
                            self.output_io.write("".join(prev_line))

                        self.output_io.flush()

                    # ===== 普通字符 / emoji =====
                    else:
                        append_grapheme(user_buffer[-1], ch)
                        self.output_io.write(ch)
                        self.output_io.flush()

            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

            return "\n".join("".join(line) for line in user_buffer).strip()

        except KeyboardInterrupt:
            return ""

    def close(self) -> None:
        """Close any open resources."""
        if self._tty_file is not None and self._tty_file is not sys.stdin:
            self._tty_file.close()
