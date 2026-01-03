"""Tool approval dialog widget."""

from typing import Any, ClassVar

from textual import events
from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Container, Vertical, VerticalScroll
from textual.message import Message
from textual.widgets import Static


class ApprovalApp(Container):
    """Tool approval dialog with yes/no/always options."""

    can_focus = True
    can_focus_children = False

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("up", "move_up", "Up", show=False),
        Binding("down", "move_down", "Down", show=False),
        Binding("enter", "select", "Select", show=False),
        Binding("1", "select_yes", "Yes", show=False),
        Binding("y", "select_yes", "Yes", show=False),
        Binding("2", "select_always", "Always Session", show=False),
        Binding("3", "select_no", "No", show=False),
        Binding("n", "select_no", "No", show=False),
    ]

    class ApprovalGranted(Message):
        """User approved tool execution."""

        def __init__(self, tool_name: str, tool_args: dict[str, Any]) -> None:
            super().__init__()
            self.tool_name = tool_name
            self.tool_args = tool_args

    class ApprovalGrantedAlways(Message):
        """User approved and wants to always allow this tool."""

        def __init__(
            self,
            tool_name: str,
            tool_args: dict[str, Any],
            save_permanently: bool = False,
        ) -> None:
            super().__init__()
            self.tool_name = tool_name
            self.tool_args = tool_args
            self.save_permanently = save_permanently

    class ApprovalRejected(Message):
        """User rejected tool execution."""

        def __init__(self, tool_name: str, tool_args: dict[str, Any]) -> None:
            super().__init__()
            self.tool_name = tool_name
            self.tool_args = tool_args

    DEFAULT_CSS = """
    ApprovalApp {
        width: 100%;
        height: auto;
        max-height: 16;
        background: $surface;
        border: round #666666;
        padding: 0 1;
        margin: 0 0 1 0;
    }
    ApprovalApp #approval-content {
        width: 100%;
        height: auto;
    }
    ApprovalApp .approval-title {
        height: auto;
        text-style: bold;
        color: #F39C12;
    }
    ApprovalApp .approval-tool-scroll {
        width: 100%;
        height: auto;
        max-height: 6;
    }
    ApprovalApp .approval-tool-info {
        width: 100%;
        height: auto;
        color: $text-muted;
    }
    ApprovalApp .approval-option {
        height: auto;
        color: $text;
    }
    ApprovalApp .approval-cursor-selected.option-yes {
        color: #27AE60;
        text-style: bold;
    }
    ApprovalApp .approval-cursor-selected.option-no {
        color: #E74C3C;
        text-style: bold;
    }
    ApprovalApp .approval-help {
        height: auto;
        color: $text-muted;
    }
    """

    def __init__(
        self,
        tool_name: str,
        tool_args: dict[str, Any],
        workdir: str,
    ) -> None:
        super().__init__(id="approval-app")
        self.tool_name = tool_name
        self.tool_args = tool_args
        self.workdir = workdir
        self.selected_option = 0
        self.option_widgets: list[Static] = []
        self.title_widget: Static | None = None
        self.help_widget: Static | None = None

    def compose(self) -> ComposeResult:
        with Vertical(id="approval-content"):
            # Title
            self.title_widget = Static(
                f"⚠ {self.tool_name} requires approval", classes="approval-title"
            )
            yield self.title_widget

            # Tool info
            with VerticalScroll(classes="approval-tool-scroll"):
                yield self._create_tool_info()

            yield Static("")

            # Options
            options_text = [
                "1. Yes",
                f"2. Yes and always allow {self.tool_name} for this session",
                "3. No and tell the agent what to do instead",
            ]
            for text in options_text:
                widget = Static(text, classes="approval-option")
                self.option_widgets.append(widget)
                yield widget

            yield Static("")

            # Help
            self.help_widget = Static(
                "↑↓ navigate  Enter select  ESC reject", classes="approval-help"
            )
            yield self.help_widget

    def _create_tool_info(self) -> Static:
        """Create tool info display."""
        info_parts = []
        for key, value in self.tool_args.items():
            value_str = str(value)
            if len(value_str) > 100:
                value_str = value_str[:100] + "..."
            info_parts.append(f"  {key}: {value_str}")

        info_text = "\n".join(info_parts) if info_parts else "  (no arguments)"
        return Static(info_text, classes="approval-tool-info")

    async def on_mount(self) -> None:
        self._update_options()
        self.focus()

    def _update_options(self) -> None:
        """Update option display based on selection."""
        option_types = ["yes", "yes", "no"]

        for idx, widget in enumerate(self.option_widgets):
            is_selected = idx == self.selected_option
            option_type = option_types[idx]

            # Update classes
            widget.remove_class("approval-cursor-selected")
            widget.remove_class("option-yes")
            widget.remove_class("option-no")

            if is_selected:
                widget.add_class("approval-cursor-selected")
                widget.add_class(f"option-{option_type}")

            # Update text with cursor
            base_texts = [
                "1. Yes",
                f"2. Yes and always allow {self.tool_name} for this session",
                "3. No and tell the agent what to do instead",
            ]
            cursor = "> " if is_selected else "  "
            widget.update(f"{cursor}{base_texts[idx]}")

    def action_move_up(self) -> None:
        """Move selection up."""
        self.selected_option = (self.selected_option - 1) % 3
        self._update_options()

    def action_move_down(self) -> None:
        """Move selection down."""
        self.selected_option = (self.selected_option + 1) % 3
        self._update_options()

    def action_select(self) -> None:
        """Select current option."""
        self._handle_selection(self.selected_option)

    def action_select_yes(self) -> None:
        """Select yes."""
        self.selected_option = 0
        self._handle_selection(0)

    def action_select_always(self) -> None:
        """Select always allow."""
        self.selected_option = 1
        self._handle_selection(1)

    def action_select_no(self) -> None:
        """Select no."""
        self.selected_option = 2
        self._handle_selection(2)

    def _handle_selection(self, option: int) -> None:
        """Handle option selection."""
        if option == 0:
            self.post_message(
                self.ApprovalGranted(
                    tool_name=self.tool_name,
                    tool_args=self.tool_args,
                )
            )
        elif option == 1:
            self.post_message(
                self.ApprovalGrantedAlways(
                    tool_name=self.tool_name,
                    tool_args=self.tool_args,
                    save_permanently=False,
                )
            )
        elif option == 2:
            self.post_message(
                self.ApprovalRejected(
                    tool_name=self.tool_name,
                    tool_args=self.tool_args,
                )
            )

    def on_blur(self, event: events.Blur) -> None:
        """Keep focus on approval dialog."""
        self.call_after_refresh(self.focus)
