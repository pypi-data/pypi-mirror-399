"""Status bar widget for TUI footer."""

import os
from typing import Any

from rich.text import Text
from textual.app import RenderResult
from textual.reactive import reactive
from textual.widget import Widget

from miu_core.modes import AgentMode, ModeManager
from miu_core.usage import UsageTracker


class StatusBar(Widget):
    """Status bar showing mode, path, and token usage.

    Layout:
    ┌────────────────────────────────────────────────────────────────┐
    │  plan mode (shift+tab)  │  ~/git/project  │  4% of 200k tokens │
    └────────────────────────────────────────────────────────────────┘
    """

    DEFAULT_CSS = """
    StatusBar {
        dock: bottom;
        height: 1;
        background: $surface-darken-1;
        padding: 0 1;
    }
    """

    # Reactive properties for updates
    mode_label: reactive[str] = reactive("normal")
    current_path: reactive[str] = reactive("")
    token_usage: reactive[str] = reactive("")

    def __init__(
        self,
        mode_manager: ModeManager | None = None,
        usage_tracker: UsageTracker | None = None,
        working_dir: str = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._mode_manager = mode_manager or ModeManager()
        self._usage_tracker = usage_tracker or UsageTracker()
        self._working_dir = working_dir

        # Set initial values
        self.mode_label = self._mode_manager.format_status()
        self.current_path = self._format_path(working_dir)
        self.token_usage = self._usage_tracker.format_usage()

        # Subscribe to mode changes
        self._mode_manager.on_change(self._on_mode_change)

    def _format_path(self, path: str) -> str:
        """Format path for display (shorten home dir)."""
        home = os.path.expanduser("~")
        if path.startswith(home):
            return "~" + path[len(home) :]
        return path

    def _on_mode_change(self, mode: AgentMode) -> None:
        """Handle mode change event."""
        _ = mode  # Unused but required by callback signature
        self.mode_label = self._mode_manager.format_status()

    def update_usage(self, input_tokens: int = 0, output_tokens: int = 0) -> None:
        """Update token usage display."""
        self._usage_tracker.add_usage(input_tokens=input_tokens, output_tokens=output_tokens)
        self.token_usage = self._usage_tracker.format_usage()

    def update_path(self, path: str) -> None:
        """Update current path display."""
        self._working_dir = path
        self.current_path = self._format_path(path)

    def render(self) -> RenderResult:
        """Render the status bar."""
        # Colors
        miu_primary = "#1ABC9C"
        muted = "dim white"

        text = Text()

        # Left: Mode indicator
        text.append("", style=miu_primary)
        text.append(f" {self.mode_label}", style=muted)

        # Center: Path (calculate spacing)
        total_width = self.size.width if self.size.width > 0 else 80
        left_len = len(f" {self.mode_label}")
        right_len = len(self.token_usage)
        center_space = total_width - left_len - right_len - 4  # padding

        if center_space > len(self.current_path) + 4:
            padding = (center_space - len(self.current_path)) // 2
            text.append(" " * padding)
            text.append(self.current_path, style=muted)
            text.append(" " * (center_space - padding - len(self.current_path)))
        else:
            text.append("  ")

        # Right: Token usage
        text.append(self.token_usage, style=miu_primary)

        return text

    @property
    def mode_manager(self) -> ModeManager:
        """Access mode manager for cycling."""
        return self._mode_manager
