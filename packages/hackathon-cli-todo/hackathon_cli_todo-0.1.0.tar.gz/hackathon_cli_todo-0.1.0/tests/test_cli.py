"""Integration tests for CLI commands."""

from __future__ import annotations

import subprocess
import sys


class TestCLIAddCommand:
    """Integration tests for the add command."""

    def test_add_task_via_cli(self) -> None:
        """Adding a task via CLI should succeed."""
        result = subprocess.run(
            [sys.executable, "-m", "src", "add", "Buy milk"],
            capture_output=True,
            text=True,
        )
        # CLI should succeed
        assert result.returncode == 0

    def test_add_task_shows_confirmation(self) -> None:
        """Adding a task should show a confirmation message."""
        result = subprocess.run(
            [sys.executable, "-m", "src", "add", "Buy milk"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Buy milk" in result.stdout


class TestCLIListCommand:
    """Integration tests for the list command."""

    def test_list_empty_shows_message(self) -> None:
        """Listing tasks when empty should show helpful message."""
        result = subprocess.run(
            [sys.executable, "-m", "src", "list"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "No tasks yet" in result.stdout or "Add one" in result.stdout


class TestCLICompleteCommand:
    """Integration tests for the complete command."""

    def test_complete_invalid_index_shows_error(self) -> None:
        """Completing invalid index should show error."""
        result = subprocess.run(
            [sys.executable, "-m", "src", "complete", "99"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "Invalid task number" in result.stderr


class TestCLIDeleteCommand:
    """Integration tests for the delete command."""

    def test_delete_invalid_index_shows_error(self) -> None:
        """Deleting invalid index should show error."""
        result = subprocess.run(
            [sys.executable, "-m", "src", "delete", "99"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "Invalid task number" in result.stderr
