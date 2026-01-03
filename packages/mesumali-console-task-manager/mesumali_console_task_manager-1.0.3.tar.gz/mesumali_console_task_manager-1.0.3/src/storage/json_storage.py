"""JSON file storage for persisting task data."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any


class JsonStorage:
    """Handles JSON file I/O with atomic writes for data integrity."""

    def __init__(self, db_dir: str, username: str) -> None:
        """Initialize storage for a specific user.

        Args:
            db_dir: Directory path for JSON files (e.g., "db/")
            username: Username for file naming
        """
        self.db_dir = Path(db_dir)
        self.username = username
        self.file_path = self.db_dir / f"user_{username}.json"

        # Create db directory if it doesn't exist
        self.db_dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> dict[str, Any]:
        """Load tasks from the JSON file.

        Returns:
            Dictionary with 'next_id' and 'tasks' keys.
            Returns empty data structure if file doesn't exist or is corrupt.
        """
        if not self.file_path.exists():
            return {"next_id": 1, "tasks": {}}

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Validate structure
                if "next_id" not in data or "tasks" not in data:
                    return {"next_id": 1, "tasks": {}}
                return data
        except (json.JSONDecodeError, OSError):
            # Handle corrupt JSON or I/O errors gracefully
            return {"next_id": 1, "tasks": {}}

    def save(self, data: dict[str, Any]) -> None:
        """Save tasks to the JSON file with atomic write.

        Args:
            data: Dictionary with 'next_id' and 'tasks' keys

        Raises:
            OSError: On unrecoverable I/O error
        """
        # Write to temp file first, then atomically rename
        fd, temp_path = tempfile.mkstemp(dir=str(self.db_dir), suffix=".json")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            os.replace(temp_path, self.file_path)
        except Exception:
            # Clean up temp file on failure
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise
