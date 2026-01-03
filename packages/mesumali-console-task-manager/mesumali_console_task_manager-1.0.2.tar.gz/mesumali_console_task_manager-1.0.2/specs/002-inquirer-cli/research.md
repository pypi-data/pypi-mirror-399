# Research: TaskFolio Interactive CLI with InquirerPy

**Branch**: `002-inquirer-cli` | **Date**: 2025-12-31
**Purpose**: Resolve technical unknowns and document best practices for InquirerPy integration

## Research Summary

| Topic | Decision | Source |
|-------|----------|--------|
| Library Choice | InquirerPy | Official docs, PyPI |
| Syntax Style | Alternate (inquirer.X) | Cleaner, more Pythonic |
| Validation | Lambda + invalid_message | InquirerPy validator docs |
| Styling | Custom style dict | InquirerPy style docs |
| Task Selection | fuzzy prompt | Best for searchable lists |

---

## 1. InquirerPy Library Overview

### Decision: Use InquirerPy

**Rationale**: Most feature-complete Python port of Inquirer.js with active maintenance

**Alternatives Considered**:

| Library | Pros | Cons | Verdict |
|---------|------|------|---------|
| InquirerPy | Full feature set, Python 3.10+ support, fuzzy search | Additional dependency | SELECTED |
| questionary | Simple API | Less active, fewer prompt types | REJECTED |
| PyInquirer | Original Python port | Deprecated, no Python 3.10+ | REJECTED |
| rich | Beautiful output | No interactive prompts | REJECTED (output only) |

**Installation**:
```bash
uv add inquirerpy
```

---

## 2. API Syntax Choice

### Decision: Use Alternate Syntax (`inquirer.X().execute()`)

**Rationale**: More concise, Pythonic, direct method chaining

**Classic Syntax** (PyInquirer-compatible):
```python
from InquirerPy import prompt

questions = [{"type": "list", "message": "Select:", "choices": [...]}]
result = prompt(questions)
```

**Alternate Syntax** (Selected):
```python
from InquirerPy import inquirer

result = inquirer.select(
    message="Select:",
    choices=[...]
).execute()
```

**Benefits of Alternate Syntax**:
- Single prompt per call (clearer flow)
- IDE autocomplete for parameters
- Easier error handling per prompt
- No need for question names/indices

---

## 3. Prompt Type Mapping

### Research Findings

| Use Case | Prompt Type | Key Parameters |
|----------|-------------|----------------|
| Main menu | `inquirer.select()` | message, choices |
| Username input | `inquirer.text()` | message, validate, invalid_message |
| Task title | `inquirer.text()` | message, validate, invalid_message |
| Task description | `inquirer.text()` | message (no validation) |
| Task selection | `inquirer.fuzzy()` | message, choices, match_exact=False |
| Status selection | `inquirer.select()` | message, choices, default |
| Delete confirmation | `inquirer.confirm()` | message, default=False |

### Select Prompt Example
```python
from InquirerPy import inquirer

result = inquirer.select(
    message="What would you like to do?",
    choices=["Add Task", "View Tasks", "Update Task", "Delete Task", "Change Status", "Exit"]
).execute()
```

### Fuzzy Prompt Example
```python
from InquirerPy import inquirer

result = inquirer.fuzzy(
    message="Select a task:",
    choices=["[1] Buy groceries - incomplete", "[2] Call mom - complete"],
    match_exact=False
).execute()
```

### Confirm Prompt Example
```python
from InquirerPy import inquirer

result = inquirer.confirm(
    message="Delete task 'Buy groceries'?",
    default=False
).execute()
```

---

## 4. Input Validation

### Decision: Use lambda validators with invalid_message

**Rationale**: Simple, inline, readable validation for text inputs

### Title Validation Pattern
```python
from InquirerPy import inquirer

MAX_TITLE_LENGTH = 200

title = inquirer.text(
    message="Enter task title:",
    validate=lambda x: len(x.strip()) > 0 and len(x) <= MAX_TITLE_LENGTH,
    invalid_message=f"Title required (max {MAX_TITLE_LENGTH} characters)"
).execute()
```

### Username Validation Pattern
```python
import re
from InquirerPy import inquirer

username = inquirer.text(
    message="Enter your username:",
    validate=lambda x: bool(re.match(r"^[a-zA-Z0-9_]+$", x)) and len(x) > 0,
    invalid_message="Username must be alphanumeric (letters, numbers, underscores only)"
).execute()
```

**Key Finding**: Validation errors appear inline below the input field without clearing the screen.

---

## 5. Styling and Theming

### Decision: Custom style dict based on default theme

**Default Theme Reference** (OneDark palette):
```python
DEFAULT_STYLE = {
    "questionmark": "#e5c07b",      # Yellow
    "answermark": "#e5c07b",
    "answer": "#61afef",            # Blue
    "input": "#98c379",             # Green
    "question": "",
    "instruction": "#abb2bf",       # Gray
    "pointer": "#61afef",           # Blue
    "checkbox": "#98c379",          # Green
    "fuzzy_prompt": "#c678dd",      # Purple
    "fuzzy_match": "#c678dd",       # Purple
}
```

### TaskFolio Custom Style
```python
TASKFOLIO_STYLE = {
    "questionmark": "#e5c07b bold",     # Yellow bold for branding
    "answermark": "#98c379",            # Green for answers
    "answer": "#61afef",                # Blue for selected
    "input": "#98c379",                 # Green for input
    "pointer": "#61afef bold",          # Blue bold pointer
    "fuzzy_match": "#c678dd bold",      # Purple bold matches
}
```

### Applying Style
```python
from InquirerPy import inquirer

result = inquirer.select(
    message="Select action:",
    choices=["Option 1", "Option 2"],
    style=TASKFOLIO_STYLE
).execute()
```

---

## 6. Choice Objects with Values

### Decision: Use Choice class for task selection

**Rationale**: Separates display text from return value (task ID)

```python
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

# Task choices with ID as value, formatted string as name
choices = [
    Choice(value=1, name="[1] Buy groceries - ○ incomplete"),
    Choice(value=2, name="[2] Call mom - ● complete"),
    Choice(value=3, name="[3] Write report - ◐ inProcessing"),
]

task_id = inquirer.fuzzy(
    message="Select a task:",
    choices=choices
).execute()
# Returns: 1, 2, or 3 (the task ID)
```

---

## 7. Keyboard Interrupt Handling

### Decision: Wrap menu loop in try/except

**Pattern**:
```python
from InquirerPy import inquirer

def run_menu():
    try:
        while True:
            action = inquirer.select(
                message="What would you like to do?",
                choices=[...]
            ).execute()

            if action == "Exit":
                break
            # ... handle action
    except KeyboardInterrupt:
        pass
    finally:
        print("\nGoodbye from TaskFolio!")
```

**Key Finding**: InquirerPy raises `KeyboardInterrupt` on Ctrl+C, which can be caught cleanly.

---

## 8. Status Icons

### Decision: Unicode circle icons for status

| Status | Icon | Rationale |
|--------|------|-----------|
| incomplete | ○ | Empty circle = not done |
| inProcessing | ◐ | Half-filled = in progress |
| complete | ● | Filled circle = done |

**Implementation**:
```python
STATUS_ICONS = {
    "incomplete": "○",
    "inProcessing": "◐",
    "complete": "●",
}

def format_task_choice(task):
    icon = STATUS_ICONS[task.status.value]
    return f"[{task.id}] {task.title} - {icon} {task.status.value}"
```

---

## 9. Empty State Handling

### Decision: Check task count before showing selectors

**Pattern**:
```python
from InquirerPy import inquirer

def select_task(manager, message):
    tasks = manager.get_all_tasks()

    if not tasks:
        print("\n⚠ No tasks found. Add a task first.")
        return None

    choices = [Choice(value=t.id, name=format_task_choice(t)) for t in tasks]

    return inquirer.fuzzy(
        message=message,
        choices=choices
    ).execute()
```

---

## 10. Terminal Compatibility

### Findings

- **Color Support**: InquirerPy uses prompt_toolkit which auto-detects terminal capabilities
- **Fallback**: Falls back to plain text in non-color terminals
- **Unicode**: Status icons (○, ◐, ●) work in most modern terminals
- **Windows**: Full support via Windows Terminal, limited in legacy cmd.exe

**No action needed**: InquirerPy handles compatibility automatically.

---

## Dependencies Summary

**Required**:
```toml
[project.dependencies]
inquirerpy = ">=0.3.4"
```

**Transitive** (auto-installed):
- prompt_toolkit >= 3.0.0
- pfzy >= 0.3.1 (for fuzzy matching)

---

## References

1. InquirerPy Documentation: https://inquirerpy.readthedocs.io/
2. InquirerPy GitHub: https://github.com/kazhala/InquirerPy
3. Context7 Documentation Snippets (164 examples)
