# Data Model: Console-based Task Management Application

**Feature**: 001-console-task-manager
**Date**: 2025-12-29

## Entities

### Task

Represents a single todo item managed by the user.

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| id | integer | Yes | Positive, unique, immutable | Auto-generated unique identifier |
| title | string | Yes | 1-200 characters, non-empty | Task title/name |
| description | string | No | No limit | Optional detailed description |
| status | TaskStatus | Yes | Enum value | Current completion state |

### TaskStatus (Enum)

| Value | Description |
|-------|-------------|
| incomplete | Task not started (default for new tasks) |
| inProcessing | Task in progress |
| complete | Task finished |

### UserData (Storage Container)

Represents the JSON file structure for a user's tasks.

| Field | Type | Description |
|-------|------|-------------|
| next_id | integer | Next ID to assign (starts at 1) |
| tasks | dict[str, Task] | Tasks keyed by ID string |

## Relationships

```
User (1) ----owns----> (N) Task
     |
     +-- identified by username
     +-- data stored in db/user_{username}.json
```

- Each user has zero or more tasks
- Tasks belong to exactly one user (via file isolation)
- No cross-user task references

## State Transitions

```
                    ┌──────────────┐
                    │  incomplete  │ ◄─── (default on create)
                    └──────┬───────┘
                           │
              mark_status("inProcessing")
                           │
                           ▼
                    ┌──────────────┐
                    │ inProcessing │
                    └──────┬───────┘
                           │
              mark_status("complete")
                           │
                           ▼
                    ┌──────────────┐
                    │   complete   │
                    └──────────────┘

Note: Any status can transition to any other status directly.
      Arrows show typical workflow, not constraints.
```

## Validation Rules

### Task Creation
- `title` must be non-empty after trimming whitespace
- `title` must not exceed 200 characters
- `description` defaults to empty string if not provided
- `status` is set to "incomplete" by default
- `id` is auto-assigned from `next_id`

### Task Update
- Task with given `id` must exist
- New `title` (if provided) must be non-empty
- New `title` (if provided) must not exceed 200 characters
- Fields not provided remain unchanged

### Task Deletion
- Task with given `id` must exist
- Deleted IDs are not reused

### Status Change
- Task with given `id` must exist
- New status must be a valid TaskStatus value

## JSON Schema

### User Data File (`db/user_{username}.json`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["next_id", "tasks"],
  "properties": {
    "next_id": {
      "type": "integer",
      "minimum": 1
    },
    "tasks": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "required": ["id", "title", "description", "status"],
        "properties": {
          "id": { "type": "integer", "minimum": 1 },
          "title": { "type": "string", "minLength": 1, "maxLength": 200 },
          "description": { "type": "string" },
          "status": { "enum": ["incomplete", "inProcessing", "complete"] }
        }
      }
    }
  }
}
```

### Example Data

```json
{
  "next_id": 4,
  "tasks": {
    "1": {
      "id": 1,
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "status": "complete"
    },
    "2": {
      "id": 2,
      "title": "Write report",
      "description": "",
      "status": "inProcessing"
    },
    "3": {
      "id": 3,
      "title": "Call dentist",
      "description": "Schedule appointment for next week",
      "status": "incomplete"
    }
  }
}
```

## Identity & Uniqueness

- Task IDs are unique within a user's file
- Task IDs are positive integers starting from 1
- IDs are assigned sequentially (1, 2, 3, ...)
- Deleted IDs are never reused
- `next_id` is always greater than any existing task ID
