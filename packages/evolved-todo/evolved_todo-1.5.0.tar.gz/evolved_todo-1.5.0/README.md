# Phase I.5: Todo CLI App - Enhanced Interface

An in-memory Python CLI todo application with rich visual formatting, built using spec-first, AI-driven development principles.

## Features

- ✅ **Add Tasks**: Create tasks with title and optional description
- ✅ **View Tasks**: Display all tasks in styled table with color-coded status
- ✅ **Update Tasks**: Modify task title and/or description
- ✅ **Delete Tasks**: Permanently remove tasks from the list
- ✅ **Toggle Status**: Mark tasks as complete or incomplete

## Enhanced UI Features (v1.5)

- 🎨 **Color-Coded Status**: Green ✓ for complete tasks, yellow ⏳ for incomplete
- 📊 **Styled Tables**: Aligned columns (ID, Status, Title, Description) with proper spacing
- ✅ **Success Messages**: Green [OK] prefix for successful operations
- ❌ **Error Messages**: Red [ERROR] prefix for failures and validation errors
- ℹ️ **Info Messages**: Blue [INFO] for neutral feedback (e.g., "No tasks found")
- 🎯 **Styled Menu**: Professional header panel with cyan-colored options
- ⌨️ **Styled Prompts**: Cyan-colored input prompts with validation
- 🔄 **Cross-Platform**: Works on Windows, macOS, Linux with automatic fallback to ASCII if needed

## Quick Start

### Prerequisites

- Python 3.13+ ([Download Python](https://www.python.org/downloads/))
- UV package manager (optional but recommended)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd hackathon-evolution-todo

# Checkout the feature branch
git checkout 001-todo-cli-app

# Install UV (if not already installed)
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell):
powershell -c "irm https://astral.sh/uv/install.sh | iex"
```

### Running the Application

**Option 1: Using Python directly**
```bash
python src/main.py
```

**Option 2: Using UV (recommended)**
```bash
uv run python src/main.py
```

## Usage

Once the application starts, you'll see a menu with 6 options:

```
==============================
    Todo List Manager
==============================
1. Add Task
2. View Tasks
3. Update Task
4. Delete Task
5. Toggle Task Status
6. Exit
==============================
```

### Example Workflow

```bash
# 1. Add a task
Select option (1-6): 1
Enter task title: Buy groceries
Enter task description (optional): Milk, eggs, bread

✓ Success! Task 1 created: Buy groceries

# 2. View all tasks
Select option (1-6): 2

--- All Tasks ---

[ ] Task 1: Buy groceries
   Description: Milk, eggs, bread

# 3. Mark task as complete
Select option (1-6): 5
Enter task ID to toggle: 1

✓ Success! Task 1 marked as complete
   [✓] Buy groceries

# 4. Update task
Select option (1-6): 3
Enter task ID to update: 1

Leave blank and press Enter to keep current value:
New title: Buy groceries and snacks
New description: 

✓ Success! Task 1 updated
   Title: Buy groceries and snacks
   Description: Milk, eggs, bread

# 5. Delete task
Select option (1-6): 4
Enter task ID to delete: 1

✓ Success! Task 1 deleted

# 6. Exit
Select option (1-6): 6

==============================
  Exiting... Goodbye!
==============================
```

## Project Structure

```
.
├── src/
│   ├── __init__.py          # Package initialization
│   ├── models.py            # Task dataclass
│   ├── todo_manager.py      # Business logic (CRUD operations)
│   └── main.py              # CLI interface
├── tests/
│   └── manual_test_checklist.md  # Manual testing scenarios
├── specs/
│   └── 001-todo-cli-app/    # Feature specifications and design docs
├── pyproject.toml           # Project configuration
├── CLAUDE.md                # Claude Code prompt history
└── README.md                # This file
```

### Key Components

- **`models.py`**: Defines the `Task` dataclass with id, title, description, and status fields
- **`todo_manager.py`**: Implements `TodoManager` class with in-memory storage using `dict[int, Task]`
- **`main.py`**: Provides CLI interface with menu-driven navigation and user input handling

## Development

### Code Quality

The project follows strict quality standards:

- **PEP 8 compliant**: All code follows Python style guidelines
- **Type hints**: Full type annotations on all functions
- **Docstrings**: Google-style docstrings for all classes and functions
- **Linting**: Passes `ruff` checks with zero errors

```bash
# Run linting
ruff check src/

# Auto-fix issues
ruff check --fix src/
```

### Testing

Manual testing checklist available at `tests/manual_test_checklist.md` with 15 test scenarios covering all 5 user stories.

### Design Principles

This project follows the **Project Constitution** principles:

1. ✅ **Spec-First Development**: Complete specification before implementation
2. ✅ **AI-Driven Architecture**: All code generated via Claude Code
3. ✅ **Iterative Evolution**: Phase I (CLI) → Phase II (Persistence) → Phase III+ (Web/Distributed)
4. ✅ **Product Thinking**: User-focused design with clear value priorities
5. ✅ **Process Documentation**: Full traceability via specs, plans, and prompt history
6. ✅ **Quality Gates**: PEP 8 compliance, type hints, manual testing

## Technical Details

- **Language**: Python 3.13+
- **Dependencies**: Python standard library only (no external packages)
- **Storage**: In-memory using `dict[int, Task]` (data lost on exit per Phase I design)
- **ID Generation**: Sequential integers starting from 1
- **Status Representation**: Boolean (False = incomplete, True = complete)
- **Error Handling**: Custom exceptions (`TaskNotFoundError`, `InvalidInputError`)

## Constraints & Limitations

**Phase I Scope** (by design):
- ❌ No persistence (tasks lost when app closes)
- ❌ No advanced features (priorities, tags, search, filters)
- ❌ No web interface or API
- ❌ No multi-user support
- ❌ Single session only (up to 100 tasks recommended)

**Future Phases**:
- Phase II: File-based persistence (JSON/SQLite)
- Phase III: REST API and web frontend
- Phase IV: Distributed features (sync, collaboration)
- Phase V: AI integration and cloud-native deployment

## Documentation

- **[Specification](specs/001-todo-cli-app/spec.md)**: Feature requirements and acceptance criteria
- **[Implementation Plan](specs/001-todo-cli-app/plan.md)**: Architecture and technical decisions
- **[Data Model](specs/001-todo-cli-app/data-model.md)**: Entity design and validation rules
- **[Task Breakdown](specs/001-todo-cli-app/tasks.md)**: 60-task implementation plan
- **[Claude Code Prompts](CLAUDE.md)**: AI-driven development history
- **[Constitution](.specify/memory/constitution.md)**: Project principles and governance

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'src'`
**Solution**: Run from project root directory, not from `src/` subdirectory

**Issue**: `python: command not found`
**Solution**: Use `python3` or `python3.13` if you have multiple Python versions

**Issue**: Ruff not found
**Solution**: Install ruff with `pip install ruff` or `uv pip install ruff`

**Issue**: Application doesn't respond to input
**Solution**: Ensure you're running in an interactive terminal, not a non-interactive shell

## Contributing

This is an educational project following spec-driven development. To contribute:

1. Read the [Project Constitution](.specify/memory/constitution.md)
2. Follow the spec → plan → tasks → implement workflow
3. Document all Claude Code prompts in CLAUDE.md
4. Ensure code passes `ruff check` with zero errors
5. Test against all 15 manual test scenarios

## License

Educational project - see repository license for details.

## Acknowledgments

Built using:
- **Claude Code**: AI-driven development agent
- **Spec-Kit Plus**: Specification management framework
- **UV**: Modern Python package manager

---

**Version**: 1.0.0 (Phase I Complete)
**Last Updated**: 2025-12-29
**Branch**: `001-todo-cli-app`
