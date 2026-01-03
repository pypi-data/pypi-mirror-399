"""Custom TextArea for chat input with history support."""

from typing import Any

from textual.message import Message
from textual.widgets import TextArea

InputMode = str  # ">", "!", "/"


class ChatTextArea(TextArea):
    """TextArea with chat-specific features."""

    class Submitted(Message):
        """Input submitted."""

        def __init__(self, value: str) -> None:
            self.value = value
            super().__init__()

    class ModeChanged(Message):
        """Input mode changed."""

        def __init__(self, mode: InputMode) -> None:
            self.mode = mode
            super().__init__()

    class HistoryPrevious(Message):
        """Request previous history entry."""

        def __init__(self, prefix: str) -> None:
            self.prefix = prefix
            super().__init__()

    class HistoryNext(Message):
        """Request next history entry."""

        def __init__(self, prefix: str) -> None:
            self.prefix = prefix
            super().__init__()

    class HistoryReset(Message):
        """Reset history navigation."""

        pass

    DEFAULT_CSS = """
    ChatTextArea {
        height: auto;
        max-height: 16;
        border: none;
        background: transparent;
        padding: 0;
        scrollbar-visibility: hidden;
    }
    """

    def __init__(
        self,
        placeholder: str = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._placeholder = placeholder
        self._input_mode: InputMode = ">"
        self._completion_manager: Any = None
        self._navigating_history = False
        self._original_text = ""
        self._last_used_prefix: str | None = None
        self._last_cursor_col: int = 0
        self._cursor_pos_after_load: tuple[int, int] | None = None
        self._cursor_moved_since_load = False

    @property
    def input_mode(self) -> InputMode:
        """Current input mode based on first character."""
        return self._input_mode

    def set_mode(self, mode: InputMode) -> None:
        """Set input mode."""
        if mode != self._input_mode:
            self._input_mode = mode
            self.post_message(self.ModeChanged(mode))

    def get_full_text(self) -> str:
        """Get full input text including mode prefix."""
        text = self.text
        if self._input_mode == ">":
            return text
        return f"{self._input_mode}{text}"

    def load_text(self, text: str) -> None:
        """Load text into editor using parent's load_text method."""
        # Call parent's load_text which handles text replacement properly
        # without triggering recursive reactive updates
        super().load_text(text)

    def clear_text(self) -> None:
        """Clear the text area."""
        super().load_text("")
        self._input_mode = ">"

    def set_cursor_offset(self, offset: int) -> None:
        """Set cursor position by offset."""
        lines = self.text.split("\n")
        pos = 0
        for row, line in enumerate(lines):
            if pos + len(line) >= offset:
                col = offset - pos
                self.move_cursor((row, col))
                return
            pos += len(line) + 1
        # End of text
        if lines:
            self.move_cursor((len(lines) - 1, len(lines[-1])))

    def _get_full_cursor_offset(self) -> int:
        """Get cursor offset in full text."""
        row, col = self.cursor_location
        lines = self.text.split("\n")
        offset = sum(len(lines[i]) + 1 for i in range(row)) + col
        return offset

    def set_completion_manager(self, manager: Any) -> None:
        """Set completion manager for auto-completion."""
        self._completion_manager = manager

    def reset_history_state(self) -> None:
        """Reset history navigation state."""
        self._navigating_history = False
        self._original_text = ""
        self._cursor_pos_after_load = None
        self._cursor_moved_since_load = False

    async def _on_key(self, event: Any) -> None:
        """Handle key events."""
        key = event.key

        # Submit on Enter (without shift) - in Textual, shift+enter is a separate key
        if key == "enter":
            event.prevent_default()
            full_text = self.get_full_text().strip()
            if full_text:
                self.post_message(self.Submitted(full_text))
            return

        # History navigation
        if key == "up" and self._at_first_line():
            event.prevent_default()
            prefix = self._get_current_prefix()
            self.post_message(self.HistoryPrevious(prefix))
            return

        if key == "down" and self._at_last_line():
            event.prevent_default()
            prefix = self._get_current_prefix()
            self.post_message(self.HistoryNext(prefix))
            return

        # Mode detection on first character
        if key in ("!", "/") and self.text == "":
            self.set_mode(key)
            return

        # Reset history on edit
        if self._navigating_history and key not in ("up", "down", "left", "right"):
            self.post_message(self.HistoryReset())
            self._navigating_history = False

        await super()._on_key(event)

        # Update mode based on content
        self._update_mode_from_text()

        # Notify completion manager
        if self._completion_manager:
            self._completion_manager.on_text_changed(
                self.get_full_text(), self._get_full_cursor_offset()
            )

    def _at_first_line(self) -> bool:
        """Check if cursor is on first line."""
        row, _ = self.cursor_location
        return row == 0

    def _at_last_line(self) -> bool:
        """Check if cursor is on last line."""
        row, _ = self.cursor_location
        lines = self.text.split("\n")
        return row >= len(lines) - 1

    def _get_current_prefix(self) -> str:
        """Get text before cursor as prefix for history search."""
        row, col = self.cursor_location
        if row == 0:
            return self.text[:col]
        return ""

    def _update_mode_from_text(self) -> None:
        """Update mode based on current text."""
        # Mode is sticky once set
        pass
