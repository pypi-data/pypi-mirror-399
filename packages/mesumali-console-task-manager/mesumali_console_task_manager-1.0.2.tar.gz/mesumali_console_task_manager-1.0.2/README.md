# TaskFolio - Interactive Task Manager

A modern, interactive console-based task management application built with Python and InquirerPy.

[![PyPI version](https://badge.fury.io/py/mesumali-console-task-manager.svg)](https://pypi.org/project/mesumali-console-task-manager/)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Arrow-key navigation** - Navigate menus with arrow keys instead of typing numbers
- **Fuzzy search** - Type to filter tasks in selection lists
- **Visual feedback** - Colored output with status icons
- **Inline validation** - Immediate feedback for invalid input
- **Delete confirmation** - Prevent accidental deletions

## Installation

### From PyPI (Recommended)

```bash
pip install mesumali-console-task-manager
```

### From Source

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Phase_01
   ```

2. Install dependencies with UV:
   ```bash
   uv sync
   ```

## Running the Application

### If installed via pip:

```bash
mesumali-todo
```

### If installed from source:

```bash
uv run python -m src.main
```

## First Run

1. When prompted, enter your username (alphanumeric):
   ```
   Welcome to TaskFolio!
   ? Enter your username: alice
   ```

2. The main menu will appear with arrow-key navigation:
   ```
   ╔════════════════════════════════════╗
   ║     TaskFolio (alice)              ║
   ╚════════════════════════════════════╝

   ? What would you like to do?
   ❯ ➕ Add Task
     📋 View All Tasks
     ✏️ Update Task
     🗑️ Delete Task
     🔄 Change Status
     👋 Exit
   ```

## Keyboard Navigation

| Key | Action |
|-----|--------|
| ↑/↓ | Move selection |
| Enter | Confirm selection |
| Type | Filter (in fuzzy lists) |
| Ctrl+C | Exit application |

## Basic Operations

### Add a Task

1. Select **➕ Add Task**
2. Enter task title (required, max 200 chars)
3. Enter description (optional, press Enter to skip)
4. See confirmation: `✓ Task 1 created successfully.`

### View All Tasks

Select **📋 View All Tasks** to see:

```
=== Your Tasks ===
[1] Buy groceries
    Description: Milk, eggs, bread
    Status: ○ incomplete
---
[2] Call mom
    Description: (none)
    Status: ● complete
---
```

### Update a Task

1. Select **✏️ Update Task**
2. Search/select task from fuzzy list (type to filter)
3. Enter new title (or press Enter to keep current)
4. Enter new description (or press Enter to keep current)
5. See confirmation: `✓ Task 1 updated successfully.`

### Delete a Task

1. Select **🗑️ Delete Task**
2. Search/select task from fuzzy list
3. Confirm deletion: `Delete task "Buy groceries"? (y/N)`
4. Press `y` to confirm or `n` to cancel

### Change Task Status

1. Select **🔄 Change Status**
2. Search/select task from fuzzy list
3. Select new status from visual menu:
   ```
   ? Select new status:
   ❯ ○ incomplete
     ◐ inProcessing
     ● complete
   ```
4. See confirmation: `✓ Task 1 marked as complete.`

## Status Icons

| Icon | Status | Meaning |
|------|--------|---------|
| ○ | incomplete | Task not started |
| ◐ | inProcessing | Task in progress |
| ● | complete | Task finished |

## Data Storage

Your tasks are stored in `db/user_{username}.json`. For example:
- User "alice" -> `db/user_alice.json`
- User "bob" -> `db/user_bob.json`

Tasks persist across sessions. Restart the app and log in with the same username to see your saved tasks.

## Troubleshooting

### Unicode Icons Not Displaying

**Symptom**: Status icons show as boxes or question marks

**Solution**: Use a modern terminal:
- Windows: Windows Terminal, VS Code terminal
- macOS: Default Terminal.app, iTerm2
- Linux: GNOME Terminal, Konsole

### Colors Not Showing

**Symptom**: All text is plain/white

**Solution**: InquirerPy auto-detects color support. If not working:
1. Check terminal supports ANSI colors
2. Set `TERM=xterm-256color` environment variable

### Keyboard Navigation Not Working

**Symptom**: Arrow keys print characters instead of navigating

**Solution**: Ensure terminal is in canonical mode. Try:
- Restart terminal
- Use `stty sane` to reset terminal settings

### Data file issues

If `db/user_{username}.json` is corrupted, delete it and restart. A fresh empty task list will be created.

## Running Tests

```bash
uv run pytest
```
