# Feature Specification: TaskFolio Interactive CLI with InquirerPy

**Feature Branch**: `002-inquirer-cli`
**Created**: 2025-12-31
**Status**: Draft
**Input**: User description: "Redesign TaskFolio CLI with InquirerPy for interactive prompts - arrow-key navigation, task selection from lists, styled output, and modern CLI experience"

## Clarifications

### Session 2025-12-31

- Q: Which Python interactive prompt library to use? → A: InquirerPy (modern Python port of Inquirer.js with best feature set)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Interactive Main Menu Navigation (Priority: P1)

As a TaskFolio user, I want to navigate the main menu using arrow keys so that I can quickly select operations without typing numbers.

**Why this priority**: The main menu is the entry point for all operations. Arrow-key navigation provides the foundation for the entire interactive experience and must work before any other feature can be used effectively.

**Independent Test**: Can be fully tested by launching the app, using arrow keys to highlight each menu option, pressing Enter to select, and verifying the correct operation is triggered. Delivers immediate value by replacing number-typing with intuitive navigation.

**Acceptance Scenarios**:

1. **Given** the application is running and main menu is displayed, **When** I press the down arrow key, **Then** the selection highlight moves to the next menu option
2. **Given** the selection is on "Add Task", **When** I press Enter, **Then** the add task flow begins
3. **Given** the selection is on the last menu item, **When** I press down arrow, **Then** the selection wraps to the first item (or stays on last - follows InquirerPy default)
4. **Given** the main menu is displayed, **When** I view the screen, **Then** the current user's name "TaskFolio (username)" is displayed as a styled header
5. **Given** the main menu is displayed, **When** I view the menu options, **Then** each option has a visual indicator (icon or prefix) indicating its function

---

### User Story 2 - Interactive Task Input with Validation (Priority: P1)

As a TaskFolio user, I want to enter task details through styled prompts with inline validation so that I receive immediate feedback on input errors without disrupting my workflow.

**Why this priority**: Task creation is the most common operation. Inline validation prevents user errors and provides a polished, professional experience essential for the core functionality.

**Independent Test**: Can be fully tested by selecting "Add Task", entering invalid input (empty title), seeing inline error message, entering valid input, and confirming task creation success.

**Acceptance Scenarios**:

1. **Given** I am in the add task flow, **When** the title prompt appears, **Then** I see a styled prompt with a clear label and input field
2. **Given** I submit an empty title, **When** validation runs, **Then** an inline error message appears below the input without clearing my screen or requiring re-navigation
3. **Given** I enter a title exceeding 200 characters, **When** validation runs, **Then** an inline error message indicates the maximum length allowed
4. **Given** I enter a valid title and description, **When** I confirm the input, **Then** a styled success message displays with the new task ID
5. **Given** the description prompt appears, **When** I press Enter without typing, **Then** the task is created with an empty description (description remains optional)

---

### User Story 3 - Task Selection from List (Priority: P1)

As a TaskFolio user, I want to select tasks from an interactive list instead of typing IDs so that I can see task details while choosing and avoid ID lookup errors.

**Why this priority**: Selecting tasks by ID is error-prone and requires users to remember or look up IDs. Interactive selection is fundamental to update, delete, and status change operations - three of the five core features.

**Independent Test**: Can be fully tested by adding tasks, selecting "Update Task", browsing the task list with arrow keys, selecting a task, and verifying the correct task is selected for editing.

**Acceptance Scenarios**:

1. **Given** tasks exist and I select "Update Task", **When** the task selector appears, **Then** I see a scrollable list showing each task with format "[ID] Title - Status"
2. **Given** the task selector is displayed, **When** I use arrow keys, **Then** the selection highlight moves between tasks
3. **Given** I highlight a task in the selector, **When** I view the display, **Then** I can see the task's ID, title, and current status clearly
4. **Given** I highlight a task and press Enter, **When** the selection is confirmed, **Then** the selected task is passed to the next operation step
5. **Given** no tasks exist, **When** I select an operation requiring task selection, **Then** a styled message indicates no tasks are available and returns to the main menu
6. **Given** many tasks exist (more than fit on screen), **When** I scroll through the list, **Then** the list scrolls smoothly to show all available tasks

---

### User Story 4 - Interactive Status Selection (Priority: P2)

As a TaskFolio user, I want to select task status from a visual menu with status indicators so that I can quickly understand and change task states.

**Why this priority**: Status changes are frequent operations. Visual indicators make the current state and available options immediately clear, reducing cognitive load.

**Independent Test**: Can be fully tested by creating a task, selecting "Change Status", selecting the task, choosing a new status from the visual menu, and verifying the status updates correctly.

**Acceptance Scenarios**:

1. **Given** I am in the change status flow and have selected a task, **When** the status menu appears, **Then** I see three options with visual indicators: incomplete, inProcessing, complete
2. **Given** the status menu is displayed, **When** I view the options, **Then** the current task's status is visually indicated (highlighted or marked)
3. **Given** I select a new status and confirm, **When** the operation completes, **Then** a styled success message confirms the status change
4. **Given** I select the same status the task already has, **When** I confirm, **Then** the system accepts it gracefully (no error, confirms current status)

---

### User Story 5 - Delete Confirmation Dialog (Priority: P2)

As a TaskFolio user, I want to confirm task deletion through a yes/no prompt so that I don't accidentally delete important tasks.

**Why this priority**: Deletion is irreversible. A confirmation step prevents accidental data loss and is a standard UX pattern for destructive operations.

**Independent Test**: Can be fully tested by selecting "Delete Task", choosing a task, seeing the confirmation prompt with task details, selecting "No" to cancel, then repeating and selecting "Yes" to delete.

**Acceptance Scenarios**:

1. **Given** I select a task for deletion, **When** the confirmation prompt appears, **Then** I see the task title and a clear yes/no choice
2. **Given** the confirmation prompt is displayed, **When** I select "No", **Then** the deletion is cancelled and I return to the main menu with a cancellation message
3. **Given** the confirmation prompt is displayed, **When** I select "Yes", **Then** the task is deleted and a styled success message confirms the deletion
4. **Given** the confirmation prompt is displayed, **When** I press Escape or Ctrl+C, **Then** the deletion is cancelled (same as selecting "No")

---

### User Story 6 - Styled Output and Visual Feedback (Priority: P2)

As a TaskFolio user, I want to see styled, colored output with clear visual hierarchy so that I can quickly scan information and understand system feedback.

**Why this priority**: Visual styling improves usability and makes the application feel professional. This enhances all other features by making their output more readable.

**Independent Test**: Can be fully tested by performing each operation and verifying that success messages, error messages, and task listings use distinct visual styles (colors, formatting).

**Acceptance Scenarios**:

1. **Given** an operation succeeds, **When** the success message displays, **Then** it uses a distinct success style (green color or success icon)
2. **Given** an operation fails, **When** the error message displays, **Then** it uses a distinct error style (red color or error icon)
3. **Given** I view the task list, **When** tasks are displayed, **Then** task IDs, titles, and statuses have distinct visual styling
4. **Given** tasks have different statuses, **When** I view the list, **Then** each status type has a unique visual indicator (color or icon): incomplete, inProcessing, complete
5. **Given** the application header displays, **When** I view it, **Then** the "TaskFolio" branding and username are prominently styled

---

### User Story 7 - Fuzzy Search for Task Selection (Priority: P3)

As a TaskFolio user with many tasks, I want to search for tasks by typing partial text so that I can quickly find specific tasks without scrolling through a long list.

**Why this priority**: Optional enhancement for users with many tasks. The application works well without this for typical use cases, but it significantly improves efficiency for power users.

**Independent Test**: Can be fully tested by adding many tasks, selecting an operation requiring task selection, typing partial task title text, and verifying matching tasks are filtered in real-time.

**Acceptance Scenarios**:

1. **Given** I am in a task selector with many tasks, **When** I start typing, **Then** the list filters to show only tasks matching my input
2. **Given** I type "gro" into the filter, **When** the list updates, **Then** tasks with "gro" in their title (e.g., "Buy groceries") are shown
3. **Given** I clear my filter input, **When** the list updates, **Then** all tasks are shown again
4. **Given** no tasks match my filter, **When** the list updates, **Then** a message indicates no matching tasks found

---

### Edge Cases

- What happens when the user presses Ctrl+C during any prompt? Application exits gracefully with a goodbye message.
- What happens when terminal doesn't support colors? InquirerPy falls back to plain text mode automatically.
- What happens when terminal window is very small? Prompts and lists adapt to available space (InquirerPy handles this).
- What happens when user presses Escape during input? Current operation is cancelled and user returns to main menu.
- What happens when task list is empty and user selects update/delete/status? Styled message indicates no tasks available, returns to menu.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display the main menu as an interactive list navigable with arrow keys
- **FR-002**: System MUST allow menu option selection by pressing Enter on highlighted option
- **FR-003**: System MUST display styled text prompts for all user inputs (title, description, username)
- **FR-004**: System MUST validate input inline and display error messages without clearing the screen
- **FR-005**: System MUST present task selection as an interactive list showing task ID, title, and status
- **FR-006**: System MUST display status options as an interactive selection with visual indicators
- **FR-007**: System MUST prompt for confirmation before deleting a task
- **FR-008**: System MUST use distinct visual styles for success messages, error messages, and warnings
- **FR-009**: System MUST use distinct visual indicators (colors or icons) for each task status
- **FR-010**: System MUST display "TaskFolio" branding in the application header with username
- **FR-011**: System MUST handle keyboard interrupts (Ctrl+C) gracefully with exit message
- **FR-012**: System MUST fall back to plain text mode in terminals without color support
- **FR-013**: System MUST support fuzzy search filtering in task selection lists
- **FR-014**: System MUST preserve all existing task management functionality (add, view, update, delete, status change)
- **FR-015**: System MUST maintain data compatibility with existing JSON storage format

### Key Entities

- **Menu Option**: Represents a selectable action in the main menu (label, action handler, icon/prefix)
- **Task Display Item**: Formatted representation of a task for list display (ID, title, truncated description, status with visual indicator)
- **Confirmation Dialog**: Yes/No prompt with context message for destructive operations
- **Input Prompt**: Styled text input with label, placeholder, and validation rules

## Assumptions

- Users have terminals that support Unicode characters for visual indicators
- InquirerPy library is available and compatible with Python 3.13+
- Existing Task, TaskManager, and JsonStorage classes remain unchanged (only CLI layer is refactored)
- Terminal width is at least 80 characters for optimal display
- Users are familiar with arrow-key navigation patterns common in modern CLI tools

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete any menu selection in under 2 seconds (from menu display to operation start)
- **SC-002**: Users can select a task from a list of 20 tasks in under 5 seconds using arrow keys or fuzzy search
- **SC-003**: 100% of invalid inputs result in inline error messages that don't disrupt the current screen
- **SC-004**: Zero accidental deletions occur due to confirmation dialog requirement
- **SC-005**: Users can visually distinguish between the three task statuses at a glance (within 1 second)
- **SC-006**: Users can identify success vs error feedback at a glance through visual styling
- **SC-007**: Application gracefully handles all keyboard interrupts (Ctrl+C, Escape) without crashing or data loss
- **SC-008**: All 5 core task operations remain fully functional after UI redesign (add, view, update, delete, status)
- **SC-009**: Existing user data files remain compatible and load correctly in the new interface
