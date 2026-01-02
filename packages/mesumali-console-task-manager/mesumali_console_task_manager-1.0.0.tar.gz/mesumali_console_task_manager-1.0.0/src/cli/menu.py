"""Command-line menu interface for task management."""

from src.models.task import Task, TaskStatus
from src.services.task_manager import TaskManager


def display_menu(username: str) -> None:
    """Display the main menu options.

    Args:
        username: Current user's name for display
    """
    print(f"\n=== Task Manager ({username}) ===")
    print("1. Add Task")
    print("2. View All Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Change Task Status")
    print("6. Exit")


def get_choice() -> str:
    """Get user's menu choice.

    Returns:
        User input string
    """
    return input("\nEnter choice (1-6): ").strip()


def handle_add_task(manager: TaskManager) -> None:
    """Handle the add task operation.

    Args:
        manager: TaskManager instance
    """
    title = input("Enter task title: ")
    description = input("Enter task description (optional): ")

    success, message = manager.add_task(title, description)
    print(f"\n{message}")


def display_task(task: Task) -> None:
    """Display a single task.

    Args:
        task: Task to display
    """
    print(f"[{task.id}] {task.title}")
    if task.description:
        print(f"    Description: {task.description}")
    print(f"    Status: {task.status.value}")
    print("---")


def handle_view_tasks(manager: TaskManager) -> None:
    """Handle the view all tasks operation.

    Args:
        manager: TaskManager instance
    """
    tasks = manager.get_all_tasks()

    if not tasks:
        print("\nNo tasks found. Add your first task using option 1.")
        return

    print("\n=== Your Tasks ===")
    for task in tasks:
        display_task(task)


def handle_update_task(manager: TaskManager) -> None:
    """Handle the update task operation.

    Args:
        manager: TaskManager instance
    """
    id_input = input("Enter task ID to update: ").strip()

    try:
        task_id = int(id_input)
    except ValueError:
        print("\nError: Please enter a valid numeric ID.")
        return

    title_input = input("Enter new title (press Enter to keep current): ")
    desc_input = input("Enter new description (press Enter to keep current): ")

    title = title_input if title_input else None
    description = desc_input if desc_input else None

    if title is None and description is None:
        print("\nNo changes made.")
        return

    success, message = manager.update_task(task_id, title, description)
    print(f"\n{message}")


def handle_delete_task(manager: TaskManager) -> None:
    """Handle the delete task operation.

    Args:
        manager: TaskManager instance
    """
    id_input = input("Enter task ID to delete: ").strip()

    try:
        task_id = int(id_input)
    except ValueError:
        print("\nError: Please enter a valid numeric ID.")
        return

    success, message = manager.delete_task(task_id)
    print(f"\n{message}")


def handle_change_status(manager: TaskManager) -> None:
    """Handle the change task status operation.

    Args:
        manager: TaskManager instance
    """
    id_input = input("Enter task ID: ").strip()

    try:
        task_id = int(id_input)
    except ValueError:
        print("\nError: Please enter a valid numeric ID.")
        return

    print("Select new status:")
    print("  1. incomplete")
    print("  2. inProcessing")
    print("  3. complete")

    status_choice = input("Enter choice (1-3): ").strip()

    status_map = {
        "1": TaskStatus.INCOMPLETE,
        "2": TaskStatus.IN_PROCESSING,
        "3": TaskStatus.COMPLETE,
    }

    if status_choice not in status_map:
        print("\nError: Invalid status choice. Please enter 1, 2, or 3.")
        return

    success, message = manager.set_status(task_id, status_map[status_choice])
    print(f"\n{message}")


def run_menu(manager: TaskManager, username: str) -> None:
    """Run the main menu loop.

    Args:
        manager: TaskManager instance
        username: Current user's name for display
    """
    while True:
        display_menu(username)
        choice = get_choice()

        if choice == "1":
            handle_add_task(manager)
        elif choice == "2":
            handle_view_tasks(manager)
        elif choice == "3":
            handle_update_task(manager)
        elif choice == "4":
            handle_delete_task(manager)
        elif choice == "5":
            handle_change_status(manager)
        elif choice == "6":
            print("\nGoodbye!")
            break
        else:
            print("\nError: Invalid choice. Please enter a number from 1 to 6.")
