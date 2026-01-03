"""Command history management."""

from pathlib import Path


class HistoryManager:
    """Manages command history with file persistence."""

    def __init__(self, history_file: Path | None = None, max_entries: int = 1000) -> None:
        self._history_file = history_file
        self._max_entries = max_entries
        self._entries: list[str] = []
        self._current_index = -1
        self._load_history()

    def _load_history(self) -> None:
        """Load history from file."""
        if not self._history_file or not self._history_file.exists():
            return
        try:
            content = self._history_file.read_text("utf-8")
            self._entries = [line for line in content.strip().split("\n") if line]
        except Exception:
            self._entries = []

    def _save_history(self) -> None:
        """Save history to file."""
        if not self._history_file:
            return
        try:
            self._history_file.parent.mkdir(parents=True, exist_ok=True)
            content = "\n".join(self._entries[-self._max_entries :])
            self._history_file.write_text(content + "\n", "utf-8")
        except Exception:
            pass

    def add(self, entry: str) -> None:
        """Add entry to history."""
        entry = entry.strip()
        if not entry:
            return
        # Remove duplicate if exists
        if entry in self._entries:
            self._entries.remove(entry)
        self._entries.append(entry)
        self._save_history()

    def get_previous(self, current: str = "", prefix: str = "") -> str | None:
        """Get previous history entry matching prefix."""
        if not self._entries:
            return None

        start = self._current_index
        if start == -1:
            start = len(self._entries)

        for i in range(start - 1, -1, -1):
            entry = self._entries[i]
            if prefix and not entry.startswith(prefix):
                continue
            self._current_index = i
            return entry

        return None

    def get_next(self, prefix: str = "") -> str | None:
        """Get next history entry matching prefix."""
        if self._current_index == -1:
            return None

        for i in range(self._current_index + 1, len(self._entries)):
            entry = self._entries[i]
            if prefix and not entry.startswith(prefix):
                continue
            self._current_index = i
            return entry

        # Reached end, reset
        self._current_index = -1
        return None

    def reset_navigation(self) -> None:
        """Reset history navigation state."""
        self._current_index = -1
