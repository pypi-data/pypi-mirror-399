"""Miu Code TUI Application - Vibe Inspired."""

import asyncio
import os
from pathlib import Path
from typing import Any, ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Static

from miu_code.agent.coding import CodingAgent
from miu_code.tui.widgets.approval import ApprovalApp
from miu_code.tui.widgets.banner import WelcomeBanner
from miu_code.tui.widgets.chat import ChatLog
from miu_code.tui.widgets.chat_input import ChatInputContainer
from miu_code.tui.widgets.loading import LoadingSpinner
from miu_code.tui.widgets.messages import BashOutputMessage
from miu_core.models import (
    MessageStopEvent,
    TextDeltaEvent,
    ToolExecutingEvent,
    ToolResultEvent,
)
from miu_core.modes import ModeManager
from miu_core.paths import MiuPaths
from miu_core.usage import UsageTracker

# Version for display
__version__ = "0.2.0"


class MiuCodeApp(App[None]):
    """Miu Code Terminal User Interface with Vibe-inspired design."""

    CSS_PATH = "app.tcss"
    TITLE = "miu"
    SUB_TITLE = ""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+n", "new_session", "New"),
        Binding("ctrl+l", "clear_chat", "Clear"),
        Binding("escape", "interrupt", "Interrupt", show=False, priority=True),
        Binding("shift+tab", "cycle_mode", "Cycle Mode", show=False, priority=True),
        Binding("shift+up", "scroll_chat_up", "Scroll Up", show=False, priority=True),
        Binding("shift+down", "scroll_chat_down", "Scroll Down", show=False, priority=True),
    ]

    def __init__(
        self,
        model: str = "anthropic:claude-sonnet-4-20250514",
        session_id: str | None = None,
    ) -> None:
        super().__init__()
        self.model = model
        self.session_id = session_id
        self._agent: CodingAgent | None = None
        self._is_processing = False
        self._interrupt_requested = False
        self._agent_task: asyncio.Task[None] | None = None

        # State managers
        self._mode_manager = ModeManager()
        self._usage_tracker = UsageTracker()
        self._working_dir = os.getcwd()

        # Auto-scroll state
        self._auto_scroll = True

        # Approval state
        self._pending_approval: asyncio.Future[tuple[bool, str | None]] | None = None
        self._current_bottom_app: str = "input"  # "input" or "approval"
        self._tools_always_approved: set[str] = set()

    def _format_path(self, path: str) -> str:
        """Format path for display (shorten home dir)."""
        home = os.path.expanduser("~")
        if path.startswith(home):
            return "~" + path[len(home) :]
        return path

    def _is_scrolled_to_bottom(self, scroll_view: VerticalScroll) -> bool:
        """Check if scroll view is at bottom (with threshold)."""
        try:
            threshold = 3
            return scroll_view.scroll_y >= (scroll_view.max_scroll_y - threshold)
        except Exception:
            return True

    def _scroll_to_bottom(self) -> None:
        """Scroll chat to bottom."""
        try:
            chat = self.query_one("#chat", VerticalScroll)
            chat.scroll_end(animate=False)
        except Exception:
            pass

    def _scroll_to_bottom_deferred(self) -> None:
        """Schedule scroll to bottom after refresh."""
        self.call_after_refresh(self._scroll_to_bottom)

    def _anchor_if_scrollable(self) -> None:
        """Anchor chat to bottom if auto-scroll is enabled."""
        if not self._auto_scroll:
            return
        try:
            chat = self.query_one("#chat", VerticalScroll)
            if chat.max_scroll_y == 0:
                return
            chat.anchor()
        except Exception:
            pass

    def action_scroll_chat_up(self) -> None:
        """Scroll chat up and disable auto-scroll."""
        try:
            chat = self.query_one("#chat", VerticalScroll)
            chat.scroll_relative(y=-5, animate=False)
            self._auto_scroll = False
        except Exception:
            pass

    def action_scroll_chat_down(self) -> None:
        """Scroll chat down, re-enable auto-scroll if at bottom."""
        try:
            chat = self.query_one("#chat", VerticalScroll)
            chat.scroll_relative(y=5, animate=False)
            if self._is_scrolled_to_bottom(chat):
                self._auto_scroll = True
        except Exception:
            pass

    def compose(self) -> ComposeResult:
        """Create child widgets - Vibe-inspired layout."""
        # Get short model name for display
        model_short = self.model.split(":")[-1] if ":" in self.model else self.model

        # Chat area (scrollable) - contains banner and messages
        with VerticalScroll(id="chat"):
            # Banner at top (scrolls with content)
            yield WelcomeBanner(
                version=__version__,
                model=model_short,
                mcp_count=0,
                working_dir=self._working_dir,
                compact=True,
                id="banner",
            )
            yield ChatLog(id="messages", scroll_callback=self._scroll_to_bottom_deferred)

        # Loading area: loading content (left) + mode indicator (right)
        with Horizontal(id="loading-area"):
            yield LoadingSpinner(id="loading-area-content")
            mode_text = f"{self._mode_manager.label} (shift+tab to cycle)"
            yield Static(mode_text, id="mode-indicator")

        # Bottom app container (for input/approval switching)
        with Static(id="bottom-app-container"):
            yield ChatInputContainer(
                history_file=self._get_history_file(),
                id="input-container",
            )

        # Bottom bar: path left, spacer, tokens right
        with Horizontal(id="bottom-bar"):
            yield Static(self._format_path(self._working_dir), id="path-display")
            yield Static("", id="spacer")
            yield Static(self._usage_tracker.format_usage(), id="token-display")

    def on_mount(self) -> None:
        """Initialize agent on mount."""
        self._init_agent()
        self.query_one("#input-container", ChatInputContainer).focus_input()

    def _get_history_file(self) -> Path:
        """Get history file path."""
        paths = MiuPaths.get()
        paths.ensure_dir(paths.code)
        return paths.history

    def _init_agent(self) -> None:
        """Initialize the coding agent."""
        self._agent = CodingAgent(
            model=self.model,
            working_dir=self._working_dir,
            session_id=self.session_id,
        )
        # Reset usage on new agent
        self._usage_tracker.reset()
        self._update_status_usage()

    def _update_status_usage(self) -> None:
        """Update token display in bottom bar."""
        token_display = self.query_one("#token-display", Static)
        token_display.update(self._usage_tracker.format_usage())

    def _update_mode_indicator(self) -> None:
        """Update mode indicator and input border in bottom bar."""
        mode_indicator = self.query_one("#mode-indicator", Static)
        mode_text = f"{self._mode_manager.label} (shift+tab to cycle)"
        mode_indicator.update(mode_text)

        # Update input border color based on mode
        try:
            input_container = self.query_one("#input-container", ChatInputContainer)
            mode = self._mode_manager.mode

            if mode.name == "ASK":
                input_container.set_border_style("border-safe")
            elif mode.name == "NORMAL":
                input_container.set_border_style("")
            elif mode.name == "PLAN":
                input_container.set_border_style("border-warning")
        except Exception:
            pass  # Container might not exist during approval

    async def _show_approval_dialog(
        self,
        tool_name: str,
        tool_args: dict[str, Any],
    ) -> tuple[bool, str | None]:
        """Show approval dialog and wait for response."""
        # Check if always approved
        if tool_name in self._tools_always_approved:
            return (True, None)

        # Create future for response
        self._pending_approval = asyncio.get_event_loop().create_future()

        # Switch to approval app
        await self._switch_to_approval_app(tool_name, tool_args)

        # Wait for response
        try:
            result = await self._pending_approval
            return result
        finally:
            self._pending_approval = None

    async def _switch_to_approval_app(self, tool_name: str, tool_args: dict[str, Any]) -> None:
        """Switch bottom area to approval dialog."""
        bottom_container = self.query_one("#bottom-app-container", Static)

        # Remove existing widgets
        for child in list(bottom_container.children):
            await child.remove()

        # Mount approval app
        approval_app = ApprovalApp(
            tool_name=tool_name,
            tool_args=tool_args,
            workdir=self._working_dir,
        )
        await bottom_container.mount(approval_app)
        self._current_bottom_app = "approval"
        self.call_after_refresh(approval_app.focus)
        self._scroll_to_bottom()

    async def _switch_to_input_app(self) -> None:
        """Switch bottom area back to input."""
        bottom_container = self.query_one("#bottom-app-container", Static)

        # Remove existing widgets
        for child in list(bottom_container.children):
            await child.remove()

        # Mount input container
        input_container = ChatInputContainer(
            history_file=self._get_history_file(),
            id="input-container",
        )
        await bottom_container.mount(input_container)
        self._current_bottom_app = "input"
        input_container.focus_input()

    def _needs_approval(self, tool_name: str) -> bool:
        """Check if tool needs approval based on current mode."""
        # If already approved for session, skip
        if tool_name in self._tools_always_approved:
            return False

        # In ASK mode, all tools need approval
        if self._mode_manager.mode.name == "ASK":
            return True

        # Some tools always need approval in NORMAL mode
        dangerous_tools = {"bash", "write", "edit", "delete"}
        return tool_name.lower() in dangerous_tools

    async def on_approval_app_approval_granted(self, event: ApprovalApp.ApprovalGranted) -> None:
        """Handle approval granted."""
        if self._pending_approval and not self._pending_approval.done():
            self._pending_approval.set_result((True, None))
        await self._switch_to_input_app()

    async def on_approval_app_approval_granted_always(
        self, event: ApprovalApp.ApprovalGrantedAlways
    ) -> None:
        """Handle approval with always allow."""
        self._tools_always_approved.add(event.tool_name)
        if self._pending_approval and not self._pending_approval.done():
            self._pending_approval.set_result((True, None))
        await self._switch_to_input_app()

    async def on_approval_app_approval_rejected(self, event: ApprovalApp.ApprovalRejected) -> None:
        """Handle approval rejected."""
        if self._pending_approval and not self._pending_approval.done():
            self._pending_approval.set_result((False, "User rejected tool execution"))
        await self._switch_to_input_app()

    async def on_chat_input_container_submitted(self, event: ChatInputContainer.Submitted) -> None:
        """Handle input submission."""
        value = event.value.strip()
        if not value:
            return

        # Clear input immediately (like mistral-vibe)
        input_container = self.query_one("#input-container", ChatInputContainer)
        input_container.clear_input()

        # If agent is running, interrupt it first
        if self._is_processing:
            await self._interrupt_agent()

        # Handle ! prefix for bash
        if value.startswith("!"):
            await self._handle_bash_command(value[1:])
            return

        # Handle / prefix for commands (future)
        if value.startswith("/"):
            await self._handle_command(value)
            return

        # Regular message - run in worker for responsive UI
        self.run_worker(self._handle_user_message(value), exclusive=False)

    async def _handle_bash_command(self, command: str) -> None:
        """Execute bash command and display result."""
        import subprocess

        if not command:
            return

        chat = self.query_one("#messages", ChatLog)

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=False,
                timeout=30,
                cwd=self._working_dir,
            )
            stdout = result.stdout.decode("utf-8", errors="replace") if result.stdout else ""
            stderr = result.stderr.decode("utf-8", errors="replace") if result.stderr else ""
            output = stdout or stderr or "(no output)"

            bash_msg = BashOutputMessage(
                command=command,
                cwd=self._working_dir,
                output=output.strip(),
                exit_code=result.returncode,
            )
            chat.mount(bash_msg)
            self._scroll_to_bottom_deferred()

        except subprocess.TimeoutExpired:
            chat.add_error(f"Command timed out: {command}")
        except Exception as e:
            chat.add_error(f"Command failed: {e}")

    async def _handle_command(self, command: str) -> None:
        """Handle slash commands."""
        chat = self.query_one("#messages", ChatLog)
        chat.add_system_message(f"Command not implemented: {command}")

    async def _handle_user_message(self, query: str) -> None:
        """Handle regular user message with streaming."""
        chat = self.query_one("#messages", ChatLog)

        # Check if at bottom before adding message
        chat_scroll = self.query_one("#chat", VerticalScroll)
        if self._is_scrolled_to_bottom(chat_scroll):
            self._auto_scroll = True

        chat.add_user_message(query)

        # Scroll after user message
        self._scroll_to_bottom_deferred()
        self.call_after_refresh(self._anchor_if_scrollable)

        if not self._agent:
            chat.add_error("Agent not initialized")
            return

        # Start loading animation
        loading = self.query_one("#loading-area-content", LoadingSpinner)
        loading.start()
        self._is_processing = True
        self._interrupt_requested = False

        try:
            # Use streaming for real-time response
            await chat.start_streaming()
            chat_scroll = self.query_one("#chat", VerticalScroll)

            # Check if at bottom before streaming starts - enable auto-scroll
            if self._is_scrolled_to_bottom(chat_scroll):
                self._auto_scroll = True

            async for stream_event in self._agent.run_stream(query):
                # Check for interrupt
                if self._interrupt_requested:
                    break

                if isinstance(stream_event, TextDeltaEvent):
                    await chat.append_streaming(stream_event.text)
                elif isinstance(stream_event, ToolExecutingEvent):
                    chat.add_tool_call(stream_event.tool_name)
                elif isinstance(stream_event, ToolResultEvent):
                    chat.add_tool_result(stream_event.output, stream_event.success)
                elif isinstance(stream_event, MessageStopEvent):
                    # Update usage from stop event
                    if stream_event.usage:
                        self._usage_tracker.add_usage(
                            input_tokens=stream_event.usage.get("input_tokens", 0),
                            output_tokens=stream_event.usage.get("output_tokens", 0),
                        )
                        self._update_status_usage()

                # Schedule scroll after layout refresh (like mistral-vibe)
                if self._auto_scroll:
                    self.call_after_refresh(self._anchor_if_scrollable)

            await chat.end_streaming()

            if self._interrupt_requested:
                chat.add_system_message("Interrupted")

        except asyncio.CancelledError:
            await chat.end_streaming()
            chat.add_system_message("Interrupted")
        except Exception as e:
            await chat.end_streaming()
            chat.add_error(str(e))
        finally:
            # Stop loading animation
            loading.stop()
            self._is_processing = False
            self._interrupt_requested = False
            self._agent_task = None
            # Focus input after completion
            try:
                input_container = self.query_one("#input-container", ChatInputContainer)
                input_container.focus_input()
            except Exception:
                pass

    async def _interrupt_agent(self) -> None:
        """Interrupt the running agent."""
        if not self._is_processing or self._interrupt_requested:
            return

        self._interrupt_requested = True

        # Cancel the task if it exists
        if self._agent_task and not self._agent_task.done():
            self._agent_task.cancel()
            try:
                await self._agent_task
            except asyncio.CancelledError:
                pass

    def action_interrupt(self) -> None:
        """Handle escape key - interrupt agent or focus input."""
        if self._is_processing:
            self.run_worker(self._interrupt_agent(), exclusive=False)
        else:
            # Focus input if not processing
            try:
                input_container = self.query_one("#input-container", ChatInputContainer)
                input_container.focus_input()
            except Exception:
                pass
        self._scroll_to_bottom()

    def action_cycle_mode(self) -> None:
        """Cycle through agent modes."""
        self._mode_manager.cycle()
        self._update_mode_indicator()
        chat = self.query_one("#messages", ChatLog)
        chat.add_system_message(f"Switched to {self._mode_manager.label}")

    def action_new_session(self) -> None:
        """Start a new session."""
        self.session_id = None
        self._init_agent()
        chat = self.query_one("#messages", ChatLog)
        chat.clear()
        chat.add_system_message("Started new session")

    def action_clear_chat(self) -> None:
        """Clear the chat log."""
        chat = self.query_one("#messages", ChatLog)
        chat.clear()


def run(model: str = "anthropic:claude-sonnet-4-20250514") -> None:
    """Run the TUI application."""
    app = MiuCodeApp(model=model)
    app.run()


if __name__ == "__main__":
    run()
