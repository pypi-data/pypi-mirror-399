"""Task model and status enum for the task management application."""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class TaskStatus(Enum):
    """Represents the completion state of a task."""

    INCOMPLETE = "incomplete"
    IN_PROCESSING = "inProcessing"
    COMPLETE = "complete"

    @classmethod
    def from_string(cls, value: str) -> "TaskStatus":
        """Convert a string to TaskStatus enum value."""
        for status in cls:
            if status.value == value:
                return status
        raise ValueError(f"Invalid status: {value}")


@dataclass
class Task:
    """Represents a single todo item managed by the user."""

    id: int
    title: str
    description: str
    status: TaskStatus

    def to_dict(self) -> dict[str, Any]:
        """Convert the task to a dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        """Create a Task instance from a dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            status=TaskStatus.from_string(data["status"]),
        )
