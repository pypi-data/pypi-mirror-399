"""Chat log widget with Vibe-inspired styling and streaming support."""

from collections.abc import Callable
from typing import Any

from rich.text import Text
from textual.widgets import Static

from miu_code.tui.theme import SEMANTIC_COLORS, VIBE_COLORS
from miu_code.tui.widgets.messages import AssistantMessage, UserMessage


class ChatLog(Static):
    """Chat log container with streaming support (like mistral-vibe's #messages)."""

    DEFAULT_CSS = """
    ChatLog {
        layout: stream;
        width: 100%;
        height: auto;
    }
    ChatLog > Static.message-text {
        height: auto;
        width: 100%;
        margin-left: 2;
        margin-bottom: 1;
    }
    ChatLog > Static.tool-info {
        height: auto;
        width: 100%;
        margin-left: 2;
    }
    """

    def __init__(self, scroll_callback: Callable[[], None] | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._streaming_msg: AssistantMessage | None = None
        self._streaming_mounted: bool = False
        self._scroll_callback = scroll_callback

    def on_resize(self) -> None:
        """Refresh on resize to ensure proper layout."""
        self.refresh()

    def _notify_scroll(self) -> None:
        """Notify parent to scroll."""
        if self._scroll_callback:
            self._scroll_callback()

    def clear(self) -> None:
        """Clear all messages from the chat log."""
        self.remove_children()

    def add_user_message(self, text: str) -> None:
        """Add a user message to the log."""
        msg = UserMessage(text)
        self.mount(msg)
        self._notify_scroll()

    def add_assistant_message(self, text: str) -> None:
        """Add a complete assistant message to the log."""
        msg = AssistantMessage(text)
        self.mount(msg)
        self._notify_scroll()

    async def start_streaming(self) -> None:
        """Prepare for streaming - widget is mounted on first content."""
        # Don't mount yet - wait for actual content
        self._streaming_msg = None
        self._streaming_mounted = False

    async def append_streaming(self, chunk: str) -> None:
        """Append text to streaming message, mounting on first chunk."""
        if not chunk:
            return

        # Mount on first content (like mistral-vibe)
        if not self._streaming_mounted:
            self._streaming_msg = AssistantMessage(chunk)
            self.mount(self._streaming_msg)
            self._streaming_mounted = True
        elif self._streaming_msg:
            await self._streaming_msg.append_content(chunk)

        self._notify_scroll()

    async def end_streaming(self) -> None:
        """Finalize streaming message."""
        if self._streaming_msg:
            await self._streaming_msg.stop_stream()
        self._streaming_msg = None
        self._streaming_mounted = False
        self._notify_scroll()

    def add_system_message(self, text: str) -> None:
        """Add a system message to the log."""
        sys_text = Text()
        sys_text.append("→ ", style=f"dim {VIBE_COLORS['orange_gold']}")
        sys_text.append(text, style=f"dim {SEMANTIC_COLORS['system']}")
        msg = Static(sys_text, classes="message-text")
        self.mount(msg)
        self._notify_scroll()

    def add_error(self, text: str) -> None:
        """Add an error message to the log."""
        err_text = Text()
        err_text.append("✗ ", style=f"bold {SEMANTIC_COLORS['error']}")
        err_text.append(text, style=SEMANTIC_COLORS["error"])
        msg = Static(err_text, classes="message-text")
        self.mount(msg)
        self._notify_scroll()

    def add_thinking_message(self, text: str) -> None:
        """Add a thinking/reasoning message to the log."""
        think_text = Text()
        think_text.append("◌ ", style=f"italic {SEMANTIC_COLORS['thinking']}")
        think_text.append(text, style=f"italic dim {SEMANTIC_COLORS['thinking']}")
        msg = Static(think_text, classes="message-text")
        self.mount(msg)
        self._notify_scroll()

    def add_tool_call(self, tool_name: str, args: str = "") -> None:
        """Add a tool call indicator to the log."""
        tool_text = Text()
        tool_text.append("⚡ ", style=f"bold {VIBE_COLORS['orange']}")
        tool_text.append("Calling: ", style="dim")
        tool_text.append(tool_name, style=f"bold {VIBE_COLORS['orange_gold']}")
        if args:
            tool_text.append(f" {args}", style="dim")
        msg = Static(tool_text, classes="tool-info")
        self.mount(msg)
        self._notify_scroll()

    def add_tool_result(self, result: str, success: bool = True) -> None:
        """Add a tool result to the log."""
        color = SEMANTIC_COLORS["assistant"] if success else SEMANTIC_COLORS["error"]
        icon = "✓" if success else "✗"
        result_text = Text()
        result_text.append(f"  {icon} ", style=f"bold {color}")
        # Truncate long results
        display_result = result[:100] + "..." if len(result) > 100 else result
        result_text.append(display_result, style=f"dim {color}")
        msg = Static(result_text, classes="tool-info")
        self.mount(msg)
        self._notify_scroll()
