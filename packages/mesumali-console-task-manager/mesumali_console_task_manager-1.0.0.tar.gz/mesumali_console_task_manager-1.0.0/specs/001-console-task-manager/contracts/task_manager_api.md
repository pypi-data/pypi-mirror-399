# Internal API Contract: TaskManager Service

**Feature**: 001-console-task-manager
**Date**: 2025-12-29

## Overview

This document defines the internal API contract for the `TaskManager` service class. This is not a REST API but an internal Python class interface used by the CLI layer.

## Class: TaskManager

### Constructor

```python
TaskManager(storage: JsonStorage, username: str)
```

**Parameters:**
- `storage`: JsonStorage instance for persistence
- `username`: String identifier for the user

**Behavior:**
- Loads existing tasks from storage on initialization
- Creates empty task store if no existing data

---

## Methods

### add_task

```python
def add_task(self, title: str, description: str = "") -> tuple[bool, str]
```

**Parameters:**
- `title`: Task title (required)
- `description`: Task description (optional, defaults to "")

**Returns:** `(success: bool, message: str)`

**Success Response:**
```python
(True, "Task 1 created successfully.")
```

**Error Responses:**
```python
(False, "Error: Title cannot be empty.")
(False, "Error: Title exceeds 200 characters.")
```

**Behavior:**
- Validates title is non-empty
- Validates title length <= 200
- Assigns next available ID
- Sets status to "incomplete"
- Persists to storage

---

### get_all_tasks

```python
def get_all_tasks(self) -> list[Task]
```

**Returns:** List of Task objects (may be empty)

**Behavior:**
- Returns all tasks for current user
- Order: by ID ascending

---

### update_task

```python
def update_task(
    self,
    task_id: int,
    title: str | None = None,
    description: str | None = None
) -> tuple[bool, str]
```

**Parameters:**
- `task_id`: ID of task to update
- `title`: New title (optional, None = no change)
- `description`: New description (optional, None = no change)

**Returns:** `(success: bool, message: str)`

**Success Response:**
```python
(True, "Task 1 updated successfully.")
```

**Error Responses:**
```python
(False, "Error: Task with ID 99 not found.")
(False, "Error: Title cannot be empty.")
(False, "Error: Title exceeds 200 characters.")
```

**Behavior:**
- Validates task exists
- Validates new title if provided
- Updates only provided fields
- Persists to storage

---

### delete_task

```python
def delete_task(self, task_id: int) -> tuple[bool, str]
```

**Parameters:**
- `task_id`: ID of task to delete

**Returns:** `(success: bool, message: str)`

**Success Response:**
```python
(True, "Task 1 deleted successfully.")
```

**Error Responses:**
```python
(False, "Error: Task with ID 99 not found.")
```

**Behavior:**
- Validates task exists
- Removes task from storage
- Persists to storage
- ID is not reused

---

### set_status

```python
def set_status(self, task_id: int, status: TaskStatus) -> tuple[bool, str]
```

**Parameters:**
- `task_id`: ID of task to update
- `status`: New status (TaskStatus enum value)

**Returns:** `(success: bool, message: str)`

**Success Response:**
```python
(True, "Task 1 marked as complete.")
```

**Error Responses:**
```python
(False, "Error: Task with ID 99 not found.")
(False, "Error: Invalid status. Choose: incomplete, inProcessing, complete.")
```

**Behavior:**
- Validates task exists
- Validates status is valid enum value
- Updates task status
- Persists to storage

---

## Class: JsonStorage

### Constructor

```python
JsonStorage(db_dir: str, username: str)
```

**Parameters:**
- `db_dir`: Directory path for JSON files (e.g., "db/")
- `username`: Username for file naming

**Behavior:**
- Creates `db_dir` if it doesn't exist
- File path: `{db_dir}/user_{username}.json`

---

### load

```python
def load(self) -> dict
```

**Returns:** Dictionary with `next_id` and `tasks`

**Behavior:**
- Returns existing data if file exists
- Returns `{"next_id": 1, "tasks": {}}` if file doesn't exist
- Handles corrupt JSON gracefully (returns empty data, logs warning)

---

### save

```python
def save(self, data: dict) -> None
```

**Parameters:**
- `data`: Dictionary with `next_id` and `tasks`

**Behavior:**
- Writes to temp file first
- Atomically renames to target path
- Raises exception only on unrecoverable I/O error
