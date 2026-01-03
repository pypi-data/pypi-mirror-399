# Data Model: CLI Todo App - Phase 1

**Feature Branch**: `001-cli-todo-app` | **Date**: 2025-12-30
**Source**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Task Entity

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | `int` | 1-based sequential, immutable | Unique identifier for display and operations |
| `title` | `str` | 1-200 chars, non-empty, stripped | Task description |
| `status` | `TaskStatus` | enum: `PENDING`, `COMPLETED` | Current state |
| `created_at` | `datetime` | auto-set on creation | Timestamp of creation |

### Status Enum

```python
from enum import Enum, auto

class TaskStatus(Enum):
    """Task completion status."""
    PENDING = auto()
    COMPLETED = auto()
```

### Validation Rules

1. **Title validation** (FR-005):
   - Must not be `None` or empty after `strip()`
   - Must not be whitespace-only
   - Max 200 characters

2. **Index validation** (FR-006):
   - Task indices are 1-based for user display
   - Internal list uses 0-based indexing
   - Index must be within bounds `[1, len(tasks)]`

### State Transitions

```text
[PENDING] --mark_complete(id)--> [COMPLETED]
  |
  +-- delete(id) --> [REMOVED] (list removed)
```

Notes:
- `COMPLETED` → `COMPLETED` is idempotent (no-op with info message)
- No transitions back to `PENDING` (Phase 1 scope)

## Data Structures

### In-Memory Collection

```python
from typing import TypedDict

class TaskList(TypedDict):
    """In-memory task collection."""
    tasks: list[Task]
    next_id: int  # For sequential ID generation
```

### Error Types

| Error | Condition | Message | Exit Code |
|-------|-----------|---------|-----------|
| `ValidationError` | Invalid title/input | "Task title cannot be empty." | 1 |
| `IndexError` | Invalid task number | "Invalid task number: {n}." | 1 |
| `DuplicateError` | Duplicate title | "A task with this title already exists." | 1 |

## File Structure

```
src/
└── models/
    ├── __init__.py
    ├── task.py          # Task dataclass + TaskStatus enum
    └── errors.py        # Custom exception classes
```

### task.py

```python
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class TaskStatus(Enum):
    """Task completion status."""
    PENDING = "pending"
    COMPLETED = "completed"


@dataclass(frozen=True, slots=True)
class Task:
    """Represents a single todo item."""
    id: int
    title: str
    status: TaskStatus
    created_at: datetime

    def __post_init__(self) -> None:
        """Validate task after initialization."""
        if not self.title or not self.title.strip():
            raise ValueError("Task title cannot be empty.")
        if len(self.title) > 200:
            raise ValueError("Task title must be under 200 characters.")
```

### errors.py

```python
from __future__ import annotations


class TodoError(Exception):
    """Base exception for todo app errors."""
    message: str
    exit_code: int = 1

    def __init__(self, message: str, exit_code: int = 1) -> None:
        self.message = message
        self.exit_code = exit_code
        super().__init__(message)


class ValidationError(TodoError):
    """Raised when task validation fails."""
    exit_code: int = 1


class IndexOutOfBoundsError(TodoError):
    """Raised when task index is invalid."""
    exit_code: int = 1
```

## Relationships

```
TaskList
  └── contains: Task[*]
```

The `TaskList` is a simple Python list stored in `TodoService`. No external persistence in Phase 1.
