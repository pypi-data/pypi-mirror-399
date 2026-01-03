"""Command-line menu interface for task management using InquirerPy."""

from InquirerPy import inquirer

from src.cli.prompts import (
    build_menu_choices,
    prompt_confirm_delete,
    prompt_select_status,
    prompt_select_task,
    prompt_task_description,
    prompt_task_title,
)
from src.cli.styles import (
    COLORS,
    STATUS_ICONS,
    TASKFOLIO_STYLE,
    print_error,
    print_header,
    print_info,
    print_success,
)
from src.models.task import Task, TaskStatus
from src.services.task_manager import TaskManager


def handle_add_task(manager: TaskManager) -> None:
    """Handle the add task operation.

    Args:
        manager: TaskManager instance
    """
    title = prompt_task_title()
    description = prompt_task_description()

    success, message = manager.add_task(title, description)
    if success:
        print_success(message)
    else:
        print_error(message)


def display_task(task: Task) -> None:
    """Display a single task with styled output.

    Args:
        task: Task to display
    """
    icon = STATUS_ICONS.get(task.status.value, "?")
    cyan = COLORS["cyan"]
    reset = COLORS["reset"]

    print(f"{cyan}[{task.id}]{reset} {task.title}")
    if task.description:
        print(f"    Description: {task.description}")
    else:
        print("    Description: (none)")
    print(f"    Status: {icon} {task.status.value}")
    print("---")


def handle_view_tasks(manager: TaskManager) -> None:
    """Handle the view all tasks operation.

    Args:
        manager: TaskManager instance
    """
    tasks = manager.get_all_tasks()

    if not tasks:
        print_info("No tasks found. Add your first task.")
        return

    bold = COLORS["bold"]
    reset = COLORS["reset"]
    print(f"\n{bold}=== Your Tasks ==={reset}")
    for task in tasks:
        display_task(task)


def handle_update_task(manager: TaskManager) -> None:
    """Handle the update task operation.

    Args:
        manager: TaskManager instance
    """
    tasks = manager.get_all_tasks()
    task_id = prompt_select_task(tasks, "Select task to update:")

    if task_id is None:
        return

    title_input = inquirer.text(
        message="Enter new title (press Enter to keep current):",
        style=TASKFOLIO_STYLE,
    ).execute()

    desc_input = inquirer.text(
        message="Enter new description (press Enter to keep current):",
        style=TASKFOLIO_STYLE,
    ).execute()

    title = title_input if title_input else None
    description = desc_input if desc_input else None

    if title is None and description is None:
        print_info("No changes made.")
        return

    success, message = manager.update_task(task_id, title, description)
    if success:
        print_success(message)
    else:
        print_error(message)


def handle_delete_task(manager: TaskManager) -> None:
    """Handle the delete task operation.

    Args:
        manager: TaskManager instance
    """
    tasks = manager.get_all_tasks()
    task_id = prompt_select_task(tasks, "Select task to delete:")

    if task_id is None:
        return

    # Find task title for confirmation message
    task = next((t for t in tasks if t.id == task_id), None)
    if task is None:
        print_error(f"Task with ID {task_id} not found.")
        return

    # Confirm deletion
    if not prompt_confirm_delete(task.title):
        print_info("Deletion cancelled.")
        return

    success, message = manager.delete_task(task_id)
    if success:
        print_success(message)
    else:
        print_error(message)


def handle_change_status(manager: TaskManager) -> None:
    """Handle the change task status operation.

    Args:
        manager: TaskManager instance
    """
    tasks = manager.get_all_tasks()
    task_id = prompt_select_task(tasks, "Select task to change status:")

    if task_id is None:
        return

    # Find current task status from the tasks list
    current_task = next((t for t in tasks if t.id == task_id), None)
    if current_task is None:
        print_error(f"Task with ID {task_id} not found.")
        return

    new_status = prompt_select_status(current_task.status)

    success, message = manager.set_status(task_id, new_status)
    if success:
        print_success(message)
    else:
        print_error(message)


def run_menu(manager: TaskManager, username: str) -> None:
    """Run the main menu loop.

    Args:
        manager: TaskManager instance
        username: Current user's name for display
    """
    try:
        while True:
            print_header(username)

            action = inquirer.select(
                message="What would you like to do?",
                choices=build_menu_choices(),
                style=TASKFOLIO_STYLE,
            ).execute()

            if action == "add":
                handle_add_task(manager)
            elif action == "view":
                handle_view_tasks(manager)
            elif action == "update":
                handle_update_task(manager)
            elif action == "delete":
                handle_delete_task(manager)
            elif action == "status":
                handle_change_status(manager)
            elif action == "exit":
                break
    except KeyboardInterrupt:
        pass
    finally:
        print("\nGoodbye from TaskFolio!")
