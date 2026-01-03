"""Entry point for the TaskFolio application."""

import sys

from InquirerPy import inquirer

from src.cli.menu import run_menu
from src.cli.prompts import validate_username
from src.cli.styles import TASKFOLIO_STYLE
from src.services.task_manager import TaskManager
from src.storage.json_storage import JsonStorage

VERSION = "1.0.3"

LOGO = """
╔══════════════════════════════════════════════════════════════════════════╗
║  ████████╗ █████╗ ███████╗██╗  ██╗███████╗ ██████╗ ██╗     ██╗ ██████╗   ║
║  ╚══██╔══╝██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔═══██╗██║     ██║██╔═══██╗  ║
║     ██║   ███████║███████╗█████╔╝ █████╗  ██║   ██║██║     ██║██║   ██║  ║
║     ██║   ██╔══██║╚════██║██╔═██╗ ██╔══╝  ██║   ██║██║     ██║██║   ██║  ║
║     ██║   ██║  ██║███████║██║  ██╗██║     ╚██████╔╝███████╗██║╚██████╔╝  ║
║     ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝      ╚═════╝ ╚══════╝╚═╝ ╚═════╝   ║
╚══════════════════════════════════════════════════════════════════════════╝"""


def print_welcome_banner() -> None:
    """Print a professional welcome banner."""
    cyan = "\033[96m"
    bold = "\033[1m"
    reset = "\033[0m"

    banner = f"""{bold}{cyan}{LOGO}
╔══════════════════════════════════════════════════════════════════════════╗
║                    Welcome to TaskFolio!                                 ║
║             Your Personal Interactive Task Manager                       ║
╚══════════════════════════════════════════════════════════════════════════╝{reset}
"""
    print(banner)


def print_help() -> None:
    """Print help information with logo."""
    cyan = "\033[96m"
    bold = "\033[1m"
    reset = "\033[0m"

    help_text = f"""{bold}{cyan}{LOGO}
╠══════════════════════════════════════════════════════════════════════════╣
║  TaskFolio v{VERSION} - Your Personal Interactive Task Manager           ║
╚══════════════════════════════════════════════════════════════════════════╝{reset}

{bold}Usage:{reset}  mesumali-todo [options]

{bold}Options:{reset}
  --help, -h      Show this help message
  --version, -v   Show version number

{bold}Features:{reset}
  - Arrow-key menu navigation
  - Fuzzy search for tasks
  - Visual status indicators
  - Delete confirmation

{bold}Run without options to start the interactive task manager.{reset}
"""
    print(help_text)


def get_username() -> str | None:
    """Prompt for and validate username using InquirerPy.

    Returns:
        Valid username (alphanumeric and underscores only), or None if cancelled
    """
    print_welcome_banner()

    try:
        return inquirer.text(
            message="Enter your username:",
            validate=validate_username,
            invalid_message="Username must be alphanumeric (letters, numbers, underscores only)",
            style=TASKFOLIO_STYLE,
        ).execute()
    except KeyboardInterrupt:
        return None


def main() -> None:
    """Main entry point for the application."""
    # Handle command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ("--help", "-h"):
            print_help()
            return
        if arg in ("--version", "-v"):
            print(f"TaskFolio v{VERSION}")
            return

    try:
        username = get_username()

        if username is None:
            print("\nGoodbye from TaskFolio!")
            return

        # Initialize storage and manager
        storage = JsonStorage(db_dir="db", username=username)
        manager = TaskManager(storage=storage, username=username)

        # Run the menu loop
        run_menu(manager, username)
    except KeyboardInterrupt:
        print("\nGoodbye from TaskFolio!")


if __name__ == "__main__":
    main()
