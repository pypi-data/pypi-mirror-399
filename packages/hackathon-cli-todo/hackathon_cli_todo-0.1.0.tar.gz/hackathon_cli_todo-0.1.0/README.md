# Hackathon CLI Todo App

A simple, elegant command-line todo list application that helps you manage your tasks efficiently from the terminal.

## Features

- ✅ Add tasks with descriptive titles
- 📋 List all tasks with completion status
- ✔️ Mark tasks as complete
- 🗑️ Delete tasks
- 🎮 Interactive menu mode
- ⌨️ Direct command support
- 💾 In-memory storage (simple and fast)
- 🚀 Zero external dependencies

## Installation

### Install via pip

```bash
pip install hackathon-cli-todo
```

### Install via uv (faster)

```bash
uv pip install hackathon-cli-todo
```

## Usage

### Interactive Mode

Run the interactive menu:

```bash
todo
```

You'll see:
```
=== Todo App ===
1. Add a task
2. List tasks
3. Complete a task
4. Delete a task
5. Exit
```

### Direct Commands

You can also use direct commands without entering the interactive mode:

```bash
# Add a new task
todo add "Buy groceries"

# List all tasks
todo list

# Complete a task (by number)
todo complete 1

# Delete a task (by number)
todo delete 1
```

### Examples

```bash
# Add multiple tasks
todo add "Write project report"
todo add "Call client meeting"
todo add "Review pull requests"

# List your tasks
todo list
# Output:
# Your tasks:
# 1. [ ] Write project report
# 2. [ ] Call client meeting
# 3. [ ] Review pull requests

# Complete the first task
todo complete 1

# Delete the second task
todo delete 2
```

## Requirements

- Python 3.11 or higher

## Development

For local development:

```bash
# Clone the repository
git clone <repo-url>
cd PHASE-I-CLI-Todo-app

# Install in editable mode
pip install -e .

# Run tests
pytest

# Run with type checking
mypy src/
```

## Project Structure

```
src/
├── __init__.py     # Package initialization
├── __main__.py     # Module entry point
├── main.py         # CLI application
├── models.py       # Data models
└── todo.py         # Service layer
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Created as part of the Hackathon II Todo App project
