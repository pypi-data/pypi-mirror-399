# Quickstart: TaskFolio Interactive CLI

**Branch**: `002-inquirer-cli` | **Date**: 2025-12-31
**Purpose**: Setup and usage instructions for the InquirerPy-enhanced CLI

## Prerequisites

- Python 3.13+
- UV package manager
- Terminal with Unicode support (recommended)

## Installation

### 1. Clone and Setup

```bash
# Clone repository (if not already)
git clone <repo-url>
cd Phase_01

# Checkout feature branch
git checkout 002-inquirer-cli

# Install dependencies with UV
uv sync
```

### 2. Verify Installation

```bash
# Check InquirerPy is installed
uv run python -c "from InquirerPy import inquirer; print('InquirerPy ready!')"
```

## Running TaskFolio

### Start the Application

```bash
uv run python -m src.main
```

Or using the entry point (if configured):

```bash
uv run taskfolio
```

### First Run Experience

1. **Welcome Screen**: TaskFolio header displays
2. **Username Prompt**: Enter alphanumeric username (letters, numbers, underscores)
3. **Main Menu**: Navigate with arrow keys, press Enter to select

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

## Usage Guide

### Navigation

| Key | Action |
|-----|--------|
| ↑/↓ | Move selection |
| Enter | Confirm selection |
| Type | Filter (in fuzzy lists) |
| Ctrl+C | Exit application |
| Escape | Cancel current operation |

### Adding a Task

1. Select **➕ Add Task**
2. Enter task title (required, max 200 chars)
3. Enter description (optional, press Enter to skip)
4. See confirmation: `✓ Task 1 created successfully.`

### Viewing Tasks

1. Select **📋 View All Tasks**
2. See formatted list:

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

### Updating a Task

1. Select **✏️ Update Task**
2. Search/select task from fuzzy list (type to filter)
3. Enter new title (or press Enter to keep current)
4. Enter new description (or press Enter to keep current)
5. See confirmation: `✓ Task 1 updated successfully.`

### Deleting a Task

1. Select **🗑️ Delete Task**
2. Search/select task from fuzzy list
3. Confirm deletion: `Delete task "Buy groceries"? (y/N)`
4. Press `y` to confirm or `n` to cancel

### Changing Status

1. Select **🔄 Change Status**
2. Search/select task from fuzzy list
3. Select new status:

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

- User data stored in `db/user_{username}.json`
- Existing data from previous CLI version is fully compatible
- Data persists between sessions

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

## Development

### Running Tests

```bash
uv run pytest tests/
```

### Manual Testing Checklist

- [ ] Arrow-key menu navigation works
- [ ] Task title validation shows inline errors
- [ ] Task selection filters on typing
- [ ] Delete confirmation prevents accidents
- [ ] Ctrl+C exits gracefully
- [ ] Existing JSON data loads correctly

## File Structure

```
src/cli/
├── menu.py      # Main menu loop and handlers
├── prompts.py   # Prompt builders and validators
└── styles.py    # Theme and styling constants
```
