# PyPI Deployment Guide

This guide explains how to upload your Python package to PyPI (Python Package Index).

## Prerequisites

- Python 3.13+
- UV package manager
- PyPI account ([Register here](https://pypi.org/account/register/))
- PyPI API token ([Generate here](https://pypi.org/manage/account/token/))

## Step 1: Configure `pyproject.toml`

Ensure your `pyproject.toml` has the required fields:

```toml
[project]
name = "your-package-name"          # Must be unique on PyPI
version = "1.0.0"                   # Semantic versioning
description = "Your package description"
readme = "README.md"
requires-python = ">=3.13"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your@email.com"}
]
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
keywords = ["your", "keywords"]
dependencies = []

[project.scripts]
your-command = "src.main:main"      # CLI command

[project.urls]
Homepage = "https://github.com/username/repo"
Repository = "https://github.com/username/repo"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src"]
```

## Step 2: Create LICENSE File

Create a `LICENSE` file in your project root (MIT example):

```
MIT License

Copyright (c) 2025 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy...
```

## Step 3: Install Build Tools

```bash
uv add build twine --dev
uv sync
```

## Step 4: Build the Package

```bash
uvx --from build pyproject-build --installer uv
```

This creates two files in `dist/`:
- `your_package-1.0.0.tar.gz` (source distribution)
- `your_package-1.0.0-py3-none-any.whl` (wheel)

## Step 5: Upload to PyPI

```bash
uv run twine upload dist/* --username __token__ --password YOUR_API_TOKEN
```

**Important:**
- Username must be exactly `__token__` (not your PyPI username)
- Password is your API token (starts with `pypi-`)

## Step 6: Verify Installation

```bash
pip install your-package-name
your-command
```

---

## Updating Your Package

### 1. Bump Version

Edit `pyproject.toml`:
```toml
version = "1.0.1"  # Increment version
```

### 2. Clean Old Builds

```bash
rm -rf dist/*
```

### 3. Rebuild

```bash
uvx --from build pyproject-build --installer uv
```

### 4. Upload New Version

```bash
uv run twine upload dist/* --username __token__ --password YOUR_API_TOKEN
```

---

## Testing with TestPyPI (Recommended)

Before uploading to the real PyPI, test on TestPyPI:

### 1. Create TestPyPI Account
- Register: https://test.pypi.org/account/register/
- Generate token: https://test.pypi.org/manage/account/token/

### 2. Upload to TestPyPI

```bash
uv run twine upload --repository testpypi dist/* --username __token__ --password YOUR_TEST_TOKEN
```

### 3. Test Install

```bash
pip install --index-url https://test.pypi.org/simple/ your-package-name
```

---

## Common Errors

### "File already exists"
```
ERROR: HTTPError: 400 Bad Request - File already exists
```
**Solution:** Bump the version number in `pyproject.toml` and rebuild.

### "Username/Password authentication is no longer supported"
```
ERROR: HTTPError: 403 Forbidden - Migrate to API Tokens
```
**Solution:** Use `__token__` as username and your API token as password.

### "Invalid or non-existent authentication"
**Solution:** Regenerate your API token at https://pypi.org/manage/account/token/

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `uvx --from build pyproject-build --installer uv` | Build package |
| `uv run twine upload dist/*` | Upload to PyPI |
| `rm -rf dist/*` | Clean old builds |
| `pip install package-name --upgrade` | Install/upgrade package |

---

## Project Links

- **PyPI:** https://pypi.org/project/mesumali-console-task-manager/
- **Install:** `pip install mesumali-console-task-manager`
- **Run:** `mesumali-todo`
