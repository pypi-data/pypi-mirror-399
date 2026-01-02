# Lessons Learned: Console CLI Builder

This document captures all bugs, issues, and lessons learned during the TeamFlow Console App implementation. Use this to avoid repeating the same mistakes.

---

## Critical Bugs Fixed

### Bug #1: ModuleNotFoundError - No module named 'cli'

**Symptom:**
```
ModuleNotFoundError: No module named 'cli'
```

**Cause:**
Running `python -m src.main` without `PYTHONPATH=src` set. Python can't find the `cli`, `models`, `services` modules because they're under `src/`.

**Fix:**
Always set `PYTHONPATH=src` before running:
```bash
# Linux/macOS/WSL
PYTHONPATH=src python -m src.main

# Windows PowerShell
$env:PYTHONPATH="src"; python -m src.main

# Or use uv run (handles it better)
PYTHONPATH=src uv run python -m src.main
```

**Prevention:**
- Document in quickstart.md with platform-specific examples
- Add to Prevention Checklist

---

### Bug #2: NameError - name 'Panel' is not defined

**Symptom:**
```
NameError: name 'Panel' is not defined
```

App crashes immediately after data loss warning when trying to display menu.

**Cause:**
Missing import in `src/cli/menus.py`:
```python
# Missing this:
from rich.panel import Panel

# But using this:
panel = Panel(menu_text, ...)
```

**Fix:**
Add the import:
```python
from rich.console import Console
from rich.panel import Panel  # ADD THIS
from rich.text import Text
```

**Prevention:**
- Always verify all Rich imports are present
- Common Rich imports needed:
  - `from rich.console import Console`
  - `from rich.panel import Panel`
  - `from rich.table import Table`
  - `from rich.text import Text`

---

### Bug #3: Assignee removed when editing other fields

**Symptom:**
When editing a task's description, the assignee becomes "Unassigned".

**Cause:**
Sentinel pattern for optional parameters was broken. The sentinel `_UNSET` was defined **inside** the method as a local variable:

```python
# WRONG - sentinel is recreated each call
def update(self, task_id: int, assignee_id: int | None = None):
    _UNSET = object()  # New object each call!
    if assignee_id is not _UNSET:  # Never True!
        task_dict["assignee_id"] = assignee_id
```

**Fix:**
Define sentinel at **module level** and use as default value:

```python
# At module level (top of file)
_UNSET = object()

class TaskService:
    def update(self, task_id: int, assignee_id: int | None | object = _UNSET):
        if assignee_id is not _UNSET:  # Now works correctly
            task_dict["assignee_id"] = assignee_id
```

**Prevention:**
- Always define sentinel at module level
- Never inside method
- Use as default parameter value: `def func(param: type | object = _UNSET)`

---

### Bug #4: Parameter name mismatch error

**Symptom:**
```
TaskService.update() got an unexpected keyword argument 'assignee'.
Did you mean 'assignee_id'?
```

**Cause:**
Field map in prompts.py used wrong key name:
```python
# WRONG - service expects 'assignee_id'
field_map = {
    5: ("assignee", self._update_assignee),  # Wrong!
}
```

**Fix:**
Match the exact parameter name from the service:
```python
# CORRECT
field_map = {
    5: ("assignee_id", self._update_assignee),
}
```

**Prevention:**
- Always check service method signature
- Match parameter names exactly
- Use IDE autocomplete to verify

---

### Bug #5: Error when pressing 'q' to cancel creation

**Symptom:**
```
[red]An error occurred: [/red]
```

App shows error and exits instead of returning to menu when user enters 'q'.

**Cause:**
`CancelledException` raised but not caught in create methods:
```python
def prompt_create_task(self) -> None:
    title = self._prompt_title()  # Raises CancelledException on 'q'
    # ... more code
    # No try/except!
```

**Fix:**
Wrap all create methods in try/except:
```python
def prompt_create_task(self) -> None:
    try:
        title = self._prompt_title()
        description = self._prompt_description()
        priority = self._prompt_priority()
        assignee_id = self._prompt_assignee()

        task = self.task_service.create(...)
        self._show_success(task)
    except CancelledException:
        pass  # Return to menu silently
```

**Prevention:**
- Always wrap prompt workflows in try/except
- Use `CancelledException` for user-initiated cancellation
- Return silently (no error message)

---

## Design Patterns That Worked

### Pattern 1: Service Layer with Optional Dependencies

**Problem:** Circular dependency between TaskService and UserService (both need each other).

**Solution:** Create services first, wire them after:

```python
# Create services
user_service = UserService(get_user_store())
task_service = TaskService(get_task_store(), user_service=user_service)

# Wire bidirectional (optional)
user_service._task_service = task_service
```

---

### Pattern 2: Protocol-Based Storage

**Problem:** Want to swap storage backends (in-memory → database) without changing services.

**Solution:** Use Protocol (abstract interface):

```python
class TaskStoreProtocol(Protocol):
    def save(self, task: Task) -> Task: ...
    def find_by_id(self, task_id: int) -> Task | None: ...

class InMemoryTaskStore:
    # Implements protocol

class SQLiteTaskStore:
    # Also implements protocol

# Service depends on protocol, not implementation
class TaskService:
    def __init__(self, store: TaskStoreProtocol):
        self._store = store
```

---

### Pattern 3: Menu State Machine

**Problem:** Track current menu, handle "Back", prevent invalid transitions.

**Solution:** State enum with history stack:

```python
class MenuState(Enum):
    MAIN = auto()
    TASK_MANAGEMENT = auto()
    USER_MANAGEMENT = auto()
    # ...

class MenuService:
    def __init__(self):
        self._state = MenuState.MAIN
        self._history = []  # For Back navigation

    def navigate(self, selection: str):
        # Save current state for Back
        self._history.append(self._state)
        # Transition to new state
        # ...

    def back(self):
        if self._history:
            self._state = self._history.pop()
```

---

### Pattern 4: Rich Tables with Foreign Key Names

**Problem:** Display assignee name instead of ID in task table.

**Solution:** Accept optional user_service and fetch names:

```python
def render_task_table(console, tasks, user_service=None):
    for task in tasks:
        if task.assignee_id and user_service:
            try:
                user = user_service.get_by_id(task.assignee_id)
                assignee = user.name
            except UserNotFoundError:
                assignee = f"User #{task.assignee_id}"
        else:
            assignee = "Unassigned"

        console.print(f"{task.id} | {task.title} | {assignee}")
```

---

### Pattern 5: Numbered Selection with Validation

**Problem:** Guide users through selections without invalid input.

**Solution:** Show numbered list, validate range:

```python
def prompt_selection(self, users: list[User]) -> User | None:
    console.print("Select user:")
    console.print("  [0] Unassigned")
    for idx, user in enumerate(users, 1):
        console.print(f"  [{idx}] {user.name}")

    while True:
        max_id = len(users)
        choice = input(f"Enter choice [0-{max_id}]: ").strip()
        if not choice:
            return None  # Default

        try:
            user_id = int(choice)
            if user_id == 0:
                return None
            if 1 <= user_id <= max_id:
                return users[user_id - 1]
        except ValueError:
            pass

        console.print(f"[red]Please enter a number between 0 and {max_id}[/red]")
```

---

## Project Setup Checklist

Before starting a new CLI app:

- [ ] Create `pyproject.toml` with dependencies
- [ ] Create `.python-version` file (`3.13`)
- [ ] Create `setup.cfg` with black/isort/pylint/mypy configs
- [ ] Create `.gitignore` for Python (`.venv/`, `__pycache__`, etc.)
- [ ] Create directory structure: `src/{models,services,cli,lib}`, `tests/{unit,integration,contract}`
- [ ] Run `uv sync --all-extras` to install dependencies
- [ ] Add `from rich.panel import Panel` import immediately
- [ ] Add module-level `_UNSET = object()` sentinel
- [ ] Add `CancelledException` class
- [ ] Set up `PYTHONPATH=src` in run scripts
- [ ] Write first test before implementation (TDD)

---

## Common Imports Needed

```python
# Always needed
from typing import Optional, Protocol

# Rich UI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Pydantic
from pydantic import BaseModel, Field, field_validator

# pytest
import pytest
from pytest_mock import MockerFixture
```

---

## Testing Patterns

### Unit Test Pattern

```python
class TestTaskService:
    def test_create_task_generates_id(self):
        service = TaskService(InMemoryTaskStore())
        task = service.create("Fix bug", priority=Priority.HIGH)
        assert task.id == 1
```

### Integration Test Pattern

```python
class TestTaskWorkflow:
    def test_create_list_update_complete_delete(self):
        service = TaskService(InMemoryTaskStore())
        task = service.create("Task 1")
        listed = service.list_all()
        assert len(listed) == 1
        # ... continue workflow
```

---

## Quick Reference

### PYTHONPATH Issues
- Symptom: `ModuleNotFoundError: No module named 'cli'`
- Fix: `PYTHONPATH=src uv run python -m src.main`

### Missing Import
- Symptom: `NameError: name 'Panel' is not defined`
- Fix: Add `from rich.panel import Panel`

### Sentinel Pattern
- Define at module level: `_UNSET = object()`
- Use as default: `def func(x: type | object = _UNSET)`
- Check: `if x is not _UNSET:`

### Cancellation
- Define: `class CancelledException(Exception): pass`
- Wrap: `try: ... except CancelledException: pass`

### Service Wiring
- Create first, wire after
- `service._other_service = other_service`

---

**Version:** 1.0.0
**Last Updated:** 2025-01-28
**Based On:** TeamFlow Console App (001-console-task-distribution)
