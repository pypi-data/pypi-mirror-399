"""Todo service for managing tasks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .models import IndexOutOfBoundsError, Task, TaskStatus, ValidationError

if TYPE_CHECKING:
    pass


class TodoService:
    """Service for managing todo tasks."""

    def __init__(self) -> None:
        """Initialize the todo service with an empty task list."""
        self._tasks: list[Task] = []
        self._next_id: int = 1

    def add_task(self, title: str) -> Task:
        """Add a new task.

        Args:
            title: The task title.

        Returns:
            The created Task.

        Raises:
            ValidationError: If the title is empty or invalid.
        """
        self._validate_title(title)
        task = Task(
            id=self._next_id,
            title=title,
            status=TaskStatus.PENDING,
        )
        self._tasks.append(task)
        self._next_id += 1
        return task

    def list_tasks(self) -> list[Task]:
        """List all tasks.

        Returns:
            List of all tasks.
        """
        return list(self._tasks)

    def complete_task(self, index: int) -> Task:
        """Mark a task as complete.

        Args:
            index: 1-based task index.

        Returns:
            The updated Task.

        Raises:
            IndexOutOfBoundsError: If the index is invalid.
        """
        old_task = self._get_task_by_index(index)
        new_task = Task(
            id=old_task.id,
            title=old_task.title,
            status=TaskStatus.COMPLETED,
            created_at=old_task.created_at,
        )
        # Replace the old task with the new one
        self._tasks[index - 1] = new_task
        return new_task

    def delete_task(self, index: int) -> None:
        """Delete a task.

        Args:
            index: 1-based task index.

        Raises:
            IndexOutOfBoundsError: If the index is invalid.
        """
        task = self._get_task_by_index(index)
        self._tasks.remove(task)

    def _validate_title(self, title: str) -> None:
        """Validate a task title.

        Args:
            title: The title to validate.

        Raises:
            ValidationError: If the title is invalid.
        """
        if not title or not title.strip():
            raise ValidationError("Task title cannot be empty.")
        if len(title) > 200:
            raise ValidationError("Task title must be under 200 characters.")

    def _get_task_by_index(self, index: int) -> Task:
        """Get a task by 1-based index.

        Args:
            index: 1-based task index.

        Returns:
            The Task at that index.

        Raises:
            IndexOutOfBoundsError: If the index is invalid.
        """
        if index < 1 or index > len(self._tasks):
            raise IndexOutOfBoundsError(f"Invalid task number: {index}.")
        return self._tasks[index - 1]
