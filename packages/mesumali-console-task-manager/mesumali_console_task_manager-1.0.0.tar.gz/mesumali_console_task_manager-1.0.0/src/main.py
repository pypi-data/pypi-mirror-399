"""Entry point for the Console Task Manager application."""

import re

from src.cli.menu import run_menu
from src.services.task_manager import TaskManager
from src.storage.json_storage import JsonStorage


def get_username() -> str:
    """Prompt for and validate username.

    Returns:
        Valid username (alphanumeric and underscores only)
    """
    print("Welcome to Task Manager!")

    while True:
        username = input("Enter your username: ").strip()

        if not username:
            print("Error: Username cannot be empty.")
            continue

        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            print("Error: Username must be alphanumeric (letters, numbers, underscores only).")
            continue

        return username


def main() -> None:
    """Main entry point for the application."""
    username = get_username()

    # Initialize storage and manager
    storage = JsonStorage(db_dir="db", username=username)
    manager = TaskManager(storage=storage, username=username)

    # Run the menu loop
    run_menu(manager, username)


if __name__ == "__main__":
    main()
