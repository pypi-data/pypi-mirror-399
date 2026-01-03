"""Message input widget."""

from textual.widgets import Input


class MessageInput(Input):
    """Input field for chat messages."""

    DEFAULT_CSS = """
    MessageInput {
        dock: bottom;
        height: auto;
        padding: 1 2;
    }
    """

    def __init__(self) -> None:
        super().__init__(placeholder="Enter message... (Ctrl+C to quit)")
