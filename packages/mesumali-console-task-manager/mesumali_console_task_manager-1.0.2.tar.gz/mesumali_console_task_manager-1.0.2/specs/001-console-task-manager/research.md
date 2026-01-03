# Research: Console-based Task Management Application

**Feature**: 001-console-task-manager
**Date**: 2025-12-29

## Overview

This document captures research findings and decisions for implementing the console task manager. All technical context from the plan template was resolved without external clarification needed.

## Decisions Summary

### D-001: Python Version and Package Manager

**Decision**: Python 3.13+ with UV package manager
**Rationale**: Specified in constitution and user requirements. UV provides fast, reliable dependency management.
**Alternatives Considered**:
- pip: Standard but slower, less reproducible
- poetry: More complex than needed for zero-dependency project

### D-002: JSON File Structure

**Decision**: Single JSON file per user containing tasks dict and metadata
```json
{
  "next_id": 4,
  "tasks": {
    "1": {"id": 1, "title": "...", "description": "...", "status": "incomplete"},
    "2": {"id": 2, "title": "...", "description": "...", "status": "complete"}
  }
}
```
**Rationale**:
- Dictionary keyed by ID for O(1) lookup
- `next_id` tracked separately for reliable ID generation
- Simple, human-readable format for debugging
**Alternatives Considered**:
- Array of tasks: Requires O(n) search by ID
- SQLite: Overkill for single-user file storage

### D-003: Task Status Values

**Decision**: String enum with values "incomplete", "inProcessing", "complete"
**Rationale**: Matches spec exactly, human-readable in JSON
**Implementation**: Python Enum class for type safety

### D-004: Atomic File Writes

**Decision**: Write to temp file, then rename
```python
with tempfile.NamedTemporaryFile(mode='w', delete=False, dir=db_dir) as f:
    json.dump(data, f, indent=2)
    temp_path = f.name
os.replace(temp_path, target_path)
```
**Rationale**: `os.replace()` is atomic on POSIX and Windows. Prevents partial writes.
**Alternatives Considered**:
- Direct write: Risk of corruption on crash
- Write + fsync: More complex, overkill for this use case

### D-005: Input Validation Strategy

**Decision**: Validate at service layer, return (success, message) tuples
**Rationale**:
- Keeps CLI layer thin (display only)
- Service layer owns all business rules
- Easy to test validation in isolation
**Validation Rules**:
- Title: Required, non-empty, max 200 chars
- Task ID: Must exist for update/delete/status operations
- Status: Must be one of valid enum values

### D-006: Menu Structure

**Decision**: Numbered menu with 6 options
```
=== Task Manager ===
1. Add Task
2. View All Tasks
3. Update Task
4. Delete Task
5. Change Task Status
6. Exit

Enter choice (1-6):
```
**Rationale**: Simple, intuitive, matches 5 core operations + exit
**Alternatives Considered**:
- Command-based (type "add", "view"): More typing, less discoverable
- Hybrid: Unnecessary complexity

### D-007: Error Message Format

**Decision**: Prefix with "Error:" and include actionable guidance
```
Error: Task with ID 99 not found. Use 'View All Tasks' to see valid IDs.
Error: Title cannot be empty. Please enter a title for the task.
```
**Rationale**: Clear, actionable, helps user recover

### D-008: Username Handling

**Decision**: Prompt for username at startup, use for file naming
```
db/user_{username}.json
```
**Rationale**: Simple user identification, natural data isolation
**Validation**: Username must be non-empty, alphanumeric + underscore only

## Best Practices Applied

### Python Dataclasses

Using `@dataclass` for Task model:
- Automatic `__init__`, `__repr__`, `__eq__`
- Type hints for documentation
- Immutable fields where appropriate

### Standard Library Only

All functionality implemented with Python standard library:
- `json` for serialization
- `os` for file operations
- `tempfile` for atomic writes
- `enum` for status values
- `dataclasses` for models

### Error Handling Pattern

```python
def add_task(self, title: str, description: str = "") -> tuple[bool, str]:
    if not title.strip():
        return False, "Error: Title cannot be empty."
    # ... create task ...
    return True, f"Task {task_id} created successfully."
```

## No Unresolved Items

All technical context has been resolved. No NEEDS CLARIFICATION items remain.
