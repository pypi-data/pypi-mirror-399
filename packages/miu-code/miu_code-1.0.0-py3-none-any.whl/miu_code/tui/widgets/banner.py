"""Welcome banner widget."""

import os
from typing import Any

from rich.console import RenderableType
from rich.text import Text
from textual.widget import Widget

from miu_code.tui.theme import MIU_COLORS, VIBE_COLORS

# ASCII art logo for miu - compact version
MIU_LOGO_COMPACT = [
    "  _ __ ___ (_)_   _",
    " | '_ ` _ \\| | | | |",
    " | | | | | | | |_| |",
    " |_| |_| |_|_|\\__,_|",
]


class WelcomeBanner(Widget):
    """Welcome banner with logo and metadata."""

    DEFAULT_CSS = """
    WelcomeBanner {
        height: 7;
        width: 100%;
        padding: 0 1;
        margin-bottom: 1;
    }
    """

    # For test compatibility
    animation_progress = 0.0
    _animation_complete = True
    _lines = MIU_LOGO_COMPACT
    _compact = True

    def __init__(
        self,
        version: str = "",
        model: str = "",
        mcp_count: int = 0,
        working_dir: str = "",
        compact: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.version = version
        self.model = model
        self.mcp_count = mcp_count
        self.working_dir = working_dir or os.getcwd()
        self._compact = compact
        self._lines = MIU_LOGO_COMPACT

    def _format_path(self, path: str) -> str:
        """Shorten path with ~ for home dir."""
        home = os.path.expanduser("~")
        if path.startswith(home):
            return "~" + path[len(home) :]
        return path

    def on_resize(self) -> None:
        """Refresh on resize to ensure proper layout."""
        self.refresh()

    def render(self) -> RenderableType:
        """Render the banner as a single Text object."""
        # Build info lines for side panel
        info_lines = []
        if self.version:
            info_lines.append(f"Miu Code v{self.version}")
        if self.model:
            mcp_str = f" | {self.mcp_count} MCP" if self.mcp_count > 0 else ""
            info_lines.append(f"{self.model}{mcp_str}")
        if self.working_dir:
            info_lines.append(self._format_path(self.working_dir))

        # Build full text
        result = Text()
        primary = MIU_COLORS["primary"]
        info_color = VIBE_COLORS["orange_gold"]

        # Logo lines with side info
        for line_idx, logo_line in enumerate(self._lines):
            if line_idx > 0:
                result.append("\n")
            result.append(logo_line, style=f"bold {primary}")
            if self._compact and line_idx < len(info_lines):
                result.append("    ", style="")
                result.append(info_lines[line_idx], style=f"dim {info_color}")

        # Empty line
        result.append("\n")

        # Help hint
        result.append("\n  Type /help for commands", style="dim white")
        result.append("  |  ", style="dim white")
        result.append("/model to switch", style="dim white")

        # Separator
        result.append("\n  " + "─" * 60, style=f"dim {info_color}")

        return result
