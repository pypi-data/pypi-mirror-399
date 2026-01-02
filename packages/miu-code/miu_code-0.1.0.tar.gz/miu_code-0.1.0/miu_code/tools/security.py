"""Security utilities for file operations."""

from pathlib import Path


class PathTraversalError(Exception):
    """Raised when a path attempts to escape the working directory."""

    def __init__(self, path: str, working_dir: str) -> None:
        self.path = path
        self.working_dir = working_dir
        super().__init__(f"Path '{path}' is outside working directory '{working_dir}'")


def validate_path(file_path: str, working_dir: str) -> Path:
    """Validate that a path stays within the working directory.

    Args:
        file_path: The file path to validate (absolute or relative)
        working_dir: The allowed working directory

    Returns:
        Resolved Path object within working directory

    Raises:
        PathTraversalError: If path escapes working directory
    """
    base = Path(working_dir).resolve()
    target = Path(file_path)

    if not target.is_absolute():
        target = base / target

    resolved = target.resolve()

    # Check that resolved path is within or equal to base directory
    try:
        resolved.relative_to(base)
    except ValueError:
        raise PathTraversalError(file_path, working_dir) from None

    return resolved


def is_safe_path(file_path: str, working_dir: str) -> bool:
    """Check if a path is safe (within working directory).

    Args:
        file_path: The file path to check
        working_dir: The allowed working directory

    Returns:
        True if path is safe, False otherwise
    """
    try:
        validate_path(file_path, working_dir)
        return True
    except PathTraversalError:
        return False
