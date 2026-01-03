---
name: python-code-writer
description: Write Python code following project conventions. Use when creating or modifying Python files (.py), writing functions, classes, or modules. Applies to all Python development tasks including new features, bug fixes, refactoring, and test writing.
---

# Python Code Writer

Write Python code following these conventions.

## Structure

- Use functions by default; classes only for state or domain modeling
- Import order: standard library → third-party → local
- Use `if __name__ == "__main__":` for scripts/entry points only

## Naming

| Element | Convention | Example |
|---------|------------|---------|
| Variables/functions | snake_case | `user_count`, `get_user()` |
| Classes | PascalCase | `UserService` |
| Constants | UPPER_CASE | `MAX_RETRIES` |

Prefer descriptive names: `dataframe` over `df`. Add context when ambiguous: `user_dataframe`.

## Type Hints & Comments

- Always add type hints
- Use Google-style docstrings
- Add 1-2 line comment above every function/class explaining what it does

```python
# Fetch user by ID, return None if not found.
def get_user_by_id(user_id: int, db: Database) -> User | None:
    """Retrieve a user record.

    Args:
        user_id: The unique identifier.
        db: Database connection.

    Returns:
        User if found, None otherwise.
    """
    return db.query(User).filter_by(id=user_id).first()
```

## Function Signatures

Keep signatures on a single line regardless of parameter count. Ignore line-length limits for definitions.

```python
# ✅ Correct
def create_user(user_id: int, username: str, email: str, password: str, age: int, is_active: bool, created_at: datetime) -> User:
    pass

# ❌ Wrong
def create_user(
    user_id: int,
    username: str,
    ...
):
    pass
```

## Error Handling

- Let exceptions propagate by default
- Catch only to add context or recover
- Create custom exception classes for domain logic

```python
class UserNotFoundError(Exception):
    """Raised when user lookup fails."""
    pass
```

## Libraries

| Prefer | Over |
|--------|------|
| `pathlib` | `os.path` |
| `dataclasses` | plain dicts (simple models) |
| `pydantic` | manual validation |

## Tooling

- Formatters: black, ruff
- Type checking: mypy
- Testing: pytest (separate `tests/` directory)

## Dependencies

Never use `pip install`. Always use `uv`:

```bash
uv init
uv add requests
uv add pytest --dev
```
