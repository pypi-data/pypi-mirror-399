# Quickstart: CLI Todo App - Phase 1

**Feature Branch**: `001-cli-todo-app` | **Date**: 2025-12-30
**Source**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Prerequisites

- Python 3.11+
- pip (comes with Python)
- uv (recommended for faster installation)

## Installation

### Method 1: Global Installation with pip

```bash
# Navigate to project directory
cd PHASE-I-CLI-Todo-app

# Install globally using pip
pip install -e .
```

### Method 2: Global Installation with uv (Faster)

```bash
# Navigate to project directory
cd PHASE-I-CLI-Todo-app

# Install globally using uv
uv pip install -e .
```

### Method 3: Development Installation

```bash
# Clone and setup
git clone <repo-url>
cd Hackthon-II-Todo-App/PHASE-I-CLI-Todo-app

# Install with uv (recommended)
uv sync

# OR install with pip
pip install -e .
```

## Running the App

### Using the Global `todo` Command (Recommended)

After installation, you can run the app from anywhere:

```bash
# Run interactive menu
todo

# Or use direct commands
todo add "Buy groceries"
todo list
todo complete 1
todo delete 1
```

### Using uv run (Development Mode)

```bash
uv run python -m src
```

### Using python -m (Standard Mode)

```bash
python -m src
```

## Project Structure

```
src/
├── __main__.py    # Module entry point (python -m src)
├── __init__.py     # Package initialization
├── main.py        # CLI application entry point
├── models.py      # Task data model and error definitions
└── todo.py        # Todo service with CRUD operations

tests/
├── __init__.py     # Test package initialization
├── test_models.py  # Model unit tests
├── test_todo.py    # Service layer unit tests
└── test_cli.py     # CLI integration tests

pyproject.toml           # uv project config
uv.lock                  # Dependency lock file
README.md                # User-facing documentation
```

## Development Workflow

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_models.py
uv run pytest tests/test_todo.py
uv run pytest tests/test_cli.py
```

### Type Checking

```bash
uv run mypy src/
```

### Linting

```bash
uv run ruff check src/
```

### Formatting

```bash
uv run ruff format src/
```

## Key Files

### Source Code

| File | Purpose |
|------|---------|
| `src/models.py` | `Task` dataclass, `TaskStatus` enum, and error definitions (`TodoError`, `ValidationError`, `IndexOutOfBoundsError`) |
| `src/todo.py` | `TodoService` class with CRUD methods |
| `src/main.py` | CLI application with menu loop and command dispatch |
| `src/__main__.py` | Module entry point (`python -m src`) |

### Test Files

| File | Purpose |
|------|---------|
| `tests/test_models.py` | Task model unit tests |
| `tests/test_todo.py` | Service layer unit tests |
| `tests/test_cli.py` | End-to-end CLI integration tests |

## Adding a New Task

```python
from src.models import Task, TaskStatus
from src.todo import TodoService
from datetime import datetime

service = TodoService()
service.add_task("Buy groceries")
tasks = service.list_tasks()
```

## Architecture Overview

```
User Input (stdin)
       |
       v
┌─────────────────┐
│  TodoApp (main) │  # Menu loop + command dispatch
└────────┬────────┘
         |
         v
┌─────────────────┐
│  TodoService    │  # Business logic (CRUD)
└────────┬────────┘
         |
         v
┌─────────────────┐
│  In-Memory List │  # Python list[Task]
└─────────────────┘
```

## Common Tasks

### Add a test

```bash
# Create test file in tests directory
touch tests/test_new_feature.py
```

### Run CI checks locally

```bash
uv run pytest --cov=src
uv run mypy src/
uv run ruff check src/
```

## Next Steps

1. Run `uv sync` to install dependencies
2. Implement `src/models.py` (Task, TaskStatus, error classes)
3. Implement `src/todo.py` (TodoService with CRUD operations)
4. Implement `src/main.py` (CLI application with menu loop)
5. Write unit tests for each module (tests/test_models.py, tests/test_todo.py)
6. Write integration tests for CLI flow (tests/test_cli.py)
7. Run full test suite with coverage

---

## Quick Start Guide for Global Users

### Step 1: Install the Application

Open your terminal and navigate to the project directory:

```bash
cd D:\Agentic-Hackthon\Hackthon-II-Todo-App\PHASE-I-CLI-Todo-app
```

Install the application globally using pip:

```bash
pip install -e .
```

*Note: The `-e` flag installs the package in "editable" mode, which means changes to the source code will be immediately reflected without reinstalling.*

### Step 2: Verify Installation

Check if the `todo` command is available:

```bash
todo --help
```

You should see the help message with available commands.

### Step 3: Run the Application

Now you can use the `todo` command from anywhere:

**Interactive Mode:**
```bash
todo
```

This will launch the interactive menu where you can:
1. Add tasks
2. List tasks
3. Complete tasks
4. Delete tasks
5. Exit

**Direct Commands:**
```bash
# Add a task
todo add "Buy groceries"

# List all tasks
todo list

# Complete a task (by number)
todo complete 1

# Delete a task (by number)
todo delete 1
```

### Troubleshooting

**Command not found:**
- Make sure you added Python's Scripts directory to your PATH
- On Windows: Add `%USERPROFILE%\AppData\Local\Programs\Python\Python311\Scripts` to PATH
- Reopen your terminal after updating PATH

**Permission errors (Linux/Mac):**
```bash
pip install -e . --user
```

**Uninstall the package:**
```bash
pip uninstall cli-todo-app
```

### Reinstalling After Changes

Since we installed with `-e` flag, changes are automatically picked up. If you need to reinstall:

```bash
pip uninstall cli-todo-app
pip install -e .
```
  