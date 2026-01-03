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

```bash
pip install mesumali-console-task-manager
```

After installation, run:

```bash
mesumali-todo --help
```

```
╔══════════════════════════════════════════════════════════════════════════╗
║  ████████╗ █████╗ ███████╗██╗  ██╗███████╗ ██████╗ ██╗     ██╗ ██████╗   ║
║  ╚══██╔══╝██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔═══██╗██║     ██║██╔═══██╗  ║
║     ██║   ███████║███████╗█████╔╝ █████╗  ██║   ██║██║     ██║██║   ██║  ║
║     ██║   ██╔══██║╚════██║██╔═██╗ ██╔══╝  ██║   ██║██║     ██║██║   ██║  ║
║     ██║   ██║  ██║███████║██║  ██╗██║     ╚██████╔╝███████╗██║╚██████╔╝  ║
║     ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝      ╚═════╝ ╚══════╝╚═╝ ╚═════╝   ║
╠══════════════════════════════════════════════════════════════════════════╣
║  TaskFolio v1.0.3 - Your Personal Interactive Task Manager               ║
╚══════════════════════════════════════════════════════════════════════════╝

Usage:  mesumali-todo [options]

Options:
  --help, -h      Show this help message
  --version, -v   Show version number

Features:
  - Arrow-key menu navigation
  - Fuzzy search for tasks
  - Visual status indicators
  - Delete confirmation

Run without options to start the interactive task manager.
```

## Quick Start

```bash
mesumali-todo
```

Interactive task manager with arrow-key navigation and fuzzy search.

### From Source

```bash
git clone <repository-url>
cd Phase_01
uv sync
uv run python -m src.main
```

## Usage

Navigate the menu using arrow keys and press Enter to select:

```
? What would you like to do?
> [1] Add Task
  [2] View All Tasks
  [3] Update Task
  [4] Delete Task
  [5] Change Status
  [6] Exit
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

1. Select **[1] Add Task**
2. Enter task title (required, max 200 chars)
3. Enter description (optional)

### View All Tasks

Select **[2] View All Tasks** to see your tasks with status icons.

### Update a Task

1. Select **[3] Update Task**
2. Search/select task from fuzzy list
3. Enter new title or description

### Delete a Task

1. Select **[4] Delete Task**
2. Search/select task from fuzzy list
3. Confirm deletion (y/N)

### Change Task Status

1. Select **[5] Change Status**
2. Search/select task from fuzzy list
3. Select new status:
   ```
   > ○ incomplete
     ◐ inProcessing
     ● complete
   ```

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
