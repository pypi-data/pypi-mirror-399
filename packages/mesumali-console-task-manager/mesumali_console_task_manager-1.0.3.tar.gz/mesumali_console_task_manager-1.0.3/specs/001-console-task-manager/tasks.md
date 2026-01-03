# Tasks: Console-based Task Management Application

**Input**: Design documents from `/specs/001-console-task-manager/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/, research.md, quickstart.md

**Tests**: Tests are OPTIONAL - manual validation is the primary testing strategy per plan.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below use the structure defined in plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create pyproject.toml with UV configuration for Python 3.13+ in pyproject.toml
- [x] T002 [P] Create directory structure: src/, src/models/, src/services/, src/storage/, src/cli/, db/, tests/
- [x] T003 [P] Create src/__init__.py with package docstring
- [x] T004 [P] Create src/models/__init__.py
- [x] T005 [P] Create src/services/__init__.py
- [x] T006 [P] Create src/storage/__init__.py
- [x] T007 [P] Create src/cli/__init__.py
- [x] T008 [P] Create tests/__init__.py
- [x] T009 Create README.md with setup instructions per quickstart.md

**Checkpoint**: Project structure ready - foundational implementation can begin

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T010 Create TaskStatus enum with values (incomplete, inProcessing, complete) in src/models/task.py
- [x] T011 Create Task dataclass with fields (id, title, description, status) in src/models/task.py
- [x] T012 Implement to_dict() and from_dict() methods on Task in src/models/task.py
- [x] T013 Implement JsonStorage class with constructor in src/storage/json_storage.py
- [x] T014 Implement JsonStorage.load() method with empty file handling in src/storage/json_storage.py
- [x] T015 Implement JsonStorage.save() method with atomic writes in src/storage/json_storage.py
- [x] T016 Implement TaskManager class constructor in src/services/task_manager.py
- [x] T017 Implement basic menu display function in src/cli/menu.py
- [x] T018 Create main.py entry point with username prompt in src/main.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Add New Task (Priority: P1)

**Goal**: Users can add tasks with title and description

**Independent Test**: Run app, select "Add Task", enter title and description, verify task is created with unique ID and "incomplete" status

### Implementation for User Story 1

- [x] T019 [US1] Implement TaskManager.add_task() method with title validation in src/services/task_manager.py
- [x] T020 [US1] Add ID generation logic (next_id tracking) in src/services/task_manager.py
- [x] T021 [US1] Implement add_task menu handler with input prompts in src/cli/menu.py
- [x] T022 [US1] Wire add_task option into main menu loop in src/main.py
- [x] T023 [US1] Add success/error message display for add operation in src/cli/menu.py

**Checkpoint**: User Story 1 complete - users can add tasks

---

## Phase 4: User Story 2 - View All Tasks (Priority: P1)

**Goal**: Users can view all tasks with ID, title, description, and status

**Independent Test**: Add several tasks, select "View All Tasks", verify all tasks appear with correct details and status indicators

### Implementation for User Story 2

- [x] T024 [US2] Implement TaskManager.get_all_tasks() method in src/services/task_manager.py
- [x] T025 [US2] Implement task list display formatter in src/cli/menu.py
- [x] T026 [US2] Implement empty list message handler in src/cli/menu.py
- [x] T027 [US2] Wire view_tasks option into main menu loop in src/main.py

**Checkpoint**: User Stories 1 AND 2 complete - MVP achieved (add and view tasks)

---

## Phase 5: User Story 3 - Update Task Details (Priority: P2)

**Goal**: Users can update a task's title and/or description by ID

**Independent Test**: Create a task, select "Update Task", provide task ID and new title/description, verify changes persist

### Implementation for User Story 3

- [x] T028 [US3] Implement TaskManager.update_task() method with ID validation in src/services/task_manager.py
- [x] T029 [US3] Add title validation for updates (non-empty, max 200 chars) in src/services/task_manager.py
- [x] T030 [US3] Implement update_task menu handler with input prompts in src/cli/menu.py
- [x] T031 [US3] Wire update_task option into main menu loop in src/main.py

**Checkpoint**: User Story 3 complete - users can update tasks

---

## Phase 6: User Story 4 - Delete Task (Priority: P2)

**Goal**: Users can delete a task by ID

**Independent Test**: Create a task, select "Delete Task", provide task ID, verify task is removed from list

### Implementation for User Story 4

- [x] T032 [US4] Implement TaskManager.delete_task() method with ID validation in src/services/task_manager.py
- [x] T033 [US4] Implement delete_task menu handler with ID prompt in src/cli/menu.py
- [x] T034 [US4] Wire delete_task option into main menu loop in src/main.py

**Checkpoint**: User Story 4 complete - users can delete tasks

---

## Phase 7: User Story 5 - Mark Task Status (Priority: P2)

**Goal**: Users can change a task's status to incomplete, inProcessing, or complete

**Independent Test**: Create a task, select "Change Status", provide task ID and new status, verify status changes

### Implementation for User Story 5

- [x] T035 [US5] Implement TaskManager.set_status() method with validation in src/services/task_manager.py
- [x] T036 [US5] Implement status selection submenu in src/cli/menu.py
- [x] T037 [US5] Wire set_status option into main menu loop in src/main.py

**Checkpoint**: All 5 user stories complete - full feature set implemented

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T038 [P] Add input validation for non-numeric task IDs in src/cli/menu.py
- [x] T039 [P] Add exit confirmation and goodbye message in src/cli/menu.py
- [x] T040 [P] Ensure consistent error message formatting across all operations in src/cli/menu.py
- [x] T041 Update README.md with complete usage examples
- [x] T042 Manual validation: test all 5 operations per acceptance checks in plan.md
- [x] T043 Manual validation: test edge cases (invalid ID, empty title, restart persistence)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 and US2 can proceed in parallel (both P1)
  - US3, US4, US5 can proceed in parallel after US1+US2 (all P2)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 3 (P2)**: Can start after Foundational - Works with existing tasks
- **User Story 4 (P2)**: Can start after Foundational - Works with existing tasks
- **User Story 5 (P2)**: Can start after Foundational - Works with existing tasks

### Within Each User Story

- TaskManager method before CLI handler
- CLI handler before main.py wiring
- All components before checkpoint validation

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002-T008)
- Within each user story, only TaskManager tasks block CLI tasks
- Different user stories can be worked on in parallel by different developers

---

## Parallel Example: Setup Phase

```bash
# Launch all [P] tasks in Setup together:
Task T002: "Create directory structure"
Task T003: "Create src/__init__.py"
Task T004: "Create src/models/__init__.py"
Task T005: "Create src/services/__init__.py"
Task T006: "Create src/storage/__init__.py"
Task T007: "Create src/cli/__init__.py"
Task T008: "Create tests/__init__.py"
```

## Parallel Example: P1 User Stories

```bash
# After Foundational phase, launch P1 stories in parallel:
# Developer A: User Story 1 (Add Task)
Task T019-T023

# Developer B: User Story 2 (View Tasks)
Task T024-T027
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Add Task)
4. Complete Phase 4: User Story 2 (View Tasks)
5. **STOP and VALIDATE**: Test adding and viewing tasks
6. Deploy/demo if ready - this is a functional MVP

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Users can add tasks
3. Add User Story 2 → Test independently → Users can view tasks (MVP!)
4. Add User Story 3 → Test independently → Users can update tasks
5. Add User Story 4 → Test independently → Users can delete tasks
6. Add User Story 5 → Test independently → Users can change status
7. Each story adds value without breaking previous stories

### Full Sequential Strategy

1. Phase 1: Setup (T001-T009)
2. Phase 2: Foundational (T010-T018)
3. Phase 3: US1 Add Task (T019-T023)
4. Phase 4: US2 View Tasks (T024-T027)
5. Phase 5: US3 Update Task (T028-T031)
6. Phase 6: US4 Delete Task (T032-T034)
7. Phase 7: US5 Mark Status (T035-T037)
8. Phase 8: Polish (T038-T043)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
