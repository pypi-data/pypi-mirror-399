# CLI Prompts API Contract

**Branch**: `002-inquirer-cli` | **Date**: 2025-12-31
**Purpose**: Define internal API contracts for CLI prompt functions

## Overview

This document defines the internal API for the CLI layer's prompt-building functions. These are not external APIs - they define the contract between `menu.py` (flow control) and `prompts.py` (prompt builders).

---

## Module: `src/cli/prompts.py`

### `build_task_choices(tasks: list[Task]) -> list[Choice]`

Converts a list of Task objects into InquirerPy Choice objects for selection prompts.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| tasks | list[Task] | Yes | List of Task objects from TaskManager |

**Returns**: `list[Choice]`
- Each Choice has `value=task.id` and `name=formatted_string`

**Format**: `"[{id}] {title} - {status_icon} {status}"`

**Example**:
```python
# Input
tasks = [Task(id=1, title="Buy groceries", status=TaskStatus.INCOMPLETE)]

# Output
[Choice(value=1, name="[1] Buy groceries - ○ incomplete")]
```

---

### `build_status_choices(current_status: TaskStatus | None = None) -> list[Choice]`

Creates status option choices with visual indicators.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| current_status | TaskStatus | None | No | Current status to pre-select |

**Returns**: `list[Choice]`
- Three choices for incomplete, inProcessing, complete
- Current status marked with indicator if provided

**Example**:
```python
# Input
current_status = TaskStatus.INCOMPLETE

# Output
[
    Choice(value=TaskStatus.INCOMPLETE, name="○ incomplete (current)"),
    Choice(value=TaskStatus.IN_PROCESSING, name="◐ inProcessing"),
    Choice(value=TaskStatus.COMPLETE, name="● complete"),
]
```

---

### `build_menu_choices() -> list[Choice]`

Creates main menu option choices with icons.

**Parameters**: None

**Returns**: `list[Choice]`
- Six choices for Add, View, Update, Delete, Status, Exit

**Output**:
```python
[
    Choice(value="add", name="➕ Add Task"),
    Choice(value="view", name="📋 View All Tasks"),
    Choice(value="update", name="✏️ Update Task"),
    Choice(value="delete", name="🗑️ Delete Task"),
    Choice(value="status", name="🔄 Change Status"),
    Choice(value="exit", name="👋 Exit"),
]
```

---

### `validate_title(text: str) -> bool`

Validates task title input.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| text | str | Yes | User input text |

**Returns**: `bool`
- `True` if valid (non-empty, <= 200 chars)
- `False` if invalid

**Rules**:
1. Must not be empty after stripping whitespace
2. Must be <= 200 characters

---

### `validate_username(text: str) -> bool`

Validates username input.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| text | str | Yes | User input text |

**Returns**: `bool`
- `True` if valid (non-empty, alphanumeric + underscore)
- `False` if invalid

**Rules**:
1. Must not be empty
2. Must match pattern `^[a-zA-Z0-9_]+$`

---

### `format_task_display(task: Task) -> str`

Formats a task for display in view mode (not selection).

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| task | Task | Yes | Task object to format |

**Returns**: `str`
- Multi-line formatted string

**Format**:
```
[{id}] {title}
    Description: {description or "(none)"}
    Status: {status_icon} {status}
---
```

---

## Module: `src/cli/styles.py`

### Constants

#### `TASKFOLIO_STYLE: dict[str, str]`

InquirerPy style dictionary for consistent theming.

```python
TASKFOLIO_STYLE = {
    "questionmark": "#e5c07b bold",
    "answermark": "#98c379",
    "answer": "#61afef",
    "input": "#98c379",
    "pointer": "#61afef bold",
    "fuzzy_match": "#c678dd bold",
    "instruction": "#abb2bf",
}
```

#### `STATUS_ICONS: dict[str, str]`

Mapping of status values to Unicode icons.

```python
STATUS_ICONS = {
    "incomplete": "○",
    "inProcessing": "◐",
    "complete": "●",
}
```

#### `MESSAGE_PREFIXES: dict[str, str]`

Prefixes for styled messages.

```python
MESSAGE_PREFIXES = {
    "success": "✓",
    "error": "✗",
    "info": "ℹ",
    "warning": "⚠",
}
```

---

### `print_success(message: str) -> None`

Prints a success message with green styling.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| message | str | Yes | Message text |

**Output**: `"✓ {message}"` in green

---

### `print_error(message: str) -> None`

Prints an error message with red styling.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| message | str | Yes | Message text |

**Output**: `"✗ {message}"` in red

---

### `print_info(message: str) -> None`

Prints an info message with cyan styling.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| message | str | Yes | Message text |

**Output**: `"ℹ {message}"` in cyan

---

### `print_header(username: str) -> None`

Prints the TaskFolio header with branding.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| username | str | Yes | Current user's name |

**Output**:
```
╔════════════════════════════════════╗
║     TaskFolio ({username})         ║
╚════════════════════════════════════╝
```

---

## Module: `src/cli/menu.py`

### `prompt_main_menu() -> str`

Displays main menu and returns selected action.

**Parameters**: None

**Returns**: `str` - One of: "add", "view", "update", "delete", "status", "exit"

**Behavior**:
- Uses `inquirer.select()` with arrow navigation
- Applies TASKFOLIO_STYLE
- Returns action value (not display name)

---

### `prompt_username() -> str`

Prompts for and validates username.

**Parameters**: None

**Returns**: `str` - Validated username

**Behavior**:
- Uses `inquirer.text()` with validation
- Shows inline error for invalid input
- Loops until valid input provided

---

### `prompt_task_title() -> str`

Prompts for and validates task title.

**Parameters**: None

**Returns**: `str` - Validated title

**Behavior**:
- Uses `inquirer.text()` with validation
- Shows inline error for empty or too-long input

---

### `prompt_task_description() -> str`

Prompts for optional task description.

**Parameters**: None

**Returns**: `str` - Description (may be empty)

**Behavior**:
- Uses `inquirer.text()` without validation
- Empty input is allowed

---

### `prompt_select_task(tasks: list[Task], message: str) -> int | None`

Prompts user to select a task from list.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| tasks | list[Task] | Yes | Available tasks |
| message | str | Yes | Prompt message |

**Returns**: `int | None`
- Task ID if selected
- `None` if no tasks available

**Behavior**:
- Returns `None` immediately if tasks empty (prints info message)
- Uses `inquirer.fuzzy()` for searchable selection
- Returns task ID (int), not Task object

---

### `prompt_select_status(current: TaskStatus) -> TaskStatus`

Prompts user to select a status.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| current | TaskStatus | Yes | Current task status |

**Returns**: `TaskStatus` - Selected status enum value

**Behavior**:
- Uses `inquirer.select()` with status icons
- Pre-selects current status

---

### `prompt_confirm_delete(task_title: str) -> bool`

Prompts for delete confirmation.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| task_title | str | Yes | Title of task to delete |

**Returns**: `bool`
- `True` if confirmed
- `False` if cancelled

**Behavior**:
- Uses `inquirer.confirm()` with default=False
- Shows task title in message

---

## Error Handling

### KeyboardInterrupt

All prompt functions may raise `KeyboardInterrupt` on Ctrl+C.

**Expected Behavior**: Caller (`run_menu()`) catches at top level and exits gracefully.

### Empty Input

- Title prompt: Validation rejects, shows error, re-prompts
- Description prompt: Accepts empty string
- Username prompt: Validation rejects, shows error, re-prompts

### Invalid Selection

Not possible with InquirerPy - user can only select from provided choices.
