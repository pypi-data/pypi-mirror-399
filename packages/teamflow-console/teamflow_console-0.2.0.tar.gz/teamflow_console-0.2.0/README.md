# TeamFlow Console App

[![PyPI](https://img.shields.io/pypi/v/teamflow-console)](https://pypi.org/project/teamflow-console/)
[![Python](https://img.shields.io/pypi/pyversions/teamflow-console)](https://pypi.org/project/teamflow-console/)
[![License](https://img.shields.io/pypi/l/teamflow-console)](https://github.com/MrOwaisAbdullah/Teamflow/blob/main/LICENSE)

Interactive menu-driven console application for task distribution in small agencies.

## Installation

```bash
# Install from PyPI
pip install teamflow-console

# Or install with pipx (recommended for isolated environments)
pipx install teamflow-console
```

## Quick Start

```bash
# Run the application
teamflow
```

## Features

- **Interactive Menu Navigation**: No command memorization required
- **Task Management**: Create, view, update, complete, and delete tasks
- **User & Team Management**: Create users with roles and skills, create teams
- **Task Assignment**: Assign tasks to team members with workload warnings
- **Task Filtering**: Filter by status, priority, and assignee
- **Keyboard Shortcuts**: Quick actions for power users (c=create, l=list, q=quit)

## First Run

1. Launch `python -m src.main`
2. See main menu with numbered options
3. Press `1` for Task Management
4. Press `1` to Create Task
5. Follow the prompts (title, description, priority, assignee)
6. Task created! Press `l` to list all tasks

## Tech Stack

- Python 3.13+
- typer (CLI framework)
- rich (terminal UI)
- pydantic (data validation)
- pytest (testing)

## Project Structure

```
src/
├── models/      # Pydantic data models
├── services/    # Business logic layer
├── cli/         # CLI interface (menus, prompts)
└── lib/         # Utilities (formatting, storage)
tests/
├── unit/        # Model and service tests
├── integration/ # End-to-end workflow tests
└── contract/    # Interface contract tests
```

## License

MIT
