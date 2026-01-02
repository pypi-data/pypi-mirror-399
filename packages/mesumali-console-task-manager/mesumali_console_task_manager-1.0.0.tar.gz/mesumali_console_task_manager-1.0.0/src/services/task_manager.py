"""Task management service with CRUD operations."""

from src.models.task import Task, TaskStatus
from src.storage.json_storage import JsonStorage


class TaskManager:
    """Provides task management operations with validation and persistence."""

    MAX_TITLE_LENGTH = 200

    def __init__(self, storage: JsonStorage, username: str) -> None:
        """Initialize TaskManager with storage and username.

        Args:
            storage: JsonStorage instance for persistence
            username: String identifier for the user
        """
        self.storage = storage
        self.username = username
        self._data = storage.load()

    def _save(self) -> None:
        """Persist current state to storage."""
        self.storage.save(self._data)

    def add_task(self, title: str, description: str = "") -> tuple[bool, str]:
        """Add a new task.

        Args:
            title: Task title (required, max 200 chars)
            description: Task description (optional)

        Returns:
            Tuple of (success, message)
        """
        # Validate title
        title = title.strip()
        if not title:
            return False, "Error: Title cannot be empty."
        if len(title) > self.MAX_TITLE_LENGTH:
            return False, f"Error: Title exceeds {self.MAX_TITLE_LENGTH} characters."

        # Generate ID and create task
        task_id = self._data["next_id"]
        task = Task(
            id=task_id,
            title=title,
            description=description.strip(),
            status=TaskStatus.INCOMPLETE,
        )

        # Store and persist
        self._data["tasks"][str(task_id)] = task.to_dict()
        self._data["next_id"] = task_id + 1
        self._save()

        return True, f"Task {task_id} created successfully."

    def get_all_tasks(self) -> list[Task]:
        """Get all tasks for the current user.

        Returns:
            List of Task objects sorted by ID ascending
        """
        tasks = [Task.from_dict(data) for data in self._data["tasks"].values()]
        return sorted(tasks, key=lambda t: t.id)

    def update_task(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
    ) -> tuple[bool, str]:
        """Update an existing task.

        Args:
            task_id: ID of task to update
            title: New title (None = no change)
            description: New description (None = no change)

        Returns:
            Tuple of (success, message)
        """
        str_id = str(task_id)
        if str_id not in self._data["tasks"]:
            return False, f"Error: Task with ID {task_id} not found."

        # Validate new title if provided
        if title is not None:
            title = title.strip()
            if not title:
                return False, "Error: Title cannot be empty."
            if len(title) > self.MAX_TITLE_LENGTH:
                return False, f"Error: Title exceeds {self.MAX_TITLE_LENGTH} characters."
            self._data["tasks"][str_id]["title"] = title

        # Update description if provided
        if description is not None:
            self._data["tasks"][str_id]["description"] = description.strip()

        self._save()
        return True, f"Task {task_id} updated successfully."

    def delete_task(self, task_id: int) -> tuple[bool, str]:
        """Delete a task by ID.

        Args:
            task_id: ID of task to delete

        Returns:
            Tuple of (success, message)
        """
        str_id = str(task_id)
        if str_id not in self._data["tasks"]:
            return False, f"Error: Task with ID {task_id} not found."

        del self._data["tasks"][str_id]
        self._save()
        return True, f"Task {task_id} deleted successfully."

    def set_status(self, task_id: int, status: TaskStatus) -> tuple[bool, str]:
        """Change a task's status.

        Args:
            task_id: ID of task to update
            status: New status (TaskStatus enum value)

        Returns:
            Tuple of (success, message)
        """
        str_id = str(task_id)
        if str_id not in self._data["tasks"]:
            return False, f"Error: Task with ID {task_id} not found."

        self._data["tasks"][str_id]["status"] = status.value
        self._save()
        return True, f"Task {task_id} marked as {status.value}."
