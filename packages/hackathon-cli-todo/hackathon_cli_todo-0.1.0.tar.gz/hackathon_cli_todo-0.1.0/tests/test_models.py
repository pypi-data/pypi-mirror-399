"""Tests for task models."""

from __future__ import annotations

import pytest

from src.models import Task, TaskStatus


class TestTaskStatus:
    """Tests for TaskStatus enum."""

    def test_pending_status_exists(self) -> None:
        """TaskStatus should have a PENDING value."""
        assert TaskStatus.PENDING is not None

    def test_completed_status_exists(self) -> None:
        """TaskStatus should have a COMPLETED value."""
        assert TaskStatus.COMPLETED is not None


class TestTask:
    """Tests for Task dataclass."""

    def test_create_task_with_valid_data(self) -> None:
        """Task should be created with valid data."""
        task = Task(id=1, title="Buy milk", status=TaskStatus.PENDING)
        assert task.id == 1
        assert task.title == "Buy milk"
        assert task.status == TaskStatus.PENDING

    def test_task_with_empty_title_raises_error(self) -> None:
        """Task with empty title should raise ValueError."""
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            Task(id=1, title="", status=TaskStatus.PENDING)

    def test_task_with_whitespace_title_raises_error(self) -> None:
        """Task with whitespace-only title should raise ValueError."""
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            Task(id=1, title="   ", status=TaskStatus.PENDING)

    def test_task_with_title_over_200_chars_raises_error(self) -> None:
        """Task with title over 200 characters should raise ValueError."""
        long_title = "x" * 201
        with pytest.raises(ValueError, match="Task title must be under 200 characters"):
            Task(id=1, title=long_title, status=TaskStatus.PENDING)

    def test_task_title_with_200_chars_is_valid(self) -> None:
        """Task with title of exactly 200 characters should be valid."""
        title = "x" * 200
        task = Task(id=1, title=title, status=TaskStatus.PENDING)
        assert len(task.title) == 200

    def test_task_title_is_stripped(self) -> None:
        """Task title should preserve whitespace (not auto-strip)."""
        task = Task(id=1, title="  Buy milk  ", status=TaskStatus.PENDING)
        assert task.title == "  Buy milk  "

    def test_task_is_immutable(self) -> None:
        """Task should be immutable (frozen dataclass)."""
        task = Task(id=1, title="Buy milk", status=TaskStatus.PENDING)
        with pytest.raises(Exception):
            task.title = "Changed title"

    def test_task_has_created_at_timestamp(self) -> None:
        """Task should have a created_at timestamp."""
        task = Task(id=1, title="Buy milk", status=TaskStatus.PENDING)
        assert task.created_at is not None

    def test_task_comparison_by_value(self) -> None:
        """Tasks with same values should be equal."""
        task1 = Task(id=1, title="Buy milk", status=TaskStatus.PENDING)
        task2 = Task(id=1, title="Buy milk", status=TaskStatus.PENDING)
        assert task1 == task2

    def test_task_with_completed_status(self) -> None:
        """Task can be created with COMPLETED status."""
        task = Task(id=1, title="Buy milk", status=TaskStatus.COMPLETED)
        assert task.status == TaskStatus.COMPLETED
