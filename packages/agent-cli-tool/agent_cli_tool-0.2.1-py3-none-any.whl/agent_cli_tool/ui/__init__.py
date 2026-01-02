"""UI package for agent-cli-tool.

This package provides different rendering backends:
- base: Base renderer class with user input handling
- stdout: Plain text output to terminal
- rich: Markdown-formatted output using Rich library
- tui: Interactive Textual-based TUI application
"""

from .base import BaseRenderer
from .stdout import StdoutRenderer
from .rich import RichRenderer
from .tui import TUIRenderer, ChatApp

__all__ = [
    "BaseRenderer",
    "StdoutRenderer",
    "RichRenderer",
    "TUIRenderer",
    "ChatApp",
]


def create_renderer(mode: str, **kwargs) -> BaseRenderer:
    """Factory function to create renderer based on mode.

    Args:
        mode: Renderer mode ("stdout", "rich", or "tui")
        **kwargs: Additional arguments passed to renderer

    Returns:
        BaseRenderer instance

    Raises:
        ValueError: If mode is not supported
    """
    config = kwargs.pop("config", {})

    user_emoji: str = config.get("USER_EMOJI") or "💬:"
    ai_emoji: str = config.get("AI_EMOJI") or "🤖:"
    think_start_emoji: str = config.get("THINK_START_EMOJI") or "🤔 [Start Thinking]"
    think_end_emoji: str = config.get("THINK_END_EMOJI") or "💡 [End Thinking]"
    rich_style = config.get("RICH_STYLE") or "github-dark"
    args = {
        "user_emoji": user_emoji,
        "ai_emoji": ai_emoji,
        "think_start_emoji": think_start_emoji,
        "think_end_emoji": think_end_emoji,
    }
    if mode == "stdout":
        return StdoutRenderer(**args)
    elif mode == "rich":
        return RichRenderer(rich_style, **args)
    elif mode == "tui":
        return TUIRenderer(
            think_start_emoji=think_start_emoji,
            think_end_emoji=think_end_emoji,
            **kwargs,
        )
    else:
        raise ValueError(f"Unsupported renderer mode: {mode}")
