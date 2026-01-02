# Quick Start: TeamFlow Console App (Phase 1)

**Feature**: 001-console-task-distribution
**Date**: 2025-01-15
**Prerequisites**: Python 3.13+

## 🚀 Quick Start (Fastest Path)

```bash
# 1. Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux/macOS
# or
irm https://astral.sh/uv/install.ps1 | iex        # Windows PowerShell

# 2. Navigate to project and install dependencies
cd /path/to/teamflow
uv sync --all-extras

# 3. Run the app
uv run python -m src.main
```

**That's it!** You're now running TeamFlow Console App.

---

## Overview

TeamFlow Console App is an **in-memory task distribution system** for small agencies (10-50 people). It features an **interactive menu-driven interface**—no command memorization required.

**What You Can Do:**
- Create, list, update, complete, and delete tasks
- Create users and teams
- Assign tasks to users
- Filter tasks by status, priority, or assignee
- View team workload

## Installation

### Step 1: Install UV (Python Package Manager)

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

### Step 2: Create Virtual Environment

```bash
# Navigate to project directory
cd /path/to/teamflow

# Create virtual environment
uv venv

# Activate (Linux/macOS)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate
```

### Step 3: Install Dependencies

**`uv sync`** reads from `pyproject.toml` and installs all dependencies automatically:

```bash
# Install runtime dependencies only
uv sync

# Install runtime + dev dependencies (recommended for development)
uv sync --all-extras
```

**What gets installed:**
- **Runtime**: `typer`, `rich`, `pydantic`
- **Dev tools** (with `--all-extras`): `pytest`, `pytest-cov`, `pytest-mock`, `black`, `isort`, `pylint`, `mypy`

## Running the Application

### Launch the App

**Recommended: Use `uv run` (handles PYTHONPATH automatically on most systems)**

```bash
# Linux/macOS/WSL
PYTHONPATH=src uv run python -m src.main

# Windows PowerShell
$env:PYTHONPATH="src"; uv run python -m src.main

# Windows CMD
set PYTHONPATH=src && uv run python -m src.main
```

**Alternative: Activate venv first**

```bash
# 1. Activate the virtual environment
# Linux/macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows CMD
.venv\Scripts\activate.bat

# 2. Set PYTHONPATH and run
# Linux/macOS/WSL
PYTHONPATH=src python -m src.main

# Windows PowerShell
$env:PYTHONPATH="src"; python -m src.main

# Windows CMD
set PYTHONPATH=src && python -m src.main
```

**Note:** `PYTHONPATH=src` tells Python where to find the `cli`, `models`, `services`, and `lib` modules. Without it, you'll get `ModuleNotFoundError: No module named 'cli'`.

### First Run Experience

When you first launch TeamFlow, you'll see the main menu:

```
┌─────────────────────────────────────────────┐
│          TEAMFLOW - Task Manager           │
├─────────────────────────────────────────────┤
│  1. Task Management                         │
│  2. User & Team Management                  │
│  3. View Tasks                              │
│  4. View Resources                          │
│  5. Exit                                    │
├─────────────────────────────────────────────┤
│ Shortcuts: c=Create, l=List, q=Quit         │
│ Select option [1-5]: _                      │
└─────────────────────────────────────────────┘
```

### Creating Your First Task (Under 60 Seconds)

1. **Press `1`** → Enter Task Management submenu
2. **Press `1`** → Create Task
3. **Enter title**: `Fix client login bug`
4. **Description**: Press Enter to skip (optional)
5. **Priority**: Press `2` for Medium (or Enter for default)
6. **Assignee**: Press `0` for Unassigned (or select a user)

**Done!** Your first task is created in under 60 seconds.

## Basic Usage

### Navigation

| Action | Key(s) |
|--------|--------|
| Select option | Number keys (1-5, 0-6) |
| Navigate | Arrow keys (Up/Down) + Enter |
| Quick actions | `c` (Create), `l` (List), `q` (Quit) |
| Go back | `0` or `b` or Escape |

### Creating Users

1. From Main Menu → Press `2` (User & Team Management)
2. Press `1` (Create User)
3. Enter name: `Sarah`
4. Select role: Press `2` for Developer
5. Skills: Enter `Python,FastAPI,SQL` (optional)

### Creating Teams

1. From Main Menu → Press `2` (User & Team Management)
2. Press `2` (Create Team)
3. Enter team name: `Frontend Squad`
4. Select members: Enter `1,3` to select users 1 and 3

### Assigning Tasks

1. From Task Management → Press `3` (Update Task)
2. Enter task ID: `1`
3. Press `5` (Assignee)
4. Select user: Press `1` for Sarah

### Viewing Tasks by Assignee

1. From Main Menu → Press `3` (View Tasks)
2. Review the task list
3. Press Enter to open filter menu
4. Press `4` (By Assignee)
5. Select assignee: Press `1` for Sarah

## Common Workflows

### Workflow 1: Create and Assign Task

```
Main Menu → 1 (Task Mgmt) → 1 (Create)
Enter title: "Fix navigation bug"
Description: [Enter to skip]
Priority: 1 (High)
Assignee: 1 (Sarah)
→ Task created!
```

### Workflow 2: Complete Task

```
Main Menu → 1 (Task Mgmt) → 4 (Complete)
Enter task ID: 1
Confirm: Y
→ Task marked as Done!
```

### Workflow 3: Delete Task

```
Main Menu → 1 (Task Mgmt) → 5 (Delete)
Enter task ID: 1
Confirm: Y
→ Task deleted!
```

### Workflow 4: Filter High Priority Tasks

```
Main Menu → 3 (View Tasks)
[Review task list]
Press Enter → Filter Menu → 3 (By Priority)
Select: 1 (High)
→ Shows only high priority tasks
```

## Understanding the Display

### Task List Table

```
┌──────┬─────────────────┬──────────┬─────────────┬────────────┐
│  ID  │ Title           │ Priority │ Assignee    │ Status     │
├──────┼─────────────────┼──────────┼─────────────┼────────────┤
│   1  │ Fix Navbar       │ High     │ Sarah       │ Todo       │
│   2  │ Update docs      │ Medium   │ Unassigned  │ Done       │
└──────┴─────────────────┴──────────┴─────────────┴────────────┘
```

**Color Coding:**
- **Red** = High Priority
- **Yellow** = Medium Priority
- **Blue** = Low Priority
- **Green** = Done Status

### Success Messages

```
┌─────────────────────────────────────────────┐
│ [SUCCESS] Task created!                      │
│                                             │
│ ID: 1                                        │
│ Title: Fix Navbar                             │
│ Priority: High                                │
│ Status: Todo                                  │
│ Assignee: Sarah                               │
│                                             │
│ Press Enter to continue...                    │
└─────────────────────────────────────────────┘
```

## Data Persistence

**Important**: Phase I uses **in-memory storage**. All data resets when you exit the application.

**Why?** Phase I is a foundation for learning and validation. Persistent database storage comes in Phase II.

**Workaround**: For testing, you can re-create tasks quickly using keyboard shortcuts (`c` for create, `l` for list).

## Running Tests

### Run All Tests

```bash
# Using UV (recommended)
uv run pytest --cov=src --cov-report=term-missing

# Or if venv is activated
pytest --cov=src --cov-report=term-missing
```

### Run Specific Test File

```bash
uv run pytest tests/unit/test_models.py -v
```

### Run with Verbose Output

```bash
uv run pytest -xvs
```

### Coverage Report

```bash
uv run pytest --cov=src --cov-report=html
# Then open htmlcov/index.html in your browser
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'cli'"

**Problem**: When running `uv run python -m src.main` or `python -m src.main`, you get:
```
ModuleNotFoundError: No module named 'cli'
```

**Cause**: Python cannot find the `src/` modules because `PYTHONPATH` is not set.

**Solution**: Always set `PYTHONPATH=src` before running the app.

**Windows PowerShell:**
```powershell
$env:PYTHONPATH="src"; uv run python -m src.main
```

**Windows CMD:**
```cmd
set PYTHONPATH=src && uv run python -m src.main
```

**Linux/macOS/WSL:**
```bash
PYTHONPATH=src uv run python -m src.main
```

**Or activate venv first** (then PYTHONPATH is not always needed on some systems):
```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Linux/macOS
source .venv/bin/activate

# Then run
python -m src.main
```

### Issue: "Module not found: src"

**Solution**: Make sure you're in the project root and the virtual environment is activated.

```bash
# Check current directory
pwd  # Should show /path/to/teamflow

# Check virtual environment
which python  # Should show .venv/bin/python
```

### Issue: "Permission denied" on UV install

**Solution**: Use `--allow-symlinks` flag or run with sudo.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh | allow-symlinks
```

### Issue: Terminal colors not showing

**Solution**: Rich auto-detects terminal capabilities. If colors don't show:
- Windows: Use Windows Terminal or PowerShell 5.1+
- Linux/macOS: Ensure `TERM` environment variable is set correctly

### Issue: Arrow keys not working

**Solution**: Some terminals don't support arrow key detection. Use number keys as fallback:
- `1`, `2`, `3`, `4`, `5` for menu options
- `0` for Back/Cancel

## Development Setup

### Code Formatting

```bash
# Format code with Black
uv run black src/ tests/

# Sort imports with isort
uv run isort src/ tests/

# Lint with pylint (requires PYTHONPATH)
PYTHONPATH=src uv run pylint src/
```

### Type Checking

```bash
# Run mypy for static type checking
uv run mypy src/
```

## Next Steps

1. **Explore the UI**: Navigate all menus and try keyboard shortcuts
2. **Create Sample Data**: Add 3-5 users, create 10 tasks, assign them
3. **Test Filtering**: Use filter menu to view tasks by status/priority/assignee
4. **Review Tests**: Run `pytest` to verify all tests pass
5. **Read the Spec**: See `specs/001-console-task-distribution/spec.md` for full requirements

## Phase II Preview

After Phase I, the system evolves to:
- **Persistent Storage**: Neon PostgreSQL database
- **Web UI**: Next.js 16 with drag-drop Kanban board
- **Authentication**: Better Auth with JWT tokens
- **REST API**: FastAPI endpoints for all operations
- **Time Tracking**: Log hours per task for profitability analysis

## Getting Help

### Documentation

- **Feature Spec**: `specs/001-console-task-distribution/spec.md`
- **Implementation Plan**: `specs/001-console-task-distribution/plan.md`
- **Data Model**: `specs/001-console-task-distribution/data-model.md`
- **Menu Flows**: `specs/001-console-task-distribution/contracts/menu-flow.md`

### Project Constitution

See `.specify/memory/constitution.md` for project principles, coding standards, and phase constraints.

### Keyboard Shortcuts Reference

| Key | Action | Where |
|-----|--------|-------|
| `1-5`, `0-6` | Select option | All menus |
| `c` | Go to Create Task | Main menu |
| `l` | Go to List Tasks | Main menu |
| `q` | Exit / Back | Any screen |
| `Enter` | Confirm selection | Any screen |
| `Escape` | Back to main menu | Any submenu |
| Arrow keys | Navigate highlight | Menus (if supported) |

---

**Enjoy using TeamFlow Console App!** 🚀
