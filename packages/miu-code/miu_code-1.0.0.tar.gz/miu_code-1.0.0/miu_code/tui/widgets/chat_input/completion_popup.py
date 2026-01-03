"""Auto-completion popup widget."""

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static


class CompletionPopup(Static):
    """Popup displaying completion suggestions."""

    DEFAULT_CSS = """
    CompletionPopup {
        width: 100%;
        height: auto;
        max-height: 8;
        padding: 0 1;
        background: $surface;
        display: none;
    }
    CompletionPopup.visible {
        display: block;
    }
    CompletionPopup .completion-item {
        width: 100%;
        height: auto;
        padding: 0 1;
    }
    CompletionPopup .completion-item.selected {
        background: $primary;
        color: $background;
    }
    CompletionPopup .completion-label {
        width: auto;
        text-style: bold;
    }
    CompletionPopup .completion-desc {
        width: auto;
        color: $text-muted;
        margin-left: 2;
    }
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._suggestions: list[tuple[str, str]] = []
        self._selected_index = 0
        self._container: Vertical | None = None

    def compose(self) -> ComposeResult:
        self._container = Vertical(id="completion-items")
        yield self._container

    def update_suggestions(
        self, suggestions: list[tuple[str, str]], selected_index: int = 0
    ) -> None:
        """Update displayed suggestions."""
        self._suggestions = suggestions
        self._selected_index = selected_index

        if not suggestions:
            self.hide()
            return

        self.show()
        self._render_items()

    def _render_items(self) -> None:
        """Render suggestion items."""
        if not self._container:
            return

        # Clear existing
        self._container.remove_children()

        for i, (label, desc) in enumerate(self._suggestions):
            classes = "completion-item"
            if i == self._selected_index:
                classes += " selected"

            item_text = f"{label}"
            if desc:
                item_text += f"  {desc}"

            item = Static(item_text, classes=classes)
            self._container.mount(item)

    def show(self) -> None:
        """Show popup."""
        self.add_class("visible")

    def hide(self) -> None:
        """Hide popup."""
        self.remove_class("visible")
        self._suggestions = []

    def select_next(self) -> None:
        """Select next item."""
        if self._suggestions:
            self._selected_index = (self._selected_index + 1) % len(self._suggestions)
            self._render_items()

    def select_previous(self) -> None:
        """Select previous item."""
        if self._suggestions:
            self._selected_index = (self._selected_index - 1) % len(self._suggestions)
            self._render_items()

    def get_selected(self) -> tuple[str, str] | None:
        """Get selected suggestion."""
        if self._suggestions and 0 <= self._selected_index < len(self._suggestions):
            return self._suggestions[self._selected_index]
        return None
