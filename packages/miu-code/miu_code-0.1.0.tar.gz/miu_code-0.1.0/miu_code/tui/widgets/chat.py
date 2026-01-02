"""Chat log widget."""

from rich.markdown import Markdown
from textual.widgets import RichLog


class ChatLog(RichLog):
    """Rich log for displaying chat messages."""

    def add_user_message(self, text: str) -> None:
        """Add a user message to the log."""
        self.write(f"[bold blue]You:[/] {text}")

    def add_assistant_message(self, text: str) -> None:
        """Add an assistant message to the log."""
        self.write("[bold green]Agent:[/]")
        try:
            self.write(Markdown(text))
        except Exception:
            self.write(text)

    def add_system_message(self, text: str) -> None:
        """Add a system message to the log."""
        self.write(f"[dim]{text}[/]")

    def add_error(self, text: str) -> None:
        """Add an error message to the log."""
        self.write(f"[bold red]Error:[/] {text}")
