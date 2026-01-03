"""Entry point for the TaskFolio application."""

from InquirerPy import inquirer

from src.cli.menu import run_menu
from src.cli.prompts import validate_username
from src.cli.styles import TASKFOLIO_STYLE
from src.services.task_manager import TaskManager
from src.storage.json_storage import JsonStorage


def print_welcome_banner() -> None:
    """Print a professional welcome banner."""
    cyan = "\033[96m"
    bold = "\033[1m"
    reset = "\033[0m"

    banner = f"""
{bold}{cyan}
╔══════════════════════════════════════════════════════════════════════════╗
║  ████████╗ █████╗ ███████╗██╗  ██╗███████╗ ██████╗ ██╗     ██╗ ██████╗   ║
║  ╚══██╔══╝██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔═══██╗██║     ██║██╔═══██╗  ║
║     ██║   ███████║███████╗█████╔╝ █████╗  ██║   ██║██║     ██║██║   ██║  ║
║     ██║   ██╔══██║╚════██║██╔═██╗ ██╔══╝  ██║   ██║██║     ██║██║   ██║  ║
║     ██║   ██║  ██║███████║██║  ██╗██║     ╚██████╔╝███████╗██║╚██████╔╝  ║
║     ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝      ╚═════╝ ╚══════╝╚═╝ ╚═════╝   ║
╠══════════════════════════════════════════════════════════════════════════╣
║                    Welcome to TaskFolio!                                 ║
║             Your Personal Interactive Task Manager                       ║
╚══════════════════════════════════════════════════════════════════════════╝{reset}
"""
    print(banner)


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
