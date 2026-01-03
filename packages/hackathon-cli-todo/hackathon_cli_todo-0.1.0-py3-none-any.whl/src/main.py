"""CLI entry point for the todo application."""

from __future__ import annotations
import argparse
import sys
from .models import IndexOutOfBoundsError, TaskStatus, ValidationError
from .todo import TodoService

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.
    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        prog="todo",
        description="A simple command-line todo list application.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", nargs="+", help="Task title")

    # List command
    subparsers.add_parser("list", help="List all tasks")

    # Complete command
    complete_parser = subparsers.add_parser("complete", help="Mark a task as complete")
    complete_parser.add_argument("index", type=int, help="Task number to complete")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("index", type=int, help="Task number to delete")

    return parser.parse_args()


def main() -> int:
    """Run the CLI todo application.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    args = parse_args()

    # If no command provided, run interactive mode
    if args.command is None:
        service = TodoService()
        return run_menu(service)

    service = TodoService()

    match args.command:
        case "add":
            title = " ".join(args.title)
            return handle_add(service, title)
        case "list":
            return handle_list(service)
        case "complete":
            return handle_complete(service, args.index)
        case "delete":
            return handle_delete(service, args.index)
        case _:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            return 1

def run_menu(service: TodoService) -> int:
    """Run the main menu loop.
    Args:
        service: The TodoService instance.
    Returns:
        Exit code.
    """
    while True:
        print_menu()
        choice = input("Enter your choice: ").strip()

        match choice:
            case "1" | "add":
                handle_add(service, "")
            case "2" | "list":
                handle_list(service)
            case "3" | "complete":
                handle_complete(service, 0)
            case "4" | "delete":
                handle_delete(service, 0)
            case "5" | "exit" | "quit":
                print("Goodbye!")
                return 0
            case "":
                continue
            case _:
                print("Invalid choice. Please enter 1-5.", file=sys.stderr)


def print_menu() -> None:
    """Print the main menu."""
    print("\n=== Todo App ===")
    print("1. Add a task")
    print("2. List tasks")
    print("3. Complete a task")
    print("4. Delete a task")
    print("5. Exit")


def handle_add(service: TodoService, title: str = "") -> int:
    """Handle adding a task.

    Args:
        service: The TodoService instance.
        title: Optional title from command line.

    Returns:
        Exit code.
    """
    if not title:
        title = input("Enter task title: ").strip()

    if not title:
        print("Task title cannot be empty.", file=sys.stderr)
        return 1

    try:
        task = service.add_task(title)
        print(f"Added task: {task.title}")
        return 0
    except ValidationError as e:
        print(f"Error: {e.message}", file=sys.stderr)
        return 1


def handle_list(service: TodoService) -> int:
    """Handle listing tasks.

    Args:
        service: The TodoService instance.

    Returns:
        Exit code.
    """
    tasks = service.list_tasks()

    if not tasks:
        print("No tasks yet. Add one!")
        return 0

    print("\nYour tasks:")
    for i, task in enumerate(tasks, start=1):
        status = "[x]" if task.status == TaskStatus.COMPLETED else "[ ]"
        print(f"{i}. {status} {task.title}")

    return 0


def handle_complete(service: TodoService, index: int = 0) -> int:
    """Handle completing a task.

    Args:
        service: The TodoService instance.
        index: Optional index from command line.

    Returns:
        Exit code.
    """
    if index <= 0:
        index_str = input("Enter task number to complete: ").strip()
        if not index_str:
            print("Please enter a task number.", file=sys.stderr)
            return 1
        try:
            index = int(index_str)
        except ValueError:
            print("Invalid task number.", file=sys.stderr)
            return 1

    try:
        task = service.complete_task(index)
        print(f"Completed: {task.title}")
        return 0
    except IndexOutOfBoundsError as e:
        print(f"Error: {e.message}", file=sys.stderr)
        return 1


def handle_delete(service: TodoService, index: int = 0) -> int:
    """Handle deleting a task.

    Args:
        service: The TodoService instance.
        index: Optional index from command line.

    Returns:
        Exit code.
    """
    if index <= 0:
        index_str = input("Enter task number to delete: ").strip()
        if not index_str:
            print("Please enter a task number.", file=sys.stderr)
            return 1
        try:
            index = int(index_str)
        except ValueError:
            print("Invalid task number.", file=sys.stderr)
            return 1

    try:
        service.delete_task(index)
        print("Task deleted.")
        return 0
    except IndexOutOfBoundsError as e:
        print(f"Error: {e.message}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
