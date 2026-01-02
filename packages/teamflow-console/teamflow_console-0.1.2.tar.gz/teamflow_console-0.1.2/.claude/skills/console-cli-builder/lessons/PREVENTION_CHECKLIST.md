# Prevention Checklist: Console CLI Builder

Use this checklist BEFORE running generated code to avoid common pitfalls.

---

## Pre-Flight Checks

### Environment Setup

- [ ] **UV is installed**
  - Run: `uv --version`
  - If missing: `curl -LsSf https://astral.sh/uv/install.sh | sh`

- [ ] **Python 3.13+ is available**
  - Run: `python --version`
  - Must be 3.13 or higher

- [ ] **pyproject.toml exists with correct dependencies**
  ```toml
  [project]
  requires-python = ">=3.13"
  dependencies = [
      "typer>=0.12.0",
      "rich>=13.7.0",
      "pydantic>=2.5.0",
  ]
  ```

---

## Code Verification

### Import Verification

Check these files for required imports:

- [ ] **`src/cli/menus.py`** has Panel import
  ```python
  from rich.panel import Panel  # MUST HAVE
  ```

- [ ] **`src/main.py`** has all prompt imports
  ```python
  from cli.prompts import TaskPrompts, UserPrompts
  ```

### Sentinel Pattern Verification

- [ ] **Sentinel is at MODULE level** (not inside method)
  ```python
  # At top of file (module level)
  _UNSET = object()

  class Service:
      def update(self, x: type | None | object = _UNSET):
          if x is not _UNSET:  # Correct comparison
              ...
  ```

- [ ] **Sentinel used as DEFAULT value** in parameter
  ```python
  def update(self, assignee_id: int | None | object = _UNSET):
  ```

### Cancellation Handling

- [ ] **All create prompts have try/except for CancelledException**
  ```python
  def prompt_create_xxx(self) -> None:
      try:
          # ... prompts ...
      except CancelledException:
          pass  # Silent return
  ```

- [ ] **CancelledException is defined**
  ```python
  class CancelledException(Exception):
      """Raised when user cancels an operation."""
      pass
  ```

---

## Run-Time Verification

### Before First Run

- [ ] **Dependencies installed**
  ```bash
  uv sync --all-extras
  ```

- [ ] **PYTHONPATH is set in run command**
  ```bash
  # Must include PYTHONPATH=src
  PYTHONPATH=src uv run python -m src.main
  ```

- [ ] **On Windows: Use proper PowerShell syntax**
  ```powershell
  $env:PYTHONPATH="src"; uv run python -m src.main
  ```

---

## Common Pitfalls

### ❌ WRONG: Sentinel inside method

```python
# WRONG - creates new object each call
def update(self, assignee_id=None):
    _UNSET = object()  # New each time!
    if assignee_id is not _UNSET:  # Never True
        ...
```

### ✅ CORRECT: Sentinel at module level

```python
# At top of file
_UNSET = object()

def update(self, assignee_id: int | None | object = _UNSET):
    if assignee_id is not _UNSET:  # Works!
        ...
```

---

### ❌ WRONG: Missing Panel import

```python
from rich.console import Console
# Missing: from rich.panel import Panel

panel = Panel("text")  # NameError!
```

### ✅ CORRECT: Import Panel

```python
from rich.console import Console
from rich.panel import Panel  # Add this

panel = Panel("text")  # Works!
```

---

### ❌ WRONG: No PYTHONPATH

```bash
python -m src.main  # Can't find modules
```

### ✅ CORRECT: Set PYTHONPATH

```bash
PYTHONPATH=src python -m src.main  # Works!
```

---

## Service Wiring Check

- [ ] **Services created before wiring**
  ```python
  # Create first
  user_service = UserService(store)
  task_service = TaskService(store, user_service=user_service)

  # Wire after both exist
  user_service._task_service = task_service
  ```

---

## Test Verification

- [ ] **Tests pass before running app**
  ```bash
  uv run pytest tests/ -v
  ```

- [ ] **Coverage is 80%+**
  ```bash
  uv run pytest --cov=src --cov-report=term-missing
  ```

---

## Quick Smoke Test

After first run, verify:

- [ ] Main menu displays without errors
- [ ] Number keys navigate to sub-menus
- [ ] '0' or 'b' returns to main menu
- [ ] 'q' in create prompt returns to menu (no error)
- [ ] Creating entity works
- [ ] Listing shows created entity
- [ ] Colors display (red=error/high, green=success)

---

**Version:** 1.0.0
**Last Updated:** 2025-01-28
