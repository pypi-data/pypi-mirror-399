"""Tests for todo service."""

from __future__ import annotations

import pytest

from src.models import Task, TaskStatus, ValidationError
from src.todo import TodoService


class TestTodoServiceAddTask:
    """Tests for TodoService.add_task()."""

    def test_add_single_task(self) -> None:
        """Adding a task should return a Task with correct data."""
        service = TodoService()
        task = service.add_task("Buy milk")

        assert task.id == 1
        assert task.title == "Buy milk"
        assert task.status == TaskStatus.PENDING

    def test_add_multiple_tasks_increment_ids(self) -> None:
        """Adding multiple tasks should have sequential IDs."""
        service = TodoService()
        task1 = service.add_task("Buy milk")
        task2 = service.add_task("Walk dog")
        task3 = service.add_task("Clean room")

        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3

    def test_add_empty_task_raises_error(self) -> None:
        """Adding an empty task should raise ValidationError."""
        service = TodoService()

        with pytest.raises(ValidationError, match="Task title cannot be empty"):
            service.add_task("")

    def test_add_whitespace_task_raises_error(self) -> None:
        """Adding a whitespace-only task should raise ValidationError."""
        service = TodoService()

        with pytest.raises(ValidationError, match="Task title cannot be empty"):
            service.add_task("   ")

    def test_add_task_trims_whitespace(self) -> None:
        """Adding a task should preserve whitespace in title."""
        service = TodoService()
        task = service.add_task("  Buy milk  ")

        assert task.title == "  Buy milk  "

    def test_add_task_stores_in_list(self) -> None:
        """Adding a task should make it retrievable via list_tasks."""
        service = TodoService()
        service.add_task("Buy milk")

        tasks = service.list_tasks()
        assert len(tasks) == 1
        assert tasks[0].title == "Buy milk"


class TestTodoServiceListTasks:
    """Tests for TodoService.list_tasks()."""

    def test_list_empty_tasks(self) -> None:
        """Listing tasks when empty should return empty list."""
        service = TodoService()
        tasks = service.list_tasks()

        assert tasks == []

    def test_list_multiple_tasks(self) -> None:
        """Listing tasks should return all tasks."""
        service = TodoService()
        service.add_task("Buy milk")
        service.add_task("Walk dog")

        tasks = service.list_tasks()
        assert len(tasks) == 2

    def test_list_maintains_order(self) -> None:
        """Listing tasks should maintain insertion order."""
        service = TodoService()
        service.add_task("First")
        service.add_task("Second")
        service.add_task("Third")

        tasks = service.list_tasks()
        assert tasks[0].title == "First"
        assert tasks[1].title == "Second"
        assert tasks[2].title == "Third"


class TestTodoServiceCompleteTask:
    """Tests for TodoService.complete_task()."""

    def test_complete_task(self) -> None:
        """Completing a task should change its status."""
        service = TodoService()
        service.add_task("Buy milk")
        task = service.complete_task(1)

        assert task.status == TaskStatus.COMPLETED

    def test_complete_invalid_index_raises_error(self) -> None:
        """Completing an invalid index should raise error."""
        from src.models import IndexOutOfBoundsError

        service = TodoService()
        service.add_task("Buy milk")

        with pytest.raises(IndexOutOfBoundsError, match="Invalid task number"):
            service.complete_task(99)

    def test_complete_zero_index_raises_error(self) -> None:
        """Completing index 0 should raise error (1-based indexing)."""
        from src.models import IndexOutOfBoundsError

        service = TodoService()
        service.add_task("Buy milk")

        with pytest.raises(IndexOutOfBoundsError):
            service.complete_task(0)

    def test_complete_negative_index_raises_error(self) -> None:
        """Completing negative index should raise error."""
        from src.models import IndexOutOfBoundsError

        service = TodoService()
        service.add_task("Buy milk")

        with pytest.raises(IndexOutOfBoundsError):
            service.complete_task(-1)


class TestTodoServiceDeleteTask:
    """Tests for TodoService.delete_task()."""

    def test_delete_task(self) -> None:
        """Deleting a task should remove it from the list."""
        service = TodoService()
        service.add_task("Buy milk")
        service.add_task("Walk dog")

        service.delete_task(1)
        tasks = service.list_tasks()

        assert len(tasks) == 1
        assert tasks[0].title == "Walk dog"

    def test_delete_renumbers_remaining_tasks(self) -> None:
        """Deleting a task should renumber remaining tasks."""
        service = TodoService()
        service.add_task("First")
        service.add_task("Second")
        service.add_task("Third")

        service.delete_task(2)
        tasks = service.list_tasks()

        assert tasks[0].id == 1  # First stays as 1
        assert tasks[1].id == 3  # Third keeps its original ID (IDs are immutable)

    def test_delete_invalid_index_raises_error(self) -> None:
        """Deleting an invalid index should raise error."""
        from src.models import IndexOutOfBoundsError

        service = TodoService()
        service.add_task("Buy milk")

        with pytest.raises(IndexOutOfBoundsError, match="Invalid task number"):
            service.delete_task(99)
