"""Business logic for managing todo tasks.

This module provides the TodoManager class and custom exceptions for task operations.
"""

from src.models import Task


class TaskNotFoundError(Exception):
    """Raised when an operation targets a non-existent task ID."""

    pass


class InvalidInputError(ValueError):
    """Raised when user input violates validation rules."""

    pass


class TodoManager:
    """Manages todo tasks in memory with CRUD operations.

    Attributes:
        _tasks: Dictionary mapping task IDs to Task instances
        _next_id: Counter for sequential ID generation
    """

    def __init__(self) -> None:
        """Initialize empty task collection with ID counter starting at 1."""
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def add_task(self, title: str, description: str = "") -> Task:
        """Create new task with unique ID and store in memory.

        Args:
            title: Task title (required, non-empty)
            description: Task details (optional, defaults to empty string)

        Returns:
            Created Task instance with auto-generated ID

        Raises:
            InvalidInputError: If title is empty or whitespace-only
        """
        if not title or title.isspace():
            raise InvalidInputError("Task title cannot be empty")

        task = Task(
            id=self._next_id, title=title, description=description, status=False
        )
        self._tasks[self._next_id] = task
        self._next_id += 1
        return task

    def get_task(self, task_id: int) -> Task:
        """Retrieve task by ID.

        Args:
            task_id: Unique task identifier

        Returns:
            Task instance

        Raises:
            TaskNotFoundError: If task_id doesn't exist in storage
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(f"Task with ID {task_id} not found")
        return self._tasks[task_id]

    def get_all_tasks(self) -> list[Task]:
        """Retrieve all tasks sorted by ID (oldest to newest).

        Returns:
            List of all Task instances, empty list if no tasks exist
        """
        return sorted(self._tasks.values(), key=lambda t: t.id)

    def update_task(
        self, task_id: int, title: str | None = None, description: str | None = None
    ) -> Task:
        """Update task title and/or description (partial updates supported).

        Args:
            task_id: Task to update
            title: New title (None = no change, must be non-empty if provided)
            description: New description (None = no change, can be empty)

        Returns:
            Updated Task instance

        Raises:
            TaskNotFoundError: If task_id doesn't exist
            InvalidInputError: If title is provided but empty/whitespace-only
        """
        task = self.get_task(task_id)  # Raises TaskNotFoundError if missing

        if title is not None:
            if not title or title.isspace():
                raise InvalidInputError("Task title cannot be empty")
            task.title = title

        if description is not None:
            task.description = description

        return task

    def delete_task(self, task_id: int) -> None:
        """Permanently remove task from storage.

        Args:
            task_id: Task to delete

        Raises:
            TaskNotFoundError: If task_id doesn't exist
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(f"Task with ID {task_id} not found")
        del self._tasks[task_id]

    def toggle_status(self, task_id: int) -> Task:
        """Toggle task between complete and incomplete status.

        Args:
            task_id: Task to toggle

        Returns:
            Updated Task instance with flipped status

        Raises:
            TaskNotFoundError: If task_id doesn't exist
        """
        task = self.get_task(task_id)  # Raises TaskNotFoundError if missing
        task.status = not task.status
        return task
