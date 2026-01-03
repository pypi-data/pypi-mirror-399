"""
UI Helpers for Todo CLI Application.

This module provides Rich library-based visual formatting for the CLI interface,
including color-coded messages, styled tables, formatted prompts, and menu display.

All visual presentation logic is isolated here to maintain separation of concerns
from business logic (todo_manager.py) and data models (models.py).
"""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.table import Table

from src.models import Task

# Initialize Rich Console (module-level, reused for all output)
console = Console()

# Color Theme Constants (Rich semantic color names)
COLOR_PRIMARY: str = "cyan"  # Headers, borders, prompts
COLOR_SUCCESS: str = "green"  # Success messages, completed tasks
COLOR_ERROR: str = "red"  # Error messages, failures
COLOR_INFO: str = "blue"  # Info messages, neutral feedback
COLOR_INCOMPLETE: str = "yellow"  # Incomplete task status

# Table Layout Constants (column widths per FR-021, FR-022, FR-023)
TABLE_WIDTH_ID: int = 5  # Right-aligned
TABLE_WIDTH_STATUS: int = 10  # Centered
TABLE_WIDTH_TITLE: int = 30  # Left-aligned
TABLE_WIDTH_DESC: int = 40  # Left-aligned, minimum width

# Status Symbol Constants (Unicode + ASCII fallback)
SYMBOL_COMPLETE_UNICODE: str = "✓"
SYMBOL_INCOMPLETE_UNICODE: str = "⏳"
SYMBOL_COMPLETE_ASCII: str = "[OK]"
SYMBOL_INCOMPLETE_ASCII: str = "[...]"


def get_status_symbol(completed: bool, use_unicode: bool = True) -> str:
    """
    Return appropriate status symbol based on terminal capabilities.

    Args:
        completed: Task completion status (True=complete, False=incomplete)
        use_unicode: Whether terminal supports Unicode (auto-detected by Rich)

    Returns:
        Status symbol string (Unicode or ASCII fallback)
    """
    if use_unicode:
        return SYMBOL_COMPLETE_UNICODE if completed else SYMBOL_INCOMPLETE_UNICODE
    else:
        return SYMBOL_COMPLETE_ASCII if completed else SYMBOL_INCOMPLETE_ASCII


def print_success(message: str) -> None:
    """
    Print success message in green with [OK] prefix.

    Args:
        message: Success message text to display
    """
    console.print(f"[{COLOR_SUCCESS}][OK] {message}[/]")


def print_error(message: str) -> None:
    """
    Print error message in red with [ERROR] prefix.

    Args:
        message: Error message text to display
    """
    console.print(f"[{COLOR_ERROR}][ERROR] {message}[/]")


def print_info(message: str) -> None:
    """
    Print info message in blue with [INFO] prefix.

    Args:
        message: Info message text to display
    """
    console.print(f"[{COLOR_INFO}][INFO] {message}[/]")


def render_task_table(tasks: list[Task]) -> None:
    """
    Render task list as a styled Rich table with color-coded status.

    Args:
        tasks: List of Task objects to display
    """
    if not tasks:
        print_info("No tasks found")
        return

    # Create table with styled header
    table = Table(show_header=True, header_style=f"bold {COLOR_PRIMARY}")

    # Add columns with specified widths and alignment
    table.add_column("ID", width=TABLE_WIDTH_ID, justify="right")
    table.add_column("Status", width=TABLE_WIDTH_STATUS, justify="center")
    table.add_column("Title", width=TABLE_WIDTH_TITLE, justify="left")
    table.add_column("Description", width=TABLE_WIDTH_DESC, justify="left")

    # Add rows for each task
    for task in tasks:
        # Color-code status: green for complete, yellow for incomplete
        status_color = COLOR_SUCCESS if task.status else COLOR_INCOMPLETE
        # Use ASCII fallback for Windows compatibility
        status_symbol = get_status_symbol(task.status, use_unicode=False)
        status_text = f"[{status_color}]{status_symbol}[/]"

        table.add_row(
            str(task.id),
            status_text,
            task.title,
            task.description
        )

    console.print(table)


def display_menu() -> None:
    """
    Display styled main menu with header panel and colored options.
    """
    # Header panel with app title and version
    console.print(
        Panel("CLI Based Todo", style=f"bold {COLOR_PRIMARY}")
    )

    # Menu options with cyan-colored numbers
    console.print(f"[{COLOR_PRIMARY}]1.[/] Add Task")
    console.print(f"[{COLOR_PRIMARY}]2.[/] View Tasks")
    console.print(f"[{COLOR_PRIMARY}]3.[/] Update Task")
    console.print(f"[{COLOR_PRIMARY}]4.[/] Delete Task")
    console.print(f"[{COLOR_PRIMARY}]5.[/] Toggle Task Status")
    console.print(f"[{COLOR_PRIMARY}]6.[/] Exit")
    console.print()  # Blank line after menu


def prompt_for_title() -> str:
    """
    Prompt user for task title with styled input prompt.

    Returns:
        Task title string entered by user
    """
    return Prompt.ask(f"[{COLOR_PRIMARY}]Enter task title[/]")


def prompt_for_description() -> str:
    """
    Prompt user for task description with styled optional prompt.

    Returns:
        Task description string (empty string if skipped)
    """
    return Prompt.ask(
        f"[{COLOR_PRIMARY}]Enter task description (optional)[/]", default=""
    )


def prompt_for_id() -> int:
    """
    Prompt user for task ID with styled input prompt and validation.

    Returns:
        Task ID integer entered by user (Rich validates numeric input)
    """
    return IntPrompt.ask(f"[{COLOR_PRIMARY}]Enter task ID[/]")
