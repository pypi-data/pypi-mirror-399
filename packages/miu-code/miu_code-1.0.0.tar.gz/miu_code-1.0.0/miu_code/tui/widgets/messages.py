"""Message widgets for chat display."""

from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Markdown, Static
from textual.widgets._markdown import MarkdownStream

from miu_code.tui.widgets.spinner import SpinnerMixin, SpinnerType


class NonSelectableStatic(Static):
    """Static that doesn't participate in text selection."""

    @property
    def text_selection(self) -> None:
        return None

    @text_selection.setter
    def text_selection(self, value: Any) -> None:
        pass


class ExpandingBorder(NonSelectableStatic):
    """Vertical border that expands with content height."""

    def render(self) -> str:
        height = self.size.height
        if height <= 1:
            return "⎣"
        return "\n".join(["⎢"] * (height - 1) + ["⎣"])

    def on_resize(self) -> None:
        self.refresh()


class UserMessage(Static):
    """User message display widget."""

    DEFAULT_CSS = """
    UserMessage {
        width: 100%;
        height: auto;
        margin-top: 1;
        padding: 1 0;
        background: $surface;
    }
    UserMessage .user-message-container {
        width: 100%;
        height: auto;
    }
    UserMessage .user-message-prompt {
        width: auto;
        height: auto;
        color: $primary;
        text-style: bold;
    }
    UserMessage .user-message-content {
        width: 1fr;
        height: auto;
        color: $text;
        text-style: bold;
    }
    """

    def __init__(self, content: str, pending: bool = False) -> None:
        super().__init__()
        self._content = content
        self._pending = pending
        if pending:
            self.add_class("pending")

    def compose(self) -> ComposeResult:
        with Horizontal(classes="user-message-container"):
            yield NonSelectableStatic("> ", classes="user-message-prompt")
            yield Static(self._content, markup=False, classes="user-message-content")

    def on_resize(self) -> None:
        """Refresh on resize to ensure proper layout."""
        self.refresh()


class AssistantMessage(Static):
    """Assistant message with streaming markdown support."""

    DEFAULT_CSS = """
    AssistantMessage {
        width: 100%;
        height: auto;
        margin-top: 1;
    }
    AssistantMessage .assistant-message-container {
        width: 100%;
        height: auto;
        align: left top;
    }
    AssistantMessage .assistant-message-dot {
        width: auto;
        height: auto;
        color: $text;
    }
    AssistantMessage .assistant-message-content {
        width: 1fr;
        height: auto;
        padding: 0;
    }
    AssistantMessage .assistant-message-content Markdown {
        width: 100%;
        height: auto;
        padding: 0;
        margin: 0;
    }
    """

    def __init__(self, content: str = "") -> None:
        super().__init__()
        self._content = content
        self._markdown: Markdown | None = None
        self._stream: MarkdownStream | None = None

    def compose(self) -> ComposeResult:
        with Horizontal(classes="assistant-message-container"):
            yield NonSelectableStatic("● ", classes="assistant-message-dot")
            with Vertical(classes="assistant-message-content"):
                self._markdown = Markdown("")
                yield self._markdown

    def on_resize(self) -> None:
        """Refresh on resize to ensure proper layout."""
        self.refresh()

    def _ensure_stream(self) -> MarkdownStream | None:
        """Get or create markdown stream."""
        if self._stream is None and self._markdown:
            self._stream = Markdown.get_stream(self._markdown)
        return self._stream

    async def append_content(self, content: str) -> None:
        """Append content to streaming message."""
        if not content:
            return
        self._content += content
        stream = self._ensure_stream()
        if stream:
            await stream.write(content)

    async def stop_stream(self) -> None:
        """Stop streaming."""
        if self._stream:
            await self._stream.stop()
            self._stream = None


class ReasoningMessage(SpinnerMixin, Static):
    """Collapsible reasoning/thinking message."""

    SPINNER_TYPE = SpinnerType.LINE
    SPINNING_TEXT = "Thinking"
    COMPLETED_TEXT = "Thought"

    DEFAULT_CSS = """
    ReasoningMessage {
        width: 100%;
        height: auto;
        margin-top: 1;
    }
    ReasoningMessage .reasoning-header {
        width: 100%;
        height: auto;
    }
    ReasoningMessage .reasoning-indicator {
        width: auto;
        height: auto;
        color: $text-muted;
        margin-right: 1;
    }
    ReasoningMessage .reasoning-indicator.success {
        color: $success;
    }
    ReasoningMessage .reasoning-text {
        width: auto;
        height: auto;
        color: $text-muted;
        text-style: italic;
    }
    ReasoningMessage .reasoning-triangle {
        width: auto;
        height: auto;
        color: $text-muted;
        margin-left: 1;
    }
    ReasoningMessage .reasoning-content {
        width: 100%;
        height: auto;
        padding-left: 2;
        color: $text-muted;
        text-style: italic;
    }
    """

    def __init__(self, content: str = "", collapsed: bool = True) -> None:
        super().__init__()
        self._content = content
        self.collapsed = collapsed
        self._markdown: Markdown | None = None
        self._stream: MarkdownStream | None = None
        self._triangle_widget: Static | None = None
        self._status_text_widget: Static | None = None
        self.init_spinner()

    def compose(self) -> ComposeResult:
        with Vertical(classes="reasoning-wrapper"):
            with Horizontal(classes="reasoning-header"):
                self._indicator_widget = NonSelectableStatic(
                    self._spinner.current_frame(), classes="reasoning-indicator"
                )
                yield self._indicator_widget
                self._status_text_widget = Static(
                    self.SPINNING_TEXT, markup=False, classes="reasoning-text"
                )
                yield self._status_text_widget
                self._triangle_widget = NonSelectableStatic(
                    "▶" if self.collapsed else "▼", classes="reasoning-triangle"
                )
                yield self._triangle_widget
            self._markdown = Markdown("", classes="reasoning-content")
            self._markdown.display = not self.collapsed
            yield self._markdown

    def on_mount(self) -> None:
        self.start_spinner_timer()

    def on_resize(self) -> None:
        """Refresh on resize to ensure proper layout."""
        self.refresh_spinner()

    async def on_click(self) -> None:
        """Toggle collapsed state on click."""
        await self.set_collapsed(not self.collapsed)

    async def set_collapsed(self, collapsed: bool) -> None:
        """Set collapsed state."""
        if self.collapsed == collapsed:
            return
        self.collapsed = collapsed
        if self._triangle_widget:
            self._triangle_widget.update("▶" if collapsed else "▼")
        if self._markdown:
            self._markdown.display = not collapsed
            if not collapsed and self._content:
                # Re-render content when expanding
                if self._stream:
                    await self._stream.stop()
                    self._stream = None
                await self._markdown.update("")
                stream = self._ensure_stream()
                if stream:
                    await stream.write(self._content)

    def _ensure_stream(self) -> MarkdownStream | None:
        if self._stream is None and self._markdown:
            self._stream = Markdown.get_stream(self._markdown)
        return self._stream

    async def append_content(self, content: str) -> None:
        """Append content."""
        self._content += content
        if not self.collapsed:
            stream = self._ensure_stream()
            if stream:
                await stream.write(content)

    async def stop_stream(self) -> None:
        """Stop streaming and show completed."""
        if self._stream:
            await self._stream.stop()
            self._stream = None
        self.stop_spinner()
        if self._status_text_widget:
            self._status_text_widget.update(self.COMPLETED_TEXT)


class BashOutputMessage(Static):
    """Styled bash command output display."""

    DEFAULT_CSS = """
    BashOutputMessage {
        width: 100%;
        height: auto;
        margin-top: 1;
    }
    BashOutputMessage .bash-container {
        width: 100%;
        height: auto;
        padding: 1 2;
        background: $surface;
    }
    BashOutputMessage .bash-cwd-line {
        width: 100%;
        height: auto;
        margin-bottom: 1;
    }
    BashOutputMessage .bash-cwd {
        width: auto;
        color: $text-muted;
    }
    BashOutputMessage .bash-exit-success {
        width: auto;
        color: $success;
    }
    BashOutputMessage .bash-exit-failure {
        width: auto;
        color: $error;
    }
    BashOutputMessage .bash-exit-code {
        width: auto;
        color: $text-muted;
    }
    BashOutputMessage .bash-command-line {
        width: 100%;
        height: auto;
        margin-bottom: 1;
    }
    BashOutputMessage .bash-chevron {
        width: auto;
        color: $primary;
        text-style: bold;
    }
    BashOutputMessage .bash-command {
        width: auto;
        color: $text;
    }
    BashOutputMessage .bash-output {
        width: 100%;
        color: $text;
    }
    """

    def __init__(self, command: str, cwd: str, output: str, exit_code: int) -> None:
        super().__init__()
        self._command = command
        self._cwd = cwd
        self._output = output
        self._exit_code = exit_code

    def compose(self) -> ComposeResult:
        with Vertical(classes="bash-container"):
            # CWD line with exit status
            with Horizontal(classes="bash-cwd-line"):
                yield Static(self._cwd, markup=False, classes="bash-cwd")
                yield Static("", classes="spacer")
                if self._exit_code == 0:
                    yield Static("✓", classes="bash-exit-success")
                else:
                    yield Static("✗", classes="bash-exit-failure")
                    yield Static(f" ({self._exit_code})", classes="bash-exit-code")
            # Command line
            with Horizontal(classes="bash-command-line"):
                yield Static("> ", classes="bash-chevron")
                yield Static(self._command, markup=False, classes="bash-command")
            # Output
            yield Static(self._output, markup=False, classes="bash-output")


class ErrorMessage(Static):
    """Error message display."""

    DEFAULT_CSS = """
    ErrorMessage {
        width: 100%;
        height: auto;
    }
    ErrorMessage .error-container {
        width: 100%;
        height: auto;
    }
    ErrorMessage .error-border {
        width: auto;
        height: 100%;
        padding: 0 1 0 2;
        color: $text-muted;
    }
    ErrorMessage .error-content {
        width: 1fr;
        height: auto;
        color: $error;
        text-style: bold;
    }
    """

    def __init__(self, error: str, collapsed: bool = True) -> None:
        super().__init__()
        self._error = error
        self.collapsed = collapsed
        self._content_widget: Static | None = None

    def compose(self) -> ComposeResult:
        with Horizontal(classes="error-container"):
            yield ExpandingBorder(classes="error-border")
            self._content_widget = Static(self._get_text(), markup=False, classes="error-content")
            yield self._content_widget

    def _get_text(self) -> str:
        if self.collapsed:
            return "Error. (ctrl+o to expand)"
        return f"Error: {self._error}"

    def set_collapsed(self, collapsed: bool) -> None:
        if self.collapsed == collapsed:
            return
        self.collapsed = collapsed
        if self._content_widget:
            self._content_widget.update(self._get_text())


class SystemMessage(Static):
    """System message display."""

    DEFAULT_CSS = """
    SystemMessage {
        width: 100%;
        height: auto;
    }
    SystemMessage .system-container {
        width: 100%;
        height: auto;
    }
    SystemMessage .system-border {
        width: auto;
        height: 100%;
        padding: 0 1 0 2;
        color: $text-muted;
    }
    SystemMessage .system-content {
        width: 1fr;
        height: auto;
        color: $text-muted;
    }
    """

    def __init__(self, message: str) -> None:
        super().__init__()
        self._message = message

    def compose(self) -> ComposeResult:
        with Horizontal(classes="system-container"):
            yield ExpandingBorder(classes="system-border")
            yield Static(self._message, markup=False, classes="system-content")
