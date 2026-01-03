<!--
Sync Impact Report
==================
Version change: 0.0.0 → 1.0.0 (MAJOR - initial ratification)

Added sections:
- Core Principles (6 principles defined)
- Technology Stack section
- Project Structure section
- Quality Constraints section
- Success Criteria section
- Governance section

Modified principles: N/A (initial version)
Removed sections: N/A (initial version)

Templates requiring updates:
- `.specify/templates/plan-template.md` - ✅ Compatible (no changes needed)
- `.specify/templates/spec-template.md` - ✅ Compatible (no changes needed)
- `.specify/templates/tasks-template.md` - ✅ Compatible (no changes needed)

Follow-up TODOs: None
-->

# Todo In-Memory Python Console App Constitution

## Core Principles

### I. Simplicity First

Every feature MUST be implemented with minimal complexity. The console application
should remain focused on the five core operations: Add, Delete, Update, View, and
Mark Complete. No unnecessary abstractions or over-engineering.

**Rationale**: A todo app is inherently simple. Code complexity should match problem
complexity. Premature optimization and abstraction obscure intent.

### II. User Data Isolation

Each user MUST have their own JSON file in the `db/` directory. User files are
named by user identifier (e.g., `db/user_alice.json`). Operations on one user's
data MUST NOT affect another user's data.

**Rationale**: Per-user files provide natural data isolation, simplify debugging,
and enable straightforward backup/restore per user.

### III. Stateless CLI Operations

Each command invocation MUST read the current state from JSON, perform the
operation, and write back immediately. No in-memory session state between
commands. The JSON file is the single source of truth.

**Rationale**: Stateless design prevents data loss, enables concurrent tool usage,
and simplifies testing and debugging.

### IV. Test-First Development

All features MUST be developed using TDD (Test-Driven Development):
1. Write failing tests that capture expected behavior
2. Implement minimal code to make tests pass
3. Refactor while keeping tests green

**Rationale**: TDD ensures correctness, documents behavior, and prevents regressions.
For a data-manipulating app, tests catch edge cases early.

### V. Clear CLI Interface

The command-line interface MUST be intuitive and self-documenting:
- Commands use clear verbs: `add`, `delete`, `update`, `view`, `complete`
- Help text is available for every command
- Error messages are actionable and specific
- Output uses human-readable format by default

**Rationale**: CLI usability directly impacts user experience. Confusion leads to
data errors in a todo application.

### VI. Data Integrity

All JSON file operations MUST maintain data integrity:
- Write operations use atomic file replacement (write temp, rename)
- Task IDs are unique and persistent within a user's file
- Invalid JSON or corrupt files MUST be detected and reported clearly
- Backup before destructive operations is RECOMMENDED

**Rationale**: User task data is valuable. Partial writes or corruption are
unacceptable failures.

## Technology Stack

**Language**: Python 3.13+
**Package Manager**: UV
**Testing**: pytest (recommended)
**Data Format**: JSON files in `db/` directory
**Interface**: Console/CLI (stdin/stdout)

**Constraints**:
- No external database dependencies
- No web framework required
- Standard library preferred where sufficient

## Project Structure

```
src/
├── __init__.py
├── models/           # Task data models
├── services/         # Business logic (CRUD operations)
├── storage/          # JSON file I/O
└── cli/              # Command-line interface

db/                   # User JSON files (created at runtime)

tests/
├── unit/             # Unit tests for models and services
├── integration/      # End-to-end CLI tests
└── fixtures/         # Test data

README.md             # Setup and usage instructions
pyproject.toml        # UV/Python project configuration
```

## Quality Constraints

- Code MUST run without errors on Python 3.13+
- No hard-coded test data in production logic
- Clear error handling for invalid inputs (e.g., invalid task ID, missing fields)
- Output MUST clearly reflect system state after each operation
- No external dependencies unless explicitly justified in specs

## Success Criteria

- All 5 required task operations work correctly via the console (Add, Delete, Update, View, Mark Complete)
- Behavior matches specifications exactly
- Codebase is clean, readable, and logically structured
- Repository structure matches the defined deliverables
- Application can be cloned, set up, and run using README instructions without modification
- Claude Code can understand and extend the project using CLAUDE.md guidance

## Governance

### Amendment Process

1. Amendments MUST be documented with rationale
2. Changes to Core Principles require explicit justification
3. Version number MUST increment per semantic versioning:
   - MAJOR: Principle removal or redefinition
   - MINOR: New principle or section added
   - PATCH: Clarifications or typo fixes

### Compliance

- All code reviews MUST verify adherence to Core Principles
- Violations require documented justification in ADR if approved
- Constitution takes precedence over convenience

### Runtime Guidance

Development-specific guidance (coding standards, commit conventions, etc.)
should be documented in `README.md` or supplementary docs, not in this
constitution.

**Version**: 1.0.0 | **Ratified**: 2025-12-29 | **Last Amended**: 2025-12-29
