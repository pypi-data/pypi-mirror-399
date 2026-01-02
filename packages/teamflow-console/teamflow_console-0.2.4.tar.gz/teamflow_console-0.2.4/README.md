# TeamFlow Console App

[![PyPI](https://img.shields.io/pypi/v/teamflow-console)](https://pypi.org/project/teamflow-console/)
[![Python](https://img.shields.io/pypi/pyversions/teamflow-console)](https://pypi.org/project/teamflow-console/)
[![License](https://img.shields.io/pypi/l/teamflow-console)](https://github.com/MrOwaisAbdullah/Teamflow/blob/main/LICENSE)

Interactive menu-driven console application for task distribution in small agencies.

## Installation

```bash
# Install from PyPI (latest version)
pip install teamflow-console

# Or install a specific version
pip install teamflow-console==0.2.3
```

**Requirements:** Python 3.13 or higher

## Quick Start

```bash
# Run the application
teamflow
```

That's it! The app will launch and show you the main menu.

## Features

- **Interactive Menu Navigation**: No command memorization required
- **Task Management**: Create, view, update, complete, and delete tasks
- **User & Team Management**: Create users with roles and skills, create teams
- **Task Assignment**: Assign tasks to team members with workload warnings
- **Task Filtering**: Filter by status, priority, and assignee
- **Keyboard Shortcuts**: Quick actions for power users (c=create, l=list, q=quit)
- **Visual Spacing**: Clean menu displays with proper line breaks

## First Run

1. Run `teamflow` in your terminal
2. You'll see a data loss warning (press Enter to continue)
3. Main menu appears with 5 options
4. Press `1` for Task Management
5. Press `1` to Create Task
6. Follow the prompts (title, description, priority, assignee)
7. Task created! Press `l` to list all tasks

## Menu Navigation

| Key | Action |
|-----|--------|
| `1-5` | Select menu option |
| `0` | Go back to main menu |
| `c` | Quick create task (from main menu) |
| `l` | Quick list tasks (from main menu) |
| `q` | Quit application |
| `Enter` | Confirm / Continue |

## Example Usage

```
$ teamflow

┌─────────────────────────────────────────────┐
│          TEAMFLOW - Task Manager           │
├─────────────────────────────────────────────┤
│  1. Task Management                         │
│  2. User & Team Management                  │
│  3. View Tasks                              │
│  4. View Resources                          │
│  5. Exit                                    │
├─────────────────────────────────────────────┤
│ c=Create, l=List, q=Quit                     │
└─────────────────────────────────────────────┘

Select option [1-5]: 1

[Task Management Menu appears...]

Select option [0-5]: 1

Enter task title: Fix login bug
Enter description (optional): [Enter to skip]
Select priority:
  1. High
  2. Medium
  3. Low
Select [1-3]: 1

┌─────────────────────────────────────────────┐
│ [SUCCESS] Task created!                      │
│                                             │
│ ID: 1                                        │
│ Title: Fix login bug                         │
│ Priority: High                               │
│ Status: Todo                                 │
│                                             │
│ Press Enter to continue...                    │
└─────────────────────────────────────────────┘
```

## Development

For development setup, see the [quickstart guide](specs/001-console-task-distribution/quickstart.md).

## Tech Stack

- Python 3.13+
- typer (CLI framework)
- rich (terminal UI)
- pydantic (data validation)
- pytest (testing)

## Project Structure

```
teamflow_console/
├── __init__.py   # Entry point
├── cli/          # CLI interface (menus, prompts)
├── lib/          # Utilities (formatting, storage, validation)
├── models/       # Pydantic data models
└── services/     # Business logic layer
tests/
├── unit/         # Model and service tests
├── integration/  # End-to-end workflow tests
└── contract/     # Interface contract tests
```

## License

MIT © 2025 Owais Abdullah

