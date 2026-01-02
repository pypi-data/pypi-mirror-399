---
name: console-cli-builder
description: Production-ready interactive console CLI applications with Python 3.13+, Typer, Rich, and Pydantic. Includes menu-driven UI, in-memory storage, TDD setup, and common patterns learned from real-world implementation.
category: backend
version: 1.0.0
---

# Console CLI Builder Skill

## Purpose

Quickly scaffold and implement **interactive menu-driven console applications** in Python with:
- Beautiful terminal UI (Rich panels, tables, colors)
- Type-safe data models (Pydantic)
- Clean service layer architecture (SOLID principles)
- TDD setup with pytest (80%+ coverage target)
- Battle-tested patterns from production implementation

## When to Use This Skill

Use this skill when:
- Building interactive CLI tools with menu navigation (no command memorization)
- Creating task management, CRUD, or data entry console apps
- Need terminal UI with colors, tables, and panels
- Want in-memory storage with easy database migration path
- Require TDD setup with proper testing structure

## Core Capabilities

### 1. Interactive Menu System

State machine-based menu navigation with keyboard shortcuts.

```python
from services.menu_service import MenuService, MenuState

# Navigate using number keys or shortcuts
menu_service = MenuService()
menu_service.navigate("1")  # Go to option 1
menu_service.navigate("c")  # Shortcut for Create
menu_service.back()         # Return to previous menu
```

### 2. Rich Terminal UI

Beautiful tables, panels, and color-coded feedback.

```python
from rich.panel import Panel
from rich.console import Console

console = Console()
console.print(Panel("Success!", border_style="green"))
```

### 3. Pydantic Data Models

Runtime validation with clear error messages.

```python
from pydantic import BaseModel, Field, field_validator

class Task(BaseModel):
    id: int
    title: str = Field(min_length=1, max_length=200)
    priority: Priority
    status: Status = Status.TODO
```

### 4. Service Layer Pattern

Business logic separated from CLI, testable in isolation.

```python
class TaskService:
    def __init__(self, store: TaskStoreProtocol):
        self._store = store
```

### 5. Protocol-Based Storage

Easy migration from in-memory to database.

```python
class TaskStoreProtocol(Protocol):
    def save(self, task: Task) -> Task: ...
    def find_by_id(self, task_id: int) -> Task | None: ...

# Swap implementation without changing business logic
# InPhaseI: InMemoryTaskStore
# PhaseII: SQLiteTaskStore
```

## Usage Instructions

### 1. Invoke the Skill

When prompted, describe your CLI app requirements:
- What data entities do you need? (tasks, users, projects, etc.)
- What operations? (create, list, update, delete, filter, etc.)
- Any special features? (assignment, teams, search, etc.)

### 2. Generated Project Structure

```
src/
├── main.py              # Entry point (typer CLI)
├── models/              # Pydantic data models
│   ├── __init__.py
│   └── entity.py        # Task, User, etc.
├── services/            # Business logic
│   ├── __init__.py
│   └── entity_service.py
├── cli/                 # CLI interface
│   ├── __init__.py
│   ├── menus.py         # Menu definitions
│   └── prompts.py       # Interactive prompts
└── lib/                 # Utilities
    ├── __init__.py
    ├── formatting.py    # Rich UI helpers
    ├── validation.py    # Input validation
    └── storage.py       # In-memory storage

tests/
├── unit/                # Model and service tests
├── integration/         # End-to-end workflow tests
└── contract/            # API contract tests
```

### 3. Key Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.13+ | Modern type hints, pattern matching |
| **uv** | latest | Fast package manager |
| **typer** | 0.12.0+ | CLI framework |
| **rich** | 13.7.0+ | Terminal UI |
| **pydantic** | 2.5.0+ | Data validation |
| **pytest** | 7.4.0+ | Testing |

### 4. Run the Generated App

```bash
# Using UV (recommended)
PYTHONPATH=src uv run python -m src.main

# Or with activated venv
source .venv/bin/activate
PYTHONPATH=src python -m src.main
```

## Common Patterns Included

### Pattern 1: Cancellation Handling

Use custom exception for graceful cancellation.

```python
class CancelledException(Exception):
    """Raised when user cancels an operation."""
    pass

def prompt_create(self) -> None:
    try:
        name = self._prompt_name()
        # ... create entity
    except CancelledException:
        pass  # Return to menu silently
```

### Pattern 2: Sentinel for Optional Parameters

Detect when optional parameter was explicitly passed.

```python
# Module-level sentinel (NOT inside method!)
_UNSET = object()

def update(self, id: int, assignee_id: int | None | object = _UNSET):
    if assignee_id is not _UNSET:
        # assignee_id was explicitly passed (including None)
        task_dict["assignee_id"] = assignee_id
    # Otherwise preserve existing value
```

### Pattern 3: Service Integration

Avoid circular dependencies with optional wiring.

```python
class TaskService:
    def __init__(self, store, user_service=None):
        self._store = store
        self._user_service = user_service  # Optional
        self._task_service = None  # Wired after creation

# Wire after both services created
task_service._task_service = user_service
user_service._task_service = task_service
```

### Pattern 4: Rich Table with Names

Display foreign key names instead of IDs.

```python
def render_table(tasks, user_service=None):
    for task in tasks:
        if task.assignee_id and user_service:
            user = user_service.get_by_id(task.assignee_id)
            assignee = user.name
        else:
            assignee = "Unassigned"
```

### Pattern 5: Numbered Selection Menu

```python
def prompt_selection(self) -> int:
    console.print("Select option:")
    console.print("  [0] Unassigned")
    for idx, user in enumerate(users, 1):
        console.print(f"  [{idx}] {user.name}")

    while True:
        choice = input(f"Enter choice [0-{len(users)}]: ").strip()
        if not choice:
            return None  # Default
        return int(choice)
```

## Prevention Checklist

Before using generated code, verify:

- [ ] **uv** is installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- [ ] **PYTHONPATH** is set when running (`PYTHONPATH=src`)
- [ ] **Rich Panel import** is present: `from rich.panel import Panel`
- [ ] **Sentinel** is module-level, not inside method
- [ ] **Cancellation** handled in all create prompts
- [ ] **Service wiring** happens after both services created
- [ ] **Tests run** with `pytest --cov=src`

## Lessons Learned

### Critical Bugs Fixed During Development

| Bug | Cause | Fix |
|-----|-------|-----|
| `ModuleNotFoundError: No module named 'cli'` | Missing PYTHONPATH | Always set `PYTHONPATH=src` before running |
| `NameError: name 'Panel' is not defined` | Missing import | Add `from rich.panel import Panel` |
| Assignee removed when editing | Sentinel defined inside method | Move `_UNSET = object()` to module level |
| Parameter name mismatch | Used `"assignee"` instead of `"assignee_id"` | Match exact parameter names from service |
| Error on 'q' to cancel | CancelledException not caught | Wrap create methods in try/except |

### Design Decisions

1. **Service Layer Separation**: Business logic in services, CLI only handles I/O
2. **Protocol-Based Storage**: Enables easy migration from in-memory to database
3. **State Machine Navigation**: Clear menu state with history stack for Back
4. **TDD First**: Write tests before implementation, 80%+ coverage target

## Output Format

When this skill is invoked, provide:
1. **Project structure** with all directories
2. **pyproject.toml** with dependencies
3. **Core models** (Pydantic)
4. **Service layer** (business logic)
5. **CLI interface** (menus, prompts)
6. **Test suite** (unit, integration, contract)
7. **Quick start guide** (README)

## Time Savings

**With this skill:** ~2-3 hours to generate a fully functional interactive CLI app with:
- Menu navigation
- CRUD operations
- Beautiful terminal UI
- Test suite with 80%+ coverage
- Clean architecture

**Without this skill:** ~1-2 days of research, trial-and-error, and debugging common pitfalls.