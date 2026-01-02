# Todo Evolution 🚀

**Professional in-memory Python console todo app with beautiful TUI**

A modern, feature-rich task management application that combines the power of a command-line interface with an intuitive, arrow-key navigable TUI dashboard. Built with Python 3.13+ and designed for developers who love working in the terminal.

[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Coverage](https://img.shields.io/badge/coverage-90%25+-brightgreen.svg)](https://github.com/yourusername/todo-evolution)

## ✨ Features

- **Beautiful TUI**: Large ASCII banner "TODO EVOLUTION", rich-formatted tables, distinct colors
- **Arrow-Key Navigation**: Intuitive menu system powered by questionary
- **Dual Modes**:
  - **Interactive Mode**: Dashboard with visual feedback (default - just run `todo`)
  - **Command Mode**: Direct CLI operations for power users (`todo add "Task"`)
- **5 Core Operations**: Add, List, Update, Delete, Mark Complete/Incomplete
- **Pure Python Services**: Reusable as a library without CLI dependencies
- **In-Memory Storage**: Fast, simple, no persistence overhead
- **90%+ Test Coverage**: Comprehensive unit and integration tests
- **Type-Safe**: Full type hints with mypy validation
- **Developer-Friendly**: Clean API, excellent error messages

## 📦 Installation

### From PyPI (coming soon)

```bash
pip install danial-todo
```

### From Source

```bash
# Clone the repository
git clone https://github.com/daniyalaneeq/todo-evolution.git
cd todo-evolution

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

## 🚀 Quick Start

### Interactive Mode (Default)

Simply run `todo` to launch the TUI dashboard:

```bash
todo
```

**You'll see:**
```
   _____ ___  ____   ___
  |_   _/ _ \|  _ \ / _ \
    | || | | | | | | | | |
    | || |_| | |_| | |_| |
    |_| \___/|____/ \___/
  _____     _____ _   _ _____ ___ ___  _   _
 | __\ \   / / _ \ | | | |_   _|_ _/ _ \| \ | |
 |  _|\ \ / / | | | | | |   | |  | | | | |  \| |
 | |___\ V /| |_| | |_| |   | |  | | |_| | |\  |
 |_____\_/  \___/|____/|_|   |_| |___\___/|_| \_|

What would you like to do?
❯ Add Task
  List Tasks
  Update Task
  Delete Task
  Mark Complete/Incomplete
  Exit
```

**Navigation:**
- ⬆️ **Up Arrow**: Move selection up
- ⬇️ **Down Arrow**: Move selection down
- **Enter**: Confirm selection
- **Ctrl+C**: Exit

### Command Mode (Power Users)

Execute operations directly from the command line:

```bash
# Add tasks
todo add "Buy groceries"
todo add "Write documentation"
todo add "Deploy application"

# List all tasks
todo list
# Output:
# ┌────┬───────────────────┬────────┐
# │ ID │ Title             │ Status │
# ├────┼───────────────────┼────────┤
# │  1 │ Buy groceries     │   ✗    │
# │  2 │ Write documentation│  ✗    │
# │  3 │ Deploy application│   ✗    │
# └────┴───────────────────┴────────┘

# Update a task
todo update 1 "Buy organic groceries"

# Mark task complete
todo complete 1

# Mark task incomplete
todo incomplete 1

# Delete a task
todo delete 2

# Get help
todo --help
```

## 💻 Usage Examples

### Interactive Mode Workflow

```bash
# Launch interactive mode
todo

# Follow the prompts:
# 1. Select "Add Task"
# 2. Enter: "Prepare presentation"
# 3. Select "List Tasks" to verify
# 4. Select "Mark Complete/Incomplete" and enter task ID
# 5. Select "Exit" when done
```

### Command Mode Workflow

```bash
# Quick task management
todo add "Morning standup at 9am"
todo add "Code review PR #123"
todo add "Deploy staging environment"

# Check your tasks
todo list

# Complete tasks as you go
todo complete 1
todo complete 2

# Update task details
todo update 3 "Deploy staging and notify team"

# Clean up completed tasks
todo delete 1
todo delete 2

# Check final state
todo list
```

### Library Usage (Programmatic API)

Use Todo Evolution as a Python library in your own applications:

```python
from todo_evolution import TaskService, Task

# Initialize service
service = TaskService()

# Add tasks
task1 = service.add_task("Deploy app to production")
task2 = service.add_task("Run database migrations")
task3 = service.add_task("Update monitoring dashboards")

print(f"Created task {task1.id}: {task1.title}")

# List all tasks
all_tasks = service.get_all_tasks()
for task in all_tasks:
    status = "✓" if task.status else "✗"
    print(f"[{status}] {task.id}: {task.title}")

# Get specific task
task = service.get_by_id(1)
if task:
    print(f"Found: {task.title}")

# Update task
updated = service.update_task(1, "Deploy app to production (urgent)")
print(f"Updated: {updated.title}")

# Mark complete
completed = service.toggle_status(2)
print(f"Task {completed.id} is now: {'complete' if completed.status else 'incomplete'}")

# Delete task
deleted = service.delete_task(3)
print(f"Deletion successful: {deleted}")

# Final count
remaining = service.get_all_tasks()
print(f"Total tasks remaining: {len(remaining)}")
```

**Output:**
```
Created task 1: Deploy app to production
[✗] 1: Deploy app to production
[✗] 2: Run database migrations
[✗] 3: Update monitoring dashboards
Found: Deploy app to production
Updated: Deploy app to production (urgent)
Task 2 is now: complete
Deletion successful: True
Total tasks remaining: 2
```

## 📚 API Reference

### TaskService

**Core business logic service for task management.**

#### Methods

##### `__init__() -> None`
Initialize a new TaskService with empty state.

```python
service = TaskService()
```

##### `add_task(title: str) -> Task`
Create a new task with auto-assigned ID.

**Parameters:**
- `title` (str): Task description (non-empty)

**Returns:** `Task` object with id, title, and status=False

**Raises:** `ValueError` if title is empty

```python
task = service.add_task("Buy milk")
assert task.id == 1
assert task.status == False
```

##### `get_all_tasks() -> list[Task]`
Retrieve all tasks in creation order.

**Returns:** List of Task objects (may be empty)

```python
tasks = service.get_all_tasks()
for task in tasks:
    print(task.title)
```

##### `get_by_id(task_id: int) -> Task | None`
Retrieve a specific task by ID.

**Parameters:**
- `task_id` (int): Task identifier

**Returns:** Task if found, None otherwise

```python
task = service.get_by_id(1)
if task:
    print(task.title)
```

##### `update_task(task_id: int, new_title: str) -> Task`
Update the title of an existing task.

**Parameters:**
- `task_id` (int): Task identifier
- `new_title` (str): New description (non-empty)

**Returns:** Updated Task object

**Raises:** `ValueError` if task not found or title is empty

```python
task = service.update_task(1, "Buy organic milk")
```

##### `delete_task(task_id: int) -> bool`
Remove a task from the collection.

**Parameters:**
- `task_id` (int): Task identifier

**Returns:** True if deleted, False if not found

```python
success = service.delete_task(1)
```

##### `toggle_status(task_id: int) -> Task`
Toggle task completion status (complete ↔ incomplete).

**Parameters:**
- `task_id` (int): Task identifier

**Returns:** Updated Task object with toggled status

**Raises:** `ValueError` if task not found

```python
task = service.toggle_status(1)
print("Complete" if task.status else "Incomplete")
```

### Task

**Data model representing a todo item.**

#### Attributes

- `id` (int): Unique auto-incrementing identifier
- `title` (str): Task description (1-500 characters)
- `status` (bool): Completion state (False=incomplete, True=complete)

```python
from todo_evolution.models import Task

task = Task(id=1, title="Example task", status=False)
print(f"{task.id}: {task.title} - {task.status}")
```

## 🧪 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/todo-evolution.git
cd todo-evolution

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install with dev dependencies
pip install -e ".[dev]"
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/todo_evolution --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_task_service.py -v

# Run integration tests only
pytest tests/integration/ -v
```

### Code Quality

```bash
# Format code with black
black src/ tests/

# Lint with ruff
ruff check src/ tests/

# Type check with mypy
mypy src/

# Run all quality checks
black src/ tests/ && ruff check src/ tests/ && mypy src/ && pytest
```

### Project Structure

```
src/todo_evolution/
├── __init__.py              # Package exports (Task, TaskService)
├── models/
│   ├── __init__.py
│   └── task.py              # Task dataclass
├── services/
│   ├── __init__.py
│   └── task_service.py      # CRUD operations
└── cli/
    ├── __init__.py
    ├── utils.py             # Banner, formatting utilities
    ├── interactive.py       # Interactive TUI mode
    ├── commands.py          # Command-line mode
    └── main.py              # Entry point router

tests/
├── conftest.py              # Shared pytest fixtures
├── unit/
│   ├── test_task_model.py      # Task model tests (6 tests)
│   └── test_task_service.py    # TaskService tests (27 tests)
└── integration/
    ├── test_interactive_cli.py # Interactive mode tests (20+ tests)
    └── test_command_cli.py     # Command mode tests (30+ tests)
```

## 📋 Requirements

- **Python**: 3.13 or higher
- **Dependencies**:
  - `rich>=13.0.0` - Terminal formatting and tables
  - `questionary>=2.0.0` - Interactive prompts
  - `pyfiglet>=1.0.0` - ASCII art banner
- **Development Dependencies**:
  - `pytest>=8.0.0` - Testing framework
  - `pytest-cov>=4.0.0` - Coverage reporting
  - `black>=24.0.0` - Code formatting
  - `ruff>=0.1.0` - Fast linter
  - `mypy>=1.8.0` - Type checking

## 🎯 Design Principles

- **Separation of Concerns**: Services layer is pure Python, CLI layer handles presentation
- **Test-Driven Development**: 90%+ test coverage with comprehensive unit and integration tests
- **Type Safety**: Full type hints for better IDE support and error detection
- **User Experience**: Beautiful, intuitive interface with clear error messages
- **Library Reusability**: Core logic usable without CLI dependencies

## 📖 Documentation

- [Feature Specification](specs/001-todo-evolution/spec.md) - Requirements and user stories
- [Implementation Plan](specs/001-todo-evolution/plan.md) - Technical architecture
- [Data Model](specs/001-todo-evolution/data-model.md) - Entity specifications
- [API Contracts](specs/001-todo-evolution/contracts/) - Service and CLI interfaces
- [Task List](specs/001-todo-evolution/tasks.md) - Implementation task breakdown
- [Quickstart Guide](specs/001-todo-evolution/quickstart.md) - Developer onboarding

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork** the repository
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** with tests
4. **Run quality checks**: `black . && ruff check . && mypy src/ && pytest`
5. **Commit your changes**: `git commit -m 'feat: add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `test:` - Test updates
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- Interactive prompts powered by [Questionary](https://github.com/tmbo/questionary)
- ASCII art by [PyFiglet](https://github.com/pwaller/pyfiglet)
- Inspired by modern CLI tools like GitHub CLI and Vercel CLI

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/todo-evolution/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/todo-evolution/discussions)
- **Documentation**: [Full Documentation](https://github.com/yourusername/todo-evolution/tree/main/specs)

## 🗺️ Roadmap

Future enhancements (not in v1.0):
- Persistent storage (JSON, SQLite)
- Task categories and tags
- Due dates and reminders
- Priority levels
- Sub-tasks and dependencies
- Export/import functionality
- Multi-user support
- Web API

## 📊 Project Stats

- **Lines of Code**: ~1,500 (src + tests)
- **Test Coverage**: 90%+
- **Test Count**: 60+ comprehensive tests
- **Type Safety**: 100% type-hinted
- **Documentation**: Comprehensive specs and guides

---

**Made with ❤️ by developers, for developers**

*Todo Evolution - Where productivity meets elegance in the terminal*
