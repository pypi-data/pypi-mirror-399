"""Default commands for miu-code."""

from pathlib import Path

from miu_core.commands import CommandRegistry

# Default commands directory
COMMANDS_DIR = Path(__file__).parent


def get_default_commands() -> CommandRegistry:
    """Get registry with default commands loaded.

    Returns:
        CommandRegistry with default commands
    """
    registry = CommandRegistry()
    registry.load_from_directory(COMMANDS_DIR)
    return registry


__all__ = ["COMMANDS_DIR", "get_default_commands"]
