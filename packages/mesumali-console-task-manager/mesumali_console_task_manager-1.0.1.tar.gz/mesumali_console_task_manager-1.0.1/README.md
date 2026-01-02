# Console Task Manager

A console-based task management application built with Python.

[![PyPI version](https://badge.fury.io/py/mesumali-console-task-manager.svg)](https://pypi.org/project/mesumali-console-task-manager/)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

### From PyPI (Recommended)

```bash
pip install mesumali-console-task-manager==1.0.0
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

1. When prompted, enter your username (alphanumeric, e.g., "alice"):
   ```
   Welcome to Task Manager!
   Enter your username: alice
   ```

2. The main menu will appear:
   ```
   === Task Manager (alice) ===
   1. Add Task
   2. View All Tasks
   3. Update Task
   4. Delete Task
   5. Change Task Status
   6. Exit

   Enter choice (1-6):
   ```

## Basic Operations

### Add a Task

```
Enter choice (1-6): 1
Enter task title: Buy groceries
Enter task description (optional): Milk, eggs, bread

Task 1 created successfully.
```

### View All Tasks

```
Enter choice (1-6): 2

=== Your Tasks ===
[1] Buy groceries
    Description: Milk, eggs, bread
    Status: incomplete
---
```

### Update a Task

```
Enter choice (1-6): 3
Enter task ID to update: 1
Enter new title (press Enter to keep current): Get groceries
Enter new description (press Enter to keep current):

Task 1 updated successfully.
```

### Delete a Task

```
Enter choice (1-6): 4
Enter task ID to delete: 1

Task 1 deleted successfully.
```

### Change Task Status

```
Enter choice (1-6): 5
Enter task ID: 1
Select new status:
  1. incomplete
  2. inProcessing
  3. complete
Enter choice (1-3): 3

Task 1 marked as complete.
```

### Exit

```
Enter choice (1-6): 6

Goodbye!
```

## Data Storage

Your tasks are stored in `db/user_{username}.json`. For example:
- User "alice" -> `db/user_alice.json`
- User "bob" -> `db/user_bob.json`

Tasks persist across sessions. Restart the app and log in with the same username to see your saved tasks.

## Troubleshooting

### "Invalid choice" error
Enter a number 1-6 corresponding to the menu options.

### "Task not found" error
Use "View All Tasks" (option 2) to see valid task IDs.

### "Title cannot be empty" error
Task titles are required. Enter at least one character.

### Data file issues
If `db/user_{username}.json` is corrupted, delete it and restart. A fresh empty task list will be created.

## Running Tests

```bash
uv run pytest
```
