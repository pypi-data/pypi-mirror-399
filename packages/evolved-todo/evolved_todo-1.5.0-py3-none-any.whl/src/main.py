"""CLI interface for the Todo application.

This module provides the interactive menu-driven interface for managing tasks.
"""

from src.todo_manager import InvalidInputError, TaskNotFoundError, TodoManager
from src.ui_helpers import (
    display_menu,
    print_error,
    print_info,
    print_success,
    prompt_for_description,
    prompt_for_id,
    prompt_for_title,
    render_task_table,
)


def add_task_cli(manager: TodoManager) -> None:
    """Prompt user for task details and create new task.

    Args:
        manager: TodoManager instance to add task to
    """
    print("\n--- Add New Task ---")
    title = prompt_for_title()
    description = prompt_for_description()

    try:
        task = manager.add_task(title, description)
        print_success(f"Task {task.id} created: {task.title}")
    except InvalidInputError as e:
        print_error(str(e))


def view_tasks_cli(manager: TodoManager) -> None:
    """Display all tasks with formatting.

    Args:
        manager: TodoManager instance to retrieve tasks from
    """
    print("\n--- All Tasks ---")
    tasks = manager.get_all_tasks()
    render_task_table(tasks)


def update_task_cli(manager: TodoManager) -> None:
    """Prompt user to update task title and/or description.

    Args:
        manager: TodoManager instance to update task in
    """
    print("\n--- Update Task ---")
    try:
        task_id = prompt_for_id()

        print("\nLeave blank and press Enter to keep current value:")
        update_title = input("Update title? (y/n): ").lower() == "y"
        new_title = prompt_for_title() if update_title else None
        update_desc = input("Update description? (y/n): ").lower() == "y"
        new_description = prompt_for_description() if update_desc else None

        if new_title is None and new_description is None:
            print_info("No changes made (both fields skipped)")
            return

        task = manager.update_task(task_id, new_title, new_description)
        print_success(f"Task {task.id} updated")
        print(f"   Title: {task.title}")
        print(f"   Description: {task.description}")

    except TaskNotFoundError as e:
        print_error(str(e))
    except InvalidInputError as e:
        print_error(str(e))


def delete_task_cli(manager: TodoManager) -> None:
    """Prompt user to delete a task by ID.

    Args:
        manager: TodoManager instance to delete task from
    """
    print("\n--- Delete Task ---")
    try:
        task_id = prompt_for_id()
        manager.delete_task(task_id)
        print_success(f"Task {task_id} deleted")

    except TaskNotFoundError as e:
        print_error(str(e))


def toggle_status_cli(manager: TodoManager) -> None:
    """Prompt user to toggle task completion status.

    Args:
        manager: TodoManager instance to toggle task in
    """
    print("\n--- Toggle Task Status ---")
    try:
        task_id = prompt_for_id()
        task = manager.toggle_status(task_id)

        status_text = "complete" if task.status else "incomplete"
        print_success(f"Task {task.id} marked as {status_text}: {task.title}")

    except TaskNotFoundError as e:
        print_error(str(e))


def main_loop(manager: TodoManager) -> None:
    """Run the main application loop with menu-driven interface.

    Args:
        manager: TodoManager instance for task operations
    """
    print("\n" + "=" * 50)
    print("  Welcome to Evolution of Todo - By Ali Askari")
    print("=" * 50)

    try:
        while True:
            display_menu()

            try:
                choice = int(input("\nSelect option (1-6): "))

                if choice == 1:
                    add_task_cli(manager)
                elif choice == 2:
                    view_tasks_cli(manager)
                elif choice == 3:
                    update_task_cli(manager)
                elif choice == 4:
                    delete_task_cli(manager)
                elif choice == 5:
                    toggle_status_cli(manager)
                elif choice == 6:
                    print("\n" + "=" * 50)
                    print("  Exiting... Goodbye!")
                    print("=" * 50 + "\n")
                    break
                else:
                    print_error("Invalid option. Please select 1-6.")

            except ValueError:
                print_error("Please enter a number (1-6)")

    except KeyboardInterrupt:
        print("\n\n" + "=" * 50)
        print("  Exiting gracefully... Goodbye!")
        print("=" * 50 + "\n")


def main() -> None:
    """Entry point for the CLI application."""
    manager = TodoManager()
    main_loop(manager)


if __name__ == "__main__":
    main()
