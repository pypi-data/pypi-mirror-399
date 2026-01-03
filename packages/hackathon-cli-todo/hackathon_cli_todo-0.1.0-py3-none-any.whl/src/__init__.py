"""CLI Todo App - A console-based todo list application."""

__version__ = "0.1.0"

from .main import main
from .models import (
    IndexOutOfBoundsError,
    Task,
    TaskStatus,
    TodoError,
    ValidationError,
)
from .todo import TodoService

__all__ = [
    "main",
    "TodoService",
    "Task",
    "TaskStatus",
    "TodoError",
    "ValidationError",
    "IndexOutOfBoundsError",
]
