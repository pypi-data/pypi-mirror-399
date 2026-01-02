# Implementation Plan: Console-based Task Management Application

**Branch**: `001-console-task-manager` | **Date**: 2025-12-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-console-task-manager/spec.md`

## Summary

Build a Python console application that provides 5 core task management operations (Add, View, Update, Delete, Mark Status) through an interactive menu loop. Tasks are persisted to JSON files in `db/` directory with per-user data isolation. The application follows clean code principles with clear separation between models, services, storage, and CLI layers.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: None (standard library only)
**Storage**: JSON files in `db/` directory (per-user files, e.g., `db/user_alice.json`)
**Testing**: pytest (manual validation for MVP, automated tests optional)
**Target Platform**: Cross-platform CLI (Linux, macOS, Windows terminal)
**Project Type**: Single project
**Performance Goals**: Application startup < 2 seconds, operations < 1 second
**Constraints**: No external dependencies, standard library preferred
**Scale/Scope**: Single user per session, hundreds of tasks per user

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Simplicity First | PASS | 5 core operations only, no unnecessary abstractions |
| II. User Data Isolation | PASS | Per-user JSON files in `db/` directory |
| III. Stateless CLI Operations | PASS | Each menu selection reads JSON, performs op, writes back |
| IV. Test-First Development | PASS | Manual validation defined, pytest available for TDD |
| V. Clear CLI Interface | PASS | Interactive menu with numbered options, help text |
| VI. Data Integrity | PASS | Atomic writes (temp file + rename), unique IDs |

**All gates passed. Proceeding to Phase 0.**

## Project Structure

### Documentation (this feature)

```text
specs/001-console-task-manager/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (internal API contracts)
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── main.py              # Entry point, menu loop
├── models/
│   ├── __init__.py
│   └── task.py          # Task dataclass
├── services/
│   ├── __init__.py
│   └── task_manager.py  # CRUD operations
├── storage/
│   ├── __init__.py
│   └── json_storage.py  # JSON file I/O with atomic writes
└── cli/
    ├── __init__.py
    └── menu.py          # Menu display and input handling

db/                      # User JSON files (created at runtime)

tests/
├── __init__.py
├── unit/
│   ├── test_task.py
│   └── test_task_manager.py
└── integration/
    └── test_cli.py

pyproject.toml           # UV project configuration
README.md                # Setup and usage instructions
```

**Structure Decision**: Single project structure selected. Clear separation of concerns:
- `models/` - Data structures (Task)
- `services/` - Business logic (TaskManager)
- `storage/` - Persistence layer (JSON I/O)
- `cli/` - User interface (menu loop)

## Architecture Decisions

### AD-001: Task ID Generation Strategy

**Decision**: Incremental counter stored in JSON file
**Rationale**: Simple, predictable, human-readable IDs (1, 2, 3...)
**Alternatives Rejected**:
- UUID: Overkill for single-user app, harder to type
- Timestamp: Not guaranteed unique within same second

### AD-002: Data Structure for Tasks

**Decision**: Dictionary keyed by task ID (stored as JSON object)
**Rationale**: O(1) lookup by ID, natural for JSON serialization
**Alternatives Rejected**:
- List: O(n) lookup by ID, index != ID after deletions

### AD-003: Separation of Concerns

**Decision**: 4-layer architecture (CLI → Service → Storage → Model)
**Rationale**: Each layer has single responsibility, testable in isolation
- CLI: Input/output only, no business logic
- Service: Business rules, validation
- Storage: File I/O only
- Model: Data structure definition

### AD-004: Error Handling Approach

**Decision**: Return error messages as strings, display in CLI layer
**Rationale**: Keep service layer pure, CLI handles user feedback
**Pattern**: Service methods return `(success: bool, message: str)` tuples

### AD-005: File Layout

**Decision**: Modular package structure under `src/`
**Rationale**: Clear organization, supports future growth, follows Python conventions

## Complexity Tracking

> No violations. All design choices align with Constitution principles.

| Principle | Design Choice | Justification |
|-----------|--------------|---------------|
| Simplicity First | 4 modules only | Minimum needed for separation of concerns |
| Data Integrity | Atomic writes | Write temp file, rename to target |
| Stateless | Read-modify-write per operation | JSON is always current state |

## Implementation Phases

### Phase 1: Foundation

- Initialize UV project with `pyproject.toml`
- Create directory structure (`src/`, `db/`, `tests/`)
- Create `README.md` with setup instructions
- Create entry point `src/main.py` with placeholder

### Phase 2: Core Model

- Implement `Task` dataclass in `src/models/task.py`
- Fields: id, title, description, status
- Status enum: incomplete, inProcessing, complete

### Phase 3: Storage Layer

- Implement `JsonStorage` in `src/storage/json_storage.py`
- Methods: load_tasks, save_tasks
- Atomic write: write to temp, rename to target
- Handle missing/corrupt file gracefully

### Phase 4: Service Layer

- Implement `TaskManager` in `src/services/task_manager.py`
- Methods: add_task, get_all_tasks, update_task, delete_task, set_status
- ID generation: track next_id in JSON
- Validation: title required, ID exists checks

### Phase 5: CLI Layer

- Implement menu loop in `src/cli/menu.py`
- Display numbered options (1-6 for operations + exit)
- Handle input, call service, display results
- Clear error messages for invalid input

### Phase 6: Integration

- Wire all layers together in `src/main.py`
- Request username at startup
- Load/create user JSON file
- Run menu loop until exit

### Phase 7: Validation

- Manual testing of all 5 operations
- Edge cases: invalid ID, empty title, missing file
- Verify persistence across restarts

## Acceptance Checks

| Check | Verification Method |
|-------|---------------------|
| Add task creates new entry | Add task, view list, confirm appears |
| View shows all tasks | Add multiple, view, confirm all displayed |
| Update modifies fields | Update task, view, confirm changes |
| Delete removes task | Delete task, view, confirm gone |
| Status change persists | Change status, restart, confirm status |
| Invalid ID shows error | Enter non-existent ID, confirm error message |
| Empty title rejected | Try adding empty title, confirm error |
| Data survives restart | Add tasks, exit, restart, confirm tasks exist |
