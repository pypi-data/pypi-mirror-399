# miu-code Code Standards

**Version:** 0.2.0
**Last Updated:** 2025-12-31

## Overview

This document defines the code standards and conventions for the miu-code project. All contributors must follow these standards to maintain consistency, readability, and maintainability across the codebase.

## Table of Contents

1. [Python Version & Environment](#python-version--environment)
2. [Style & Formatting](#style--formatting)
3. [Type Hints](#type-hints)
4. [Naming Conventions](#naming-conventions)
5. [Documentation Standards](#documentation-standards)
6. [Code Organization](#code-organization)
7. [Error Handling](#error-handling)
8. [Testing Standards](#testing-standards)
9. [Tools & Linting](#tools--linting)

## Python Version & Environment

**Required Version:** Python 3.11 or higher

**Supported Versions:**
- Python 3.11
- Python 3.12
- Python 3.13

**Virtual Environment:**
```bash
python3.11 -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
```

**Package Management:** Use `uv` for dependency management

```bash
uv sync              # Install dependencies
uv add <package>     # Add new dependency
uv remove <package>  # Remove dependency
```

## Style & Formatting

### Code Formatter

Use **Ruff** for automatic code formatting:

```bash
ruff format miu_code/ tests/
```

**Configuration** (pyproject.toml):
```toml
[tool.ruff.format]
line-length = 100
skip-magic-trailing-comma = false
```

### Indentation

- Use **spaces** (not tabs)
- **4 spaces per indentation level**
- Max line length: **100 characters**

### Imports

**Order (PEP 8):**
1. Standard library imports
2. Third-party imports
3. Local imports (relative imports with dots)

```python
# Standard library
import asyncio
import os
from collections.abc import AsyncIterator
from typing import ClassVar

# Third-party
import asyncclick as click
from rich.console import Console
from textual.app import App

# Local
from miu_code.agent.coding import CodingAgent
from miu_code.tools import get_all_tools
```

**Use isort or ruff to organize imports automatically**

### Line Length

- **Maximum:** 100 characters
- **Exception:** Long strings, URLs, or table formatting
- Break long lines with parentheses or backslash

```python
# Good: Parentheses
result = (
    some_long_function_name(arg1, arg2)
    + other_function(arg3, arg4)
)

# Also good: Backslash for imports
from some.very.long.module.path import (
    ClassA,
    ClassB,
    ClassC,
)
```

### Blank Lines

- **Two blank lines** between top-level functions and classes
- **One blank line** between methods in a class
- Use blank lines to organize logical sections within functions

```python
class MyClass:
    """Docstring."""

    def method_one(self) -> None:
        """Method one."""
        pass

    def method_two(self) -> None:
        """Method two."""
        pass


def top_level_function() -> None:
    """Top level function."""
    pass
```

## Type Hints

**All public functions and methods must have type hints**

### Function Signatures

```python
def read_file(
    path: str,
    encoding: str = "utf-8",
    limit: int | None = None,
) -> str:
    """Read file contents."""
    pass

async def run_stream(
    self,
    query: str,
) -> AsyncIterator[StreamEvent]:
    """Run query with streaming."""
    pass
```

### Type Union Syntax

Use **PEP 604 union syntax** (Python 3.10+):

```python
# Good (Python 3.11+)
value: str | None = None

# Avoid (older style)
value: Optional[str] = None
```

### Complex Types

```python
from collections.abc import AsyncIterator, Callable
from typing import Any

# Type aliases for clarity
MessageList = list[dict[str, Any]]
StreamCallback = Callable[[str], None]

def process_messages(messages: MessageList) -> str:
    pass

async def stream_with_callback(
    callback: StreamCallback,
) -> AsyncIterator[str]:
    pass
```

### Generic Classes

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class Container(Generic[T]):
    """Generic container."""

    def __init__(self, value: T) -> None:
        self.value = value

    def get(self) -> T:
        return self.value
```

### mypy Configuration

```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
strict_optional = true
```

**Verify compliance:**
```bash
mypy miu_code/
```

## Naming Conventions

### Module & Package Names

**snake_case** - lowercase with underscores
```python
# Good
miu_code/
  coding_agent.py
  session_storage.py

# Avoid
MiuCode/
  CodingAgent.py
```

### Class Names

**PascalCase** - capitalize first letter of each word
```python
# Good
class CodingAgent:
    pass

class ChatInputContainer:
    pass

# Avoid
class coding_agent:
    pass

class Chat_Input_Container:
    pass
```

### Function & Method Names

**snake_case** - lowercase with underscores
```python
# Good
def read_file(path: str) -> str:
    pass

def on_message_submitted(self, message: str) -> None:
    pass

# Avoid
def readFile(path: str) -> str:
    pass

def OnMessageSubmitted(self, message: str) -> None:
    pass
```

### Constants

**UPPER_CASE** - all uppercase with underscores
```python
# Good
MAX_RETRIES = 3
DEFAULT_MODEL = "anthropic:claude-sonnet-4-20250514"
TIMEOUT_SECONDS = 600

# Avoid
MaxRetries = 3
defaultModel = "anthropic:claude-sonnet-4-20250514"
```

### Private Attributes

Prefix with single underscore

```python
class Agent:
    def __init__(self) -> None:
        self._agent: ReActAgent | None = None
        self._is_processing = False

    def _init_agent(self) -> None:
        """Private initialization method."""
        pass
```

### Positional-Only & Keyword-Only Arguments

```python
# Positional-only (/)
def func(arg1: str, /) -> None:
    pass

# Keyword-only (*)
def func(*, arg1: str, arg2: int) -> None:
    pass

# Mixed
def func(arg1: str, /, arg2: str, *, arg3: int) -> None:
    pass
```

## Documentation Standards

### Module Docstrings

Every module must have a docstring at the top:

```python
"""Chat input system for TUI interface.

This module provides text input widgets with history support
and completion popups for the Textual-based TUI.
"""

import asyncio
```

### Class Docstrings

Document class purpose and important attributes:

```python
class ChatInputContainer(Container):
    """Input container with history and completion support.

    Provides a multiline text input with command history navigation
    and autocomplete suggestions. Part of the TUI chat interface.

    Attributes:
        _body: The ChatInputBody widget containing input logic.
        _completion_popup: Autocomplete suggestion popup.
    """

    def __init__(self) -> None:
        """Initialize the input container."""
        super().__init__()
```

### Function/Method Docstrings

Use Google-style docstrings:

```python
def read_file(
    path: str,
    encoding: str = "utf-8",
    limit: int | None = None,
) -> str:
    """Read file contents from disk.

    Supports reading large files with optional line-based limits.
    Handles various encodings and binary files gracefully.

    Args:
        path: Path to file relative to working directory.
        encoding: Text encoding (default: utf-8).
        limit: Maximum lines to read (default: None for all).

    Returns:
        File contents as string.

    Raises:
        FileNotFoundError: If file doesn't exist.
        PermissionError: If insufficient permissions.
        ValueError: If path is outside working directory.

    Example:
        >>> content = read_file("main.py")
        >>> content = read_file("config.json", limit=100)
    """
    pass
```

### Inline Comments

Use sparingly - code should be self-documenting:

```python
# Good - explains "why"
if not path.startswith(working_dir):
    # Security: prevent directory traversal attacks
    raise ValueError("Path outside working directory")

# Avoid - explains "what"
x = y + 1  # increment y
```

## Code Organization

### Directory Structure

```
miu_code/
├── __init__.py              # Package initialization
├── __main__.py              # CLI entry point
├── agent/
│   ├── __init__.py
│   └── coding.py            # Main agent class
├── cli/
│   ├── __init__.py
│   └── entry.py             # CLI commands
├── acp/
│   ├── __init__.py
│   └── server.py            # ACP server
├── commands/
│   ├── __init__.py          # Command registry
│   └── *.md                 # Command templates
├── session/
│   ├── __init__.py
│   └── storage.py           # Session persistence
├── tools/
│   ├── __init__.py          # Tool exports
│   ├── bash.py
│   ├── read.py
│   ├── write.py
│   ├── edit.py
│   ├── glob.py
│   ├── grep.py
│   └── security.py          # Security utilities
└── tui/
    ├── __init__.py
    ├── app.py               # Main TUI app
    ├── app.tcss             # Styles
    ├── theme.py             # Color definitions
    └── widgets/
        ├── __init__.py
        └── *.py             # Widget implementations
```

### Module Organization

Within each module, organize code as follows:

```python
"""Module docstring."""

# Imports
from typing import ClassVar

# Constants
DEFAULT_TIMEOUT = 600
MAX_RETRIES = 3

# Type aliases
MessageType = dict[str, str]

# Exceptions
class CustomError(Exception):
    """Custom exception."""
    pass

# Classes
class MainClass:
    """Main class."""
    pass

# Functions
def helper_function() -> None:
    """Helper function."""
    pass

# Entry point
if __name__ == "__main__":
    helper_function()
```

## Error Handling

### Exception Hierarchy

Create custom exceptions in module:

```python
class MiuCodeError(Exception):
    """Base exception for miu-code."""
    pass

class ToolError(MiuCodeError):
    """Tool execution error."""
    pass

class PathError(MiuCodeError):
    """Path validation error."""
    pass
```

### Raising Exceptions

Include informative messages:

```python
# Good
if not file_exists:
    raise FileNotFoundError(f"File not found: {path}")

if not validate_path(path):
    raise ValueError(
        f"Path outside working directory: {path} "
        f"(working_dir: {working_dir})"
    )

# Avoid
if not file_exists:
    raise FileNotFoundError()

if not validate_path(path):
    raise ValueError("Invalid path")
```

### Exception Handling

Catch specific exceptions:

```python
# Good
try:
    content = read_file(path)
except FileNotFoundError:
    logger.error(f"File not found: {path}")
    raise
except PermissionError:
    logger.error(f"Permission denied: {path}")
    raise

# Avoid
try:
    content = read_file(path)
except Exception:
    pass  # Never swallow exceptions silently
```

### Async Exception Handling

Use try-finally for cleanup:

```python
async def process_query(self, query: str) -> None:
    """Process query with cleanup."""
    try:
        self._is_processing = True
        self.loading.start()
        async for event in self._agent.run_stream(query):
            await self._handle_event(event)
    finally:
        self._is_processing = False
        self.loading.stop()
```

## Testing Standards

### Test File Organization

```
tests/
├── __init__.py
├── test_code_tools.py       # Tool unit tests
├── test_tui_widgets.py      # Widget tests
├── test_agent.py            # Agent tests
└── fixtures/                # Test data
```

### Test Naming

- File: `test_*.py`
- Class: `Test*` (PascalCase)
- Method: `test_*` (snake_case)

```python
import pytest
from miu_code.tools import ReadTool

class TestReadTool:
    """Tests for ReadTool."""

    def test_read_existing_file(self, tmp_path):
        """Test reading existing file."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        # Test
        tool = ReadTool()
        result = tool.execute({"path": str(test_file)})

        # Assert
        assert result == "content"

    def test_read_missing_file_raises_error(self, tmp_path):
        """Test reading non-existent file raises error."""
        tool = ReadTool()
        with pytest.raises(FileNotFoundError):
            tool.execute({"path": "/non/existent/file.txt"})
```

### Fixtures & Setup

```python
import pytest
from pathlib import Path

@pytest.fixture
def tmp_workspace(tmp_path):
    """Create temporary workspace for tests."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "main.py").write_text("# Python file")
    (workspace / "config.json").write_text("{}")
    return workspace

def test_with_workspace(tmp_workspace):
    """Test using workspace fixture."""
    assert (tmp_workspace / "main.py").exists()
```

### Test Coverage

- Minimum coverage: **80%**
- Critical code (security, core logic): **95%+**
- Tools: **100%** (all paths tested)

```bash
pytest --cov=miu_code tests/
pytest --cov=miu_code --cov-report=html tests/
```

## Tools & Linting

### Essential Tools

1. **ruff** - Code formatter and linter
   ```bash
   ruff format .
   ruff check . --fix
   ```

2. **mypy** - Type checker
   ```bash
   mypy miu_code/
   ```

3. **pytest** - Test runner
   ```bash
   pytest tests/ -v
   ```

4. **pytest-cov** - Coverage reporting
   ```bash
   pytest tests/ --cov=miu_code
   ```

### Pre-commit Hooks

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        args: [--strict]
```

Install hooks:
```bash
pre-commit install
pre-commit run --all-files
```

### CI/CD Checks

Run before committing:

```bash
# Format
ruff format miu_code/ tests/

# Type check
mypy miu_code/

# Lint
ruff check miu_code/ tests/

# Test
pytest tests/ --cov=miu_code --cov-fail-under=80
```

## Contributing Checklist

- [ ] Code follows PEP 8 style guidelines
- [ ] All functions have type hints
- [ ] All public functions have docstrings
- [ ] Code passes ruff format and check
- [ ] Code passes mypy type checking
- [ ] Tests added for new functionality
- [ ] Test coverage >= 80%
- [ ] No breaking changes (or documented)
- [ ] Commit message follows conventional commits

## Examples

### Good Code Example

```python
"""File reading tool for miu-code."""

import os
from pathlib import Path


class FileReadError(Exception):
    """Error reading file."""
    pass


def read_file(
    path: str,
    working_dir: str = ".",
    encoding: str = "utf-8",
    limit: int | None = None,
) -> str:
    """Read file contents.

    Args:
        path: File path relative to working directory.
        working_dir: Base directory for security validation.
        encoding: Text encoding (default: utf-8).
        limit: Maximum lines to read (default: all).

    Returns:
        File contents as string.

    Raises:
        FileNotFoundError: If file doesn't exist.
        FileReadError: If reading fails.
        ValueError: If path is outside working directory.
    """
    # Validate path for security
    full_path = Path(working_dir) / path
    if not str(full_path.resolve()).startswith(str(Path(working_dir).resolve())):
        raise ValueError(f"Path outside working directory: {path}")

    # Read file
    try:
        with open(full_path, "r", encoding=encoding) as f:
            lines = f.readlines()
            if limit:
                lines = lines[:limit]
            return "".join(lines)
    except FileNotFoundError:
        raise
    except Exception as e:
        raise FileReadError(f"Failed to read {path}: {e}")
```

## References

- [PEP 8 - Python Style Guide](https://pep8.org/)
- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [Type Hints (PEP 484)](https://peps.python.org/pep-0484/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
