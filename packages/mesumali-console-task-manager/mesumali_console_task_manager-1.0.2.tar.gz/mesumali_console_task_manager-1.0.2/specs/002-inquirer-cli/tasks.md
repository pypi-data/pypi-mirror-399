# Tasks: TaskFolio Interactive CLI with InquirerPy

**Input**: Design documents from `/specs/002-inquirer-cli/`
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

**Purpose**: Add InquirerPy dependency and create new CLI modules

- [X] T001 Add InquirerPy dependency to pyproject.toml
- [X] T002 [P] Create src/cli/styles.py with TASKFOLIO_STYLE dict and STATUS_ICONS constant
- [X] T003 [P] Create src/cli/prompts.py with module docstring and imports

**Checkpoint**: Dependencies installed, new modules ready for implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core prompt utilities that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Implement validate_title() function in src/cli/prompts.py
- [X] T005 [P] Implement validate_username() function in src/cli/prompts.py
- [X] T006 [P] Implement print_success(), print_error(), print_info() in src/cli/styles.py
- [X] T007 Implement print_header(username) function in src/cli/styles.py
- [X] T008 Implement build_task_choices(tasks) function in src/cli/prompts.py
- [X] T009 [P] Implement build_status_choices(current_status) function in src/cli/prompts.py
- [X] T010 [P] Implement build_menu_choices() function in src/cli/prompts.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Interactive Main Menu Navigation (Priority: P1)

**Goal**: Users navigate menu with arrow keys instead of typing numbers

**Independent Test**: Launch app, use arrow keys to highlight menu options, press Enter to select, verify correct operation triggers

### Implementation for User Story 1

- [X] T011 [US1] Import InquirerPy and prompts module in src/cli/menu.py
- [X] T012 [US1] Replace display_menu() with print_header() call in src/cli/menu.py
- [X] T013 [US1] Replace get_choice() with inquirer.select() using build_menu_choices() in src/cli/menu.py
- [X] T014 [US1] Update run_menu() loop to use new prompt and handle action values in src/cli/menu.py
- [X] T015 [US1] Add try/except KeyboardInterrupt wrapper around menu loop in src/cli/menu.py

**Checkpoint**: User Story 1 complete - arrow-key menu navigation works

---

## Phase 4: User Story 2 - Interactive Task Input with Validation (Priority: P1)

**Goal**: Users enter task details with styled prompts and inline validation

**Independent Test**: Select "Add Task", enter empty title (see inline error), enter valid title and description, see styled success message

### Implementation for User Story 2

- [X] T016 [US2] Create prompt_task_title() function using inquirer.text() with validation in src/cli/prompts.py
- [X] T017 [US2] Create prompt_task_description() function using inquirer.text() in src/cli/prompts.py
- [X] T018 [US2] Refactor handle_add_task() to use prompt_task_title() and prompt_task_description() in src/cli/menu.py
- [X] T019 [US2] Replace print() success/error messages with print_success()/print_error() in handle_add_task() in src/cli/menu.py

**Checkpoint**: User Story 2 complete - styled input with inline validation works

---

## Phase 5: User Story 3 - Task Selection from List (Priority: P1)

**Goal**: Users select tasks from interactive list instead of typing IDs

**Independent Test**: Add tasks, select "Update Task", browse task list with arrows, select a task, verify correct task is selected

### Implementation for User Story 3

- [X] T020 [US3] Create prompt_select_task(tasks, message) function using inquirer.fuzzy() in src/cli/prompts.py
- [X] T021 [US3] Add empty list check in prompt_select_task() that prints info and returns None in src/cli/prompts.py
- [X] T022 [US3] Refactor handle_update_task() to use prompt_select_task() instead of input() in src/cli/menu.py
- [X] T023 [US3] Refactor handle_delete_task() to use prompt_select_task() instead of input() in src/cli/menu.py
- [X] T024 [US3] Refactor handle_change_status() to use prompt_select_task() instead of input() in src/cli/menu.py
- [X] T025 [US3] Update handle_update_task() to use inquirer.text() for new title/description in src/cli/menu.py

**Checkpoint**: User Story 3 complete - task selection from list works for update/delete/status

---

## Phase 6: User Story 4 - Interactive Status Selection (Priority: P2)

**Goal**: Users select status from visual menu with icons

**Independent Test**: Create task, select "Change Status", select task, choose new status from visual menu, verify status updates

### Implementation for User Story 4

- [X] T026 [US4] Create prompt_select_status(current_status) function using inquirer.select() in src/cli/prompts.py
- [X] T027 [US4] Update handle_change_status() to use prompt_select_status() with status icons in src/cli/menu.py
- [X] T028 [US4] Replace status print() messages with print_success() in handle_change_status() in src/cli/menu.py

**Checkpoint**: User Story 4 complete - status selection with visual indicators works

---

## Phase 7: User Story 5 - Delete Confirmation Dialog (Priority: P2)

**Goal**: Users confirm deletion through yes/no prompt

**Independent Test**: Select "Delete Task", choose task, see confirmation with task title, select No (cancelled), repeat with Yes (deleted)

### Implementation for User Story 5

- [X] T029 [US5] Create prompt_confirm_delete(task_title) function using inquirer.confirm() in src/cli/prompts.py
- [X] T030 [US5] Update handle_delete_task() to call prompt_confirm_delete() before deletion in src/cli/menu.py
- [X] T031 [US5] Add cancellation message when user selects No in handle_delete_task() in src/cli/menu.py

**Checkpoint**: User Story 5 complete - delete confirmation prevents accidental deletions

---

## Phase 8: User Story 6 - Styled Output and Visual Feedback (Priority: P2)

**Goal**: Users see styled, colored output with visual hierarchy

**Independent Test**: Perform each operation, verify success (green), error (red), and task listings use distinct styles

### Implementation for User Story 6

- [X] T032 [US6] Update handle_view_tasks() to use print_info() for empty list message in src/cli/menu.py
- [X] T033 [US6] Update display_task() to include status icons from STATUS_ICONS in src/cli/menu.py
- [X] T034 [US6] Apply TASKFOLIO_STYLE to all inquirer prompts in src/cli/menu.py
- [X] T035 [US6] Replace all remaining print() calls with styled equivalents in src/cli/menu.py

**Checkpoint**: User Story 6 complete - styled output with colors and icons throughout

---

## Phase 9: User Story 7 - Fuzzy Search for Task Selection (Priority: P3)

**Goal**: Users can type to filter tasks in selection lists

**Independent Test**: Add many tasks, select operation requiring task selection, type partial title, verify filtered results

### Implementation for User Story 7

- [X] T036 [US7] Verify fuzzy matching is enabled in prompt_select_task() (InquirerPy default) in src/cli/prompts.py
- [X] T037 [US7] Test fuzzy search with 20+ tasks to verify performance in manual testing

**Checkpoint**: User Story 7 complete - fuzzy search filters tasks efficiently

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements affecting all user stories

- [X] T038 [P] Update src/main.py to use inquirer.text() for username prompt with validation
- [X] T039 [P] Add graceful Ctrl+C handling in src/main.py get_username() function
- [X] T040 [P] Ensure Escape key cancels current operation and returns to menu
- [X] T041 Update README.md with new InquirerPy-based usage instructions
- [ ] T042 Manual validation: test all 5 operations per acceptance checks in plan.md
- [ ] T043 Manual validation: test edge cases (Ctrl+C, empty list, invalid input, existing data)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion
  - US1, US2, US3 are P1 (can proceed in parallel after Foundational)
  - US4, US5, US6 are P2 (can proceed in parallel after Foundational)
  - US7 is P3 (optional enhancement)
- **Polish (Phase 10)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 3 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 4 (P2)**: Depends on US3 (uses task selection) - Should complete after US3
- **User Story 5 (P2)**: Depends on US3 (uses task selection) - Should complete after US3
- **User Story 6 (P2)**: Can start after Foundational - No dependencies on other stories
- **User Story 7 (P3)**: Depends on US3 (enhances task selection) - Should complete after US3

### Within Each User Story

- prompts.py functions before menu.py handlers
- Core implementation before integration
- All components before checkpoint validation

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002, T003)
- All Foundational tasks marked [P] can run in parallel (T005, T006, T009, T010)
- US1, US2, US6 can proceed in parallel (no cross-dependencies)
- US3 should complete first, then US4, US5, US7 can proceed in parallel
- All Polish tasks marked [P] can run in parallel (T038, T039, T040)

---

## Parallel Example: Setup Phase

```bash
# Launch all [P] tasks in Setup together:
Task T002: "Create src/cli/styles.py with TASKFOLIO_STYLE dict"
Task T003: "Create src/cli/prompts.py with module docstring"
```

## Parallel Example: Foundational Phase

```bash
# After T004, launch all [P] tasks together:
Task T005: "Implement validate_username() function"
Task T006: "Implement print_success(), print_error(), print_info()"
Task T009: "Implement build_status_choices()"
Task T010: "Implement build_menu_choices()"
```

## Parallel Example: P1 User Stories

```bash
# After Foundational phase, launch P1 stories in parallel:
# Developer A: User Story 1 (Menu Navigation)
Task T011-T015

# Developer B: User Story 2 (Input Validation)
Task T016-T019

# Developer C: User Story 3 (Task Selection)
Task T020-T025
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 + 3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Menu Navigation)
4. Complete Phase 4: User Story 2 (Input Validation)
5. Complete Phase 5: User Story 3 (Task Selection)
6. **STOP and VALIDATE**: Test all three P1 stories
7. Deploy/demo if ready - this is a functional MVP with interactive UI

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Arrow-key menu works
3. Add User Story 2 → Test independently → Styled inputs work
4. Add User Story 3 → Test independently → Task selection works (MVP!)
5. Add User Story 4 → Test independently → Status selection works
6. Add User Story 5 → Test independently → Delete confirmation works
7. Add User Story 6 → Test independently → Full styling applied
8. Add User Story 7 → Test independently → Fuzzy search works
9. Each story adds value without breaking previous stories

### Full Sequential Strategy

1. Phase 1: Setup (T001-T003)
2. Phase 2: Foundational (T004-T010)
3. Phase 3: US1 Menu Navigation (T011-T015)
4. Phase 4: US2 Input Validation (T016-T019)
5. Phase 5: US3 Task Selection (T020-T025)
6. Phase 6: US4 Status Selection (T026-T028)
7. Phase 7: US5 Delete Confirmation (T029-T031)
8. Phase 8: US6 Styled Output (T032-T035)
9. Phase 9: US7 Fuzzy Search (T036-T037)
10. Phase 10: Polish (T038-T043)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
