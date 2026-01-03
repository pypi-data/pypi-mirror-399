"""TaskFolio CLI styling and theming constants."""

from InquirerPy.utils import get_style

# InquirerPy style dictionary for consistent theming (OneDark palette)
_TASKFOLIO_STYLE_DICT = {
    "questionmark": "#e5c07b bold",  # Yellow bold for branding
    "answermark": "#98c379",  # Green for answers
    "answer": "#61afef",  # Blue for selected
    "input": "#98c379",  # Green for input
    "pointer": "#61afef bold",  # Blue bold pointer
    "fuzzy_match": "#c678dd bold",  # Purple bold matches
    "instruction": "#abb2bf",  # Gray for help text
}

# Create the proper InquirerPy style object
TASKFOLIO_STYLE = get_style(_TASKFOLIO_STYLE_DICT, style_override=False)

# Unicode status icons
STATUS_ICONS = {
    "incomplete": "○",  # Empty circle
    "inProcessing": "◐",  # Half-filled circle
    "complete": "●",  # Filled circle
}

# Message prefixes for styled output
MESSAGE_PREFIXES = {
    "success": "✓",
    "error": "✗",
    "info": "ℹ",
    "warning": "⚠",
}

# ANSI color codes for terminal output
COLORS = {
    "green": "\033[92m",
    "red": "\033[91m",
    "cyan": "\033[96m",
    "yellow": "\033[93m",
    "bold": "\033[1m",
    "reset": "\033[0m",
}


def print_success(message: str) -> None:
    """Print a success message with green styling.

    Args:
        message: Message text to display
    """
    prefix = MESSAGE_PREFIXES["success"]
    print(f"{COLORS['green']}{prefix} {message}{COLORS['reset']}")


def print_error(message: str) -> None:
    """Print an error message with red styling.

    Args:
        message: Message text to display
    """
    prefix = MESSAGE_PREFIXES["error"]
    print(f"{COLORS['red']}{prefix} {message}{COLORS['reset']}")


def print_info(message: str) -> None:
    """Print an info message with cyan styling.

    Args:
        message: Message text to display
    """
    prefix = MESSAGE_PREFIXES["info"]
    print(f"{COLORS['cyan']}{prefix} {message}{COLORS['reset']}")


def print_header(username: str) -> None:
    """Print the TaskFolio header with professional ASCII art branding.

    Args:
        username: Current user's name for display
    """
    cyan = "\033[96m"
    bold = "\033[1m"
    reset = "\033[0m"

    # ASCII art logo for TaskFolio - single professional color
#     logo = f"""
# {bold}{cyan}╔═════════════════════════════════════════════════════════════════╗
# ║  ████████╗ █████╗ ███████╗██╗  ██╗███████╗ ██████╗ ██╗     ██╗ ██████╗      ║
# ║  ╚══██╔══╝██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔═══██╗██║     ██║██╔═══██╗     ║
# ║     ██║   ███████║███████╗█████╔╝ █████╗  ██║   ██║██║     ██║██║   ██║     ║
# ║     ██║   ██╔══██║╚════██║██╔═██╗ ██╔══╝  ██║   ██║██║     ██║██║   ██║     ║
# ║     ██║   ██║  ██║███████║██║  ██╗██║     ╚██████╔╝███████╗██║╚██████╔╝     ║
# ║     ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝      ╚═════╝ ╚══════╝╚═╝ ╚═════╝      ║
# ╠═════════════════════════════════════════════════════════════════════════════╣
# ║  Your Personal Task Manager                            User: {username:<6}  ║
# ╚═════════════════════════════════════════════════════════════════════════════╝{reset}"""

    # print(logo)
