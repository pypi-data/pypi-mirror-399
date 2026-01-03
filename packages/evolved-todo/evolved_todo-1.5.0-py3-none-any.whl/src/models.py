"""Data models for the Todo CLI application.

This module defines the Task entity with validation and display formatting.
"""

from dataclasses import dataclass


@dataclass
class Task:
    """Represents a todo task with unique ID, title, description, and status.

    Attributes:
        id: Unique integer identifier (immutable, auto-generated)
        title: Task description (required, non-empty, mutable)
        description: Extended task details (optional, mutable)
        status: Completion state (False=incomplete, True=complete, mutable)
    """

    id: int
    title: str
    description: str = ""
    status: bool = False

    def __str__(self) -> str:
        """Format task for display with status symbol and details.

        Returns:
            Formatted string showing status, ID, title, and description preview.
        """
        status_symbol = "[✓]" if self.status else "[ ]"
        desc_preview = (
            self.description[:50] + "..."
            if len(self.description) > 50
            else self.description
        )
        return f"{status_symbol} Task {self.id}: {self.title}\n    {desc_preview}"
