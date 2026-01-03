# Data Model: TaskFolio Interactive CLI

**Branch**: `002-inquirer-cli` | **Date**: 2025-12-31
**Purpose**: Define CLI-layer entities for InquirerPy integration

## Overview

This feature only modifies the CLI layer. The existing data models (`Task`, `TaskStatus`) remain unchanged. This document defines new CLI-specific entities for prompt building and display formatting.

---

## Existing Entities (Unchanged)

### Task (from src/models/task.py)

```
Task
├── id: int              # Unique identifier
├── title: str           # Task title (required, max 200 chars)
├── description: str     # Task description (optional)
└── status: TaskStatus   # Current status
```

### TaskStatus (from src/models/task.py)

```
TaskStatus (Enum)
├── INCOMPLETE = "incomplete"
├── IN_PROCESSING = "inProcessing"
└── COMPLETE = "complete"
```

---

## New CLI Entities

### MenuAction

Represents a selectable action in the main menu.

```
MenuAction
├── value: str           # Internal action identifier
├── label: str           # Display text with icon
└── handler: Callable    # Function to execute when selected
```

**Instances**:

| Value | Label | Handler |
|-------|-------|---------|
| "add" | "➕ Add Task" | handle_add_task |
| "view" | "📋 View All Tasks" | handle_view_tasks |
| "update" | "✏️ Update Task" | handle_update_task |
| "delete" | "🗑️ Delete Task" | handle_delete_task |
| "status" | "🔄 Change Status" | handle_change_status |
| "exit" | "👋 Exit" | (breaks loop) |

---

### TaskChoice

Formatted representation of a Task for interactive selection.

```
TaskChoice
├── value: int           # Task ID (returned on selection)
├── name: str            # Display format: "[{id}] {title} - {icon} {status}"
└── enabled: bool        # Always True (no disabled choices)
```

**Display Format**: `"[{id}] {title} - {status_icon} {status}"`

**Example**: `"[1] Buy groceries - ○ incomplete"`

---

### StatusChoice

Represents a status option with visual indicator.

```
StatusChoice
├── value: TaskStatus    # Enum value returned on selection
├── name: str            # Display format: "{icon} {status}"
└── current: bool        # True if this is the task's current status
```

**Options**:

| Value | Name | Icon |
|-------|------|------|
| TaskStatus.INCOMPLETE | "○ incomplete" | ○ |
| TaskStatus.IN_PROCESSING | "◐ inProcessing" | ◐ |
| TaskStatus.COMPLETE | "● complete" | ● |

---

### PromptStyle

Theme configuration for InquirerPy prompts.

```
PromptStyle
├── questionmark: str    # Style for ? prefix
├── answermark: str      # Style for answer indicator
├── answer: str          # Style for selected answer
├── input: str           # Style for user input
├── pointer: str         # Style for selection pointer
├── fuzzy_match: str     # Style for fuzzy match highlights
└── instruction: str     # Style for help text
```

**TaskFolio Theme**:

| Component | Style | Color |
|-----------|-------|-------|
| questionmark | `#e5c07b bold` | Yellow bold |
| answermark | `#98c379` | Green |
| answer | `#61afef` | Blue |
| input | `#98c379` | Green |
| pointer | `#61afef bold` | Blue bold |
| fuzzy_match | `#c678dd bold` | Purple bold |

---

### ValidationResult

Result of input validation (implicit in InquirerPy).

```
ValidationResult
├── valid: bool          # True if input passes validation
└── message: str         # Error message if invalid (from invalid_message param)
```

**Validation Rules**:

| Field | Rule | Error Message |
|-------|------|---------------|
| username | Non-empty, alphanumeric + underscore | "Username must be alphanumeric" |
| title | Non-empty, max 200 chars | "Title required (max 200 chars)" |
| description | (none) | N/A |

---

## Status Icon Mapping

```
STATUS_ICONS: dict[str, str]
├── "incomplete": "○"      # Empty circle
├── "inProcessing": "◐"    # Half-filled circle
└── "complete": "●"        # Filled circle
```

---

## Message Styles

### Success Messages

Format: `"✓ {message}"`
Color: Green

Examples:
- "✓ Task 1 created successfully."
- "✓ Task 1 updated successfully."
- "✓ Task 1 deleted."
- "✓ Task 1 marked as complete."

### Error Messages

Format: `"✗ {message}"`
Color: Red

Examples:
- "✗ Title cannot be empty."
- "✗ Task with ID 99 not found."

### Info Messages

Format: `"ℹ {message}"`
Color: Cyan

Examples:
- "ℹ No tasks found. Add your first task."
- "ℹ Deletion cancelled."

---

## Relationships

```
┌─────────────────┐     ┌─────────────────┐
│   MenuAction    │────>│   TaskManager   │
│   (menu.py)     │     │   (unchanged)   │
└─────────────────┘     └─────────────────┘
        │
        v
┌─────────────────┐     ┌─────────────────┐
│   TaskChoice    │<────│      Task       │
│   (prompts.py)  │     │   (unchanged)   │
└─────────────────┘     └─────────────────┘
        │
        v
┌─────────────────┐     ┌─────────────────┐
│  StatusChoice   │<────│   TaskStatus    │
│   (prompts.py)  │     │   (unchanged)   │
└─────────────────┘     └─────────────────┘
        │
        v
┌─────────────────┐
│   PromptStyle   │
│   (styles.py)   │
└─────────────────┘
```

---

## Module Mapping

| Entity | Module | Notes |
|--------|--------|-------|
| MenuAction | src/cli/menu.py | Defined as dict for InquirerPy Choice |
| TaskChoice | src/cli/prompts.py | Builder function creates from Task |
| StatusChoice | src/cli/prompts.py | Constant list of three options |
| PromptStyle | src/cli/styles.py | Exported as TASKFOLIO_STYLE dict |
| STATUS_ICONS | src/cli/styles.py | Exported constant dict |
