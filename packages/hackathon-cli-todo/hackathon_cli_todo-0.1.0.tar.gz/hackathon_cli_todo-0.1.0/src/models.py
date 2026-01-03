"""Task data models and custom exceptions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum, auto


class TaskStatus(Enum):
    """Task completion status."""

    PENDING = auto()
    COMPLETED = auto()


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


@dataclass(frozen=True, slots=True)
class Task:
    """Represents a single todo item."""

    id: int
    title: str
    status: TaskStatus
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Validate task after initialization."""
        if not self.title or not self.title.strip():
            raise ValueError("Task title cannot be empty.")
        if len(self.title) > 200:
            raise ValueError("Task title must be under 200 characters.")
