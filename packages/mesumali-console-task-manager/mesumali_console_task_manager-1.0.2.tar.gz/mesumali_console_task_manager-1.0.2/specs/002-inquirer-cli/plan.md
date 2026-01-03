# Implementation Plan: TaskFolio Interactive CLI with InquirerPy

**Branch**: `002-inquirer-cli` | **Date**: 2025-12-31 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-inquirer-cli/spec.md`

## Summary

Refactor the TaskFolio CLI layer to use InquirerPy for interactive prompts, replacing basic `input()` calls with arrow-key navigable menus, fuzzy-searchable task selection lists, styled output with colors, and confirmation dialogs. The existing models, services, and storage layers remain unchanged - only `src/cli/` is modified.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: InquirerPy (interactive prompts), prompt_toolkit (InquirerPy dependency)
**Storage**: JSON files in `db/` directory (unchanged from existing implementation)
**Testing**: pytest with manual CLI validation
**Target Platform**: Cross-platform CLI (Linux, macOS, Windows terminal)
**Project Type**: Single project (existing structure)
**Performance Goals**: Menu display < 100ms, input response < 50ms
**Constraints**: Must maintain backwards compatibility with existing JSON data format
**Scale/Scope**: Single user per session, hundreds of tasks per user

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Simplicity First | PASS | Only CLI layer changes; models/services/storage untouched |
| II. User Data Isolation | PASS | No changes to storage layer - per-user JSON files preserved |
| III. Stateless CLI Operations | PASS | Each menu action reads JSON, performs op, writes back |
| IV. Test-First Development | PASS | Manual validation defined; pytest available for unit tests |
| V. Clear CLI Interface | PASS | InquirerPy provides intuitive arrow-key navigation, help text |
| VI. Data Integrity | PASS | No changes to atomic write logic in storage layer |

**All gates passed. Proceeding to Phase 0.**

## Project Structure

### Documentation (this feature)

```text
specs/002-inquirer-cli/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (CLI entities)
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (prompt definitions)
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── main.py              # Entry point (minor updates for branding)
├── models/
│   ├── __init__.py
│   └── task.py          # Unchanged
├── services/
│   ├── __init__.py
│   └── task_manager.py  # Unchanged
├── storage/
│   ├── __init__.py
│   └── json_storage.py  # Unchanged
└── cli/
    ├── __init__.py
    ├── menu.py          # REFACTOR: InquirerPy main menu and handlers
    ├── prompts.py       # NEW: Reusable prompt builders
    └── styles.py        # NEW: Custom theme and color definitions

db/                      # User JSON files (unchanged)

tests/
├── __init__.py
├── unit/
│   ├── test_task.py
│   └── test_task_manager.py
└── integration/
    └── test_cli.py      # UPDATE: Add InquirerPy prompt tests

pyproject.toml           # UPDATE: Add InquirerPy dependency
```

**Structure Decision**: Extend existing single project structure. Add two new modules in `src/cli/` for prompt builders and styles. No changes to models, services, or storage.

## Architecture Decisions

### AD-001: Interactive Prompt Library Choice

**Decision**: Use InquirerPy
**Rationale**: Most feature-complete Python port of Inquirer.js with excellent documentation
**Alternatives Rejected**:
- questionary: Less active maintenance, fewer prompt types
- PyInquirer: Deprecated, no Python 3.10+ support
- rich: Output formatting only, no interactive prompts

### AD-002: Prompt Type Mapping

**Decision**: Map each UI interaction to optimal InquirerPy prompt type

| Interaction | Prompt Type | Rationale |
|-------------|-------------|-----------|
| Main menu | `select` | Arrow navigation, visual highlight |
| Username input | `text` with validate | Inline error, regex validation |
| Task title input | `text` with validate | Required field, max length check |
| Description input | `text` | Optional, no validation needed |
| Task selection | `fuzzy` | Searchable list, handles many items |
| Status selection | `select` | Three fixed options with icons |
| Delete confirmation | `confirm` | Standard yes/no with default No |

### AD-003: Styling Strategy

**Decision**: Use InquirerPy's built-in theming with custom style dict
**Rationale**: Consistent look across all prompts without external dependencies
**Implementation**:
- Green: Success messages, complete status
- Red: Error messages, delete operations
- Yellow: Warning, inProcessing status
- Cyan: Info, task IDs
- Bold: Headers, important text

### AD-004: Error Handling for Keyboard Interrupts

**Decision**: Catch `KeyboardInterrupt` at menu loop level, display goodbye message
**Rationale**: Graceful exit is expected UX for CLI applications
**Pattern**: Wrap entire menu loop in try/except, cleanup on Ctrl+C

### AD-005: Task Display Format

**Decision**: Format tasks as `"[{id}] {title} - {status_icon} {status}"`
**Rationale**: ID for reference, title for recognition, icon for quick scanning
**Status Icons**:
- incomplete: `○`
- inProcessing: `◐`
- complete: `●`

### AD-006: Module Organization

**Decision**: Split CLI into three modules
**Rationale**: Separation of concerns, testability, reusability

| Module | Responsibility |
|--------|---------------|
| `menu.py` | Main loop, operation handlers, flow control |
| `prompts.py` | Prompt builders, validators, formatters |
| `styles.py` | Theme configuration, color constants |

## Complexity Tracking

> No violations. All design choices align with Constitution principles.

| Principle | Design Choice | Justification |
|-----------|--------------|---------------|
| Simplicity First | Only CLI layer changed | Models/services/storage untouched |
| Clear CLI Interface | InquirerPy prompts | Arrow navigation is more intuitive than number typing |
| Data Integrity | No storage changes | Atomic writes preserved in existing layer |

## Implementation Phases

### Phase 1: Foundation

- Add InquirerPy to `pyproject.toml` dependencies
- Create `src/cli/styles.py` with theme configuration
- Create `src/cli/prompts.py` with utility functions
- Update imports in `src/cli/menu.py`

### Phase 2: Main Menu (US1)

- Replace `display_menu()` with InquirerPy `select` prompt
- Replace `get_choice()` with arrow-key selection
- Update `run_menu()` loop to use new prompt
- Add TaskFolio branding header

### Phase 3: Input Prompts (US2)

- Replace `handle_add_task()` with InquirerPy `text` prompts
- Add inline validation for title (required, max 200 chars)
- Add styled success/error messages
- Update description prompt to be optional

### Phase 4: Task Selection (US3)

- Create task selector using InquirerPy `fuzzy` prompt
- Format task choices with ID, title, status icon
- Handle empty task list gracefully
- Update `handle_update_task()`, `handle_delete_task()`, `handle_change_status()`

### Phase 5: Status Selection (US4)

- Create status selector with visual indicators
- Pre-select current status
- Update `handle_change_status()` flow

### Phase 6: Delete Confirmation (US5)

- Add InquirerPy `confirm` prompt before delete
- Show task title in confirmation message
- Handle cancel gracefully

### Phase 7: Styled Output (US6)

- Apply colors to all print statements
- Add status icons to task display
- Style header with TaskFolio branding

### Phase 8: Fuzzy Search (US7)

- Enable fuzzy matching in task selector
- Test with many tasks for performance

### Phase 9: Polish & Edge Cases

- Add Ctrl+C handling throughout
- Test terminal fallback modes
- Ensure Escape key cancels operations
- Final validation of all flows

## Acceptance Checks

| Check | Verification Method |
|-------|---------------------|
| Arrow-key menu works | Navigate main menu with arrows, press Enter |
| Inline validation works | Enter empty title, see error without screen clear |
| Task selection works | Select task from list for update/delete/status |
| Fuzzy search works | Type partial title, see filtered results |
| Delete confirmation works | Select No to cancel, Yes to delete |
| Status icons display | View tasks, see different icons per status |
| Ctrl+C exits gracefully | Press Ctrl+C, see goodbye message |
| Existing data loads | Use existing JSON files with new CLI |
| All 5 operations work | Add, view, update, delete, status change |
