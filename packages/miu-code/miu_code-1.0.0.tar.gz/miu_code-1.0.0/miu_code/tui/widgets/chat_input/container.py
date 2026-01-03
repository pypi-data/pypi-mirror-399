"""Chat input container with completion support."""

from pathlib import Path
from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message

from miu_code.tui.widgets.chat_input.body import ChatInputBody
from miu_code.tui.widgets.chat_input.completion_popup import CompletionPopup
from miu_code.tui.widgets.chat_input.text_area import ChatTextArea


class ChatInputContainer(Vertical):
    """Container for chat input with completion popup."""

    class Submitted(Message):
        """Input submitted."""

        def __init__(self, value: str) -> None:
            self.value = value
            super().__init__()

    DEFAULT_CSS = """
    ChatInputContainer {
        height: auto;
        width: 100%;
    }
    """

    def __init__(
        self,
        history_file: Path | None = None,
        border_class: str = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._history_file = history_file
        self._border_class = border_class
        self._completion_popup: CompletionPopup | None = None
        self._body: ChatInputBody | None = None

    def compose(self) -> ComposeResult:
        self._completion_popup = CompletionPopup(id="completion-popup")
        yield self._completion_popup

        classes = "input-box-inner"
        if self._border_class:
            classes += f" {self._border_class}"

        with Vertical(id="input-box", classes=classes):
            self._body = ChatInputBody(history_file=self._history_file, id="input-body")
            yield self._body

    def on_mount(self) -> None:
        if self._body:
            self._body.set_completion_reset_callback(self._reset_completion)
            self._body.focus_input()

    @property
    def input_widget(self) -> ChatTextArea | None:
        """Get underlying text area."""
        return self._body.input_widget if self._body else None

    @property
    def value(self) -> str:
        """Get current input value."""
        return self._body.value if self._body else ""

    @value.setter
    def value(self, text: str) -> None:
        """Set input value."""
        if self._body:
            self._body.value = text

    def focus_input(self) -> None:
        """Focus the input."""
        if self._body:
            self._body.focus_input()

    def clear_input(self) -> None:
        """Clear the input value."""
        if self._body:
            self._body.value = ""

    def on_chat_input_body_submitted(self, event: ChatInputBody.Submitted) -> None:
        """Handle submission from body."""
        event.stop()
        self.post_message(self.Submitted(event.value))

    def _reset_completion(self) -> None:
        """Reset completion state."""
        if self._completion_popup:
            self._completion_popup.hide()

    def show_completions(self, suggestions: list[tuple[str, str]], selected: int = 0) -> None:
        """Show completion suggestions."""
        if self._completion_popup:
            self._completion_popup.update_suggestions(suggestions, selected)

    def hide_completions(self) -> None:
        """Hide completions."""
        if self._completion_popup:
            self._completion_popup.hide()

    def set_border_style(self, style: str) -> None:
        """Set border style class."""
        input_box = self.query_one("#input-box")
        # Remove existing border classes
        for cls in ["border-safe", "border-warning", "border-error"]:
            input_box.remove_class(cls)
        if style:
            input_box.add_class(style)
