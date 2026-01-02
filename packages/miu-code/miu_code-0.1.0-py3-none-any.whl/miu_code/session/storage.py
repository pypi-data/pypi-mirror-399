"""Session storage using JSONL."""

import json
import uuid
from pathlib import Path

from miu_core.models import Message


class SessionStorage:
    """JSONL-based session persistence."""

    def __init__(
        self,
        session_id: str | None = None,
        working_dir: str = ".",
    ) -> None:
        self.session_id = session_id or str(uuid.uuid4())[:8]
        self.base_dir = Path(working_dir) / ".miu" / "sessions"

    @property
    def session_file(self) -> Path:
        return self.base_dir / f"{self.session_id}.jsonl"

    def save(self, messages: list[Message]) -> None:
        """Save messages to JSONL file."""
        self.base_dir.mkdir(parents=True, exist_ok=True)

        with open(self.session_file, "w", encoding="utf-8") as f:
            for msg in messages:
                line = msg.model_dump_json()
                f.write(line + "\n")

    def load(self) -> list[Message]:
        """Load messages from JSONL file."""
        if not self.session_file.exists():
            return []

        messages: list[Message] = []
        try:
            with open(self.session_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        data = json.loads(line)
                        messages.append(Message.model_validate(data))
        except (json.JSONDecodeError, OSError):
            return []

        return messages

    def clear(self) -> None:
        """Clear session file."""
        if self.session_file.exists():
            self.session_file.unlink()
