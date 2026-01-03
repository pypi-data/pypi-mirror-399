"""TaskFolio CLI prompt builders and validators using InquirerPy."""

import re

from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from src.cli.styles import STATUS_ICONS, TASKFOLIO_STYLE, print_info
from src.models.task import Task, TaskStatus

# Constants
MAX_TITLE_LENGTH = 200


def validate_title(text: str) -> bool:
    """Validate task title input.

    Args:
        text: User input text

    Returns:
        True if valid (non-empty, <= 200 chars), False if invalid
    """
    stripped = text.strip()
    return len(stripped) > 0 and len(stripped) <= MAX_TITLE_LENGTH


def validate_username(text: str) -> bool:
    """Validate username input.

    Args:
        text: User input text

    Returns:
        True if valid (non-empty, alphanumeric + underscore), False if invalid
    """
    if not text:
        return False
    return bool(re.match(r"^[a-zA-Z0-9_]+$", text))


def build_task_choices(tasks: list[Task]) -> list[Choice]:
    """Convert a list of Task objects into InquirerPy Choice objects.

    Args:
        tasks: List of Task objects from TaskManager

    Returns:
        List of Choice objects with value=task.id and name=formatted_string
    """
    choices = []
    for task in tasks:
        icon = STATUS_ICONS.get(task.status.value, "?")
        name = f"[{task.id}] {task.title} - {icon} {task.status.value}"
        choices.append(Choice(value=task.id, name=name))
    return choices


def build_status_choices(current_status: TaskStatus | None = None) -> list[Choice]:
    """Create status option choices with visual indicators.

    Args:
        current_status: Current status to mark as current (optional)

    Returns:
        List of Choice objects for each status
    """
    statuses = [
        (TaskStatus.INCOMPLETE, "incomplete"),
        (TaskStatus.IN_PROCESSING, "inProcessing"),
        (TaskStatus.COMPLETE, "complete"),
    ]

    choices = []
    for status_enum, status_value in statuses:
        icon = STATUS_ICONS.get(status_value, "?")
        name = f"{icon} {status_value}"
        if current_status == status_enum:
            name += " (current)"
        choices.append(Choice(value=status_enum, name=name))
    return choices


def build_menu_choices() -> list[Choice]:
    """Create main menu option choices.

    Returns:
        List of Choice objects for menu options
    """
    return [
        Choice(value="add", name="[1] Add Task"),
        Choice(value="view", name="[2] View All Tasks"),
        Choice(value="update", name="[3] Update Task"),
        Choice(value="delete", name="[4] Delete Task"),
        Choice(value="status", name="[5] Change Status"),
        Choice(value="exit", name="[6] Exit"),
    ]


def prompt_task_title() -> str:
    """Prompt for and validate task title.

    Returns:
        Validated title string
    """
    return inquirer.text(
        message="Enter task title:",
        validate=validate_title,
        invalid_message=f"Title required (max {MAX_TITLE_LENGTH} characters)",
        style=TASKFOLIO_STYLE,
    ).execute()


def prompt_task_description() -> str:
    """Prompt for optional task description.

    Returns:
        Description string (may be empty)
    """
    return inquirer.text(
        message="Enter task description (optional):",
        style=TASKFOLIO_STYLE,
    ).execute()


def prompt_select_task(tasks: list[Task], message: str) -> int | None:
    """Prompt user to select a task from list.

    Args:
        tasks: List of available tasks
        message: Prompt message to display

    Returns:
        Task ID if selected, None if no tasks available
    """
    if not tasks:
        print_info("No tasks found. Add a task first.")
        return None

    choices = build_task_choices(tasks)

    return inquirer.fuzzy(
        message=message,
        choices=choices,
        style=TASKFOLIO_STYLE,
    ).execute()


def prompt_select_status(current_status: TaskStatus) -> TaskStatus:
    """Prompt user to select a status.

    Args:
        current_status: Current task status (for pre-selection)

    Returns:
        Selected TaskStatus enum value
    """
    choices = build_status_choices(current_status)

    return inquirer.select(
        message="Select new status:",
        choices=choices,
        default=current_status,
        style=TASKFOLIO_STYLE,
    ).execute()


def prompt_confirm_delete(task_title: str) -> bool:
    """Prompt for delete confirmation.

    Args:
        task_title: Title of task to delete

    Returns:
        True if confirmed, False if cancelled
    """
    return inquirer.confirm(
        message=f'Delete task "{task_title}"?',
        default=False,
        style=TASKFOLIO_STYLE,
    ).execute()
