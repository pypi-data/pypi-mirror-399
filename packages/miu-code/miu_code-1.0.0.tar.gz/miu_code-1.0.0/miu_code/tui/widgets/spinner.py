"""Spinner animation mixin for widgets."""

from enum import Enum

from textual.timer import Timer
from textual.widgets import Static


class SpinnerType(Enum):
    """Spinner animation types."""

    LINE = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")
    DOT = ("⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷")
    SIMPLE = ("◐", "◓", "◑", "◒")


class Spinner:
    """Spinner animation state."""

    def __init__(self, spinner_type: SpinnerType = SpinnerType.LINE) -> None:
        self._frames: tuple[str, ...] = spinner_type.value
        self._index = 0

    def current_frame(self) -> str:
        """Get current frame."""
        return str(self._frames[self._index])

    def advance(self) -> str:
        """Advance to next frame and return it."""
        self._index = (self._index + 1) % len(self._frames)
        return str(self._frames[self._index])


class SpinnerMixin:
    """Mixin for widgets that need spinner animation."""

    SPINNER_TYPE: SpinnerType = SpinnerType.LINE
    SPINNING_TEXT: str = "Loading"
    COMPLETED_TEXT: str = "Done"

    _spinner: Spinner
    _spinner_timer: Timer | None
    _spinner_running: bool
    _indicator_widget: Static | None

    def init_spinner(self) -> None:
        """Initialize spinner state. Call in __init__."""
        self._spinner = Spinner(self.SPINNER_TYPE)
        self._spinner_timer = None
        self._spinner_running = False
        self._indicator_widget = None

    def start_spinner_timer(self) -> None:
        """Start spinner animation timer."""
        if hasattr(self, "set_interval"):
            self._spinner_timer = self.set_interval(0.1, self._update_spinner)
            self._spinner_running = True

    def stop_spinner(self) -> None:
        """Stop spinner and show completed state."""
        self._spinner_running = False
        if self._spinner_timer:
            self._spinner_timer.stop()
        if self._indicator_widget:
            self._indicator_widget.update("✓")
            self._indicator_widget.add_class("success")

    def _update_spinner(self) -> None:
        """Update spinner frame."""
        if self._spinner_running and self._indicator_widget:
            self._indicator_widget.update(self._spinner.advance())

    def refresh_spinner(self) -> None:
        """Refresh spinner display."""
        if self._indicator_widget and self._spinner_running:
            self._indicator_widget.update(self._spinner.current_frame())
