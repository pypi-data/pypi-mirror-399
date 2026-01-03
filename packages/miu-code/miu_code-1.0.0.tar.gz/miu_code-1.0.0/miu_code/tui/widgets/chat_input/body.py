"""Chat input body with prompt and text area."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static

from miu_code.tui.widgets.chat_input.history import HistoryManager
from miu_code.tui.widgets.chat_input.text_area import ChatTextArea


class ChatInputBody(Widget):
    """Chat input with prompt indicator and text area."""

    class Submitted(Message):
        """Input submitted."""

        def __init__(self, value: str) -> None:
            self.value = value
            super().__init__()

    DEFAULT_CSS = """
    ChatInputBody {
        height: auto;
        width: 100%;
    }
    """

    def __init__(self, history_file: Path | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.input_widget: ChatTextArea | None = None
        self.prompt_widget: Static | None = None
        self._history = HistoryManager(history_file) if history_file else None
        self._completion_reset: Callable[[], None] | None = None

    def compose(self) -> ComposeResult:
        with Horizontal():
            self.prompt_widget = Static(">", id="prompt")
            yield self.prompt_widget
            self.input_widget = ChatTextArea(placeholder="Ask anything...", id="input")
            yield self.input_widget

    def on_mount(self) -> None:
        if self.input_widget:
            self.input_widget.focus()

    @property
    def value(self) -> str:
        """Get current input value."""
        if not self.input_widget:
            return ""
        return self.input_widget.get_full_text()

    @value.setter
    def value(self, text: str) -> None:
        """Set input value."""
        if self.input_widget:
            # Parse mode from text
            if text.startswith("!"):
                self.input_widget.set_mode("!")
                self.input_widget.load_text(text[1:])
            elif text.startswith("/"):
                self.input_widget.set_mode("/")
                self.input_widget.load_text(text[1:])
            else:
                self.input_widget.set_mode(">")
                self.input_widget.load_text(text)
            self._update_prompt()

    def focus_input(self) -> None:
        """Focus the input widget."""
        if self.input_widget:
            self.input_widget.focus()

    def _update_prompt(self) -> None:
        """Update prompt based on current mode."""
        if self.input_widget and self.prompt_widget:
            self.prompt_widget.update(self.input_widget.input_mode)

    def on_chat_text_area_mode_changed(self, event: ChatTextArea.ModeChanged) -> None:
        """Handle mode change."""
        if self.prompt_widget:
            self.prompt_widget.update(event.mode)

    def on_chat_text_area_submitted(self, event: ChatTextArea.Submitted) -> None:
        """Handle submission."""
        event.stop()
        value = event.value.strip()
        if value:
            if self._history:
                self._history.add(value)
                self._history.reset_navigation()
            if self.input_widget:
                self.input_widget.clear_text()
            self._update_prompt()
            if self._completion_reset:
                self._completion_reset()
            self.post_message(self.Submitted(value))

    def on_chat_text_area_history_previous(self, event: ChatTextArea.HistoryPrevious) -> None:
        """Handle history previous."""
        if not self._history or not self.input_widget:
            return
        if self._history._current_index == -1:
            self.input_widget._original_text = self.input_widget.text
        previous = self._history.get_previous(prefix=event.prefix)
        if previous is not None:
            self._load_history_entry(previous)

    def on_chat_text_area_history_next(self, event: ChatTextArea.HistoryNext) -> None:
        """Handle history next."""
        if not self._history or not self.input_widget:
            return
        next_entry = self._history.get_next(prefix=event.prefix)
        if next_entry is not None:
            self._load_history_entry(next_entry)

    def on_chat_text_area_history_reset(self, event: ChatTextArea.HistoryReset) -> None:
        """Handle history reset."""
        if self._history:
            self._history.reset_navigation()
        if self.input_widget:
            self.input_widget._original_text = ""

    def _load_history_entry(self, text: str) -> None:
        """Load a history entry into input."""
        if not self.input_widget:
            return
        self.input_widget._navigating_history = True
        # Parse mode
        if text.startswith("!"):
            self.input_widget.set_mode("!")
            self.input_widget.load_text(text[1:])
        elif text.startswith("/"):
            self.input_widget.set_mode("/")
            self.input_widget.load_text(text[1:])
        else:
            self.input_widget.set_mode(">")
            self.input_widget.load_text(text)
        self._update_prompt()

    def set_completion_reset_callback(self, callback: Callable[[], None]) -> None:
        """Set callback for completion reset."""
        self._completion_reset = callback

    def replace_input(self, text: str, cursor_offset: int | None = None) -> None:
        """Replace input text with completion."""
        if not self.input_widget:
            return
        self.input_widget.load_text(text)
        self.input_widget.reset_history_state()
        self._update_prompt()
        if cursor_offset is not None:
            self.input_widget.set_cursor_offset(cursor_offset)
