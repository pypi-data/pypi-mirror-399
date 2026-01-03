"""Tool call and result widgets."""

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static

from miu_code.tui.widgets.messages import ExpandingBorder


class ToolCallMessage(Static):
    """Tool call indicator."""

    DEFAULT_CSS = """
    ToolCallMessage {
        width: 100%;
        height: auto;
        margin-top: 1;
    }
    ToolCallMessage .tool-call-container {
        width: 100%;
        height: auto;
    }
    ToolCallMessage .tool-call-icon {
        width: auto;
        color: $warning;
        margin-right: 1;
    }
    ToolCallMessage .tool-call-text {
        width: auto;
        color: $text;
    }
    ToolCallMessage .tool-call-name {
        width: auto;
        color: $primary;
        text-style: bold;
    }
    """

    def __init__(self, tool_name: str, args: str = "") -> None:
        super().__init__()
        self._tool_name = tool_name
        self._args = args

    def compose(self) -> ComposeResult:
        with Horizontal(classes="tool-call-container"):
            yield Static("⚡", classes="tool-call-icon")
            yield Static("Calling: ", classes="tool-call-text")
            yield Static(self._tool_name, classes="tool-call-name")
            if self._args:
                yield Static(f" {self._args}", classes="tool-call-text")


class ToolResultMessage(Static):
    """Tool result display."""

    DEFAULT_CSS = """
    ToolResultMessage {
        width: 100%;
        height: auto;
    }
    ToolResultMessage .tool-result-container {
        width: 100%;
        height: auto;
    }
    ToolResultMessage .tool-result-border {
        width: auto;
        height: 100%;
        padding: 0 1 0 2;
        color: $text-muted;
    }
    ToolResultMessage .tool-result-content {
        width: 1fr;
        height: auto;
        color: $text;
    }
    ToolResultMessage .tool-result-content.error {
        color: $error;
    }
    ToolResultMessage .tool-result-content.success {
        color: $success;
    }
    """

    def __init__(self, result: str, success: bool = True, collapsed: bool = True) -> None:
        super().__init__()
        self._result = result
        self._success = success
        self.collapsed = collapsed

    def compose(self) -> ComposeResult:
        with Horizontal(classes="tool-result-container"):
            yield ExpandingBorder(classes="tool-result-border")
            status_class = "success" if self._success else "error"
            icon = "✓" if self._success else "✗"
            display_text = self._get_display_text()
            yield Static(
                f"{icon} {display_text}",
                markup=False,
                classes=f"tool-result-content {status_class}",
            )

    def _get_display_text(self) -> str:
        if self.collapsed:
            return self._result[:100] + "..." if len(self._result) > 100 else self._result
        return self._result
