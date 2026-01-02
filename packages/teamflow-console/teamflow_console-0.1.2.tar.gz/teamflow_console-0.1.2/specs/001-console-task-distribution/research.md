# Research: TeamFlow Console App (Phase 1)

**Feature**: 001-console-task-distribution
**Date**: 2025-01-15
**Status**: Complete

## Overview

Phase 1 of TeamFlow is an in-memory Python console application with interactive menu-driven UX. All technical decisions are derived from the project constitution and feature specification.

## Technology Decisions

### CLI Framework: typer

**Decision**: Use `typer>=0.12.0` for CLI structure.

**Rationale**:
- Modern, type-safe CLI framework built on Click
- Automatic help generation and command discovery
- Native support for subcommands (fits menu structure)
- Seamless integration with Pydantic for data validation
- Excellent Python 3.13+ compatibility

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| `click` | Older API, more boilerplate for subcommands |
| `argparse` (stdlib) | Verbose, no automatic help, manual validation |
| `prompt_toolkit` | More complex, overkill for simple menu navigation |

**References**:
- https://typer.tiangolo.com/
- https://rich.readthedocs.io/en/stable/protocols.html#typer

### Terminal UI: rich

**Decision**: Use `rich>=13.7.0` for terminal UI.

**Rationale**:
- Beautiful table rendering with borders and colors
- Panel widgets for success/error messages
- Progress bars for operations (if needed)
- Syntax highlighting for code/error messages
- Built-in support for menu-like interfaces
- Excellent Windows terminal support (via Windows console API)

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| `bullet` | Too simple, lacks table/panel widgets |
| `blessed` | Curses-like complexity, overkill for this use case |
| `texttable` | Tables only, no colors or panels |
| `terminaltables` | No longer maintained, less features |

**References**:
- https://rich.readthedocs.io/
- https://rich.readthedocs.io/en/stable/panels.html
- https://rich.readthedocs.io/en/stable/tables.html

### Data Validation: pydantic

**Decision**: Use `pydantic>=2.5.0` for data models.

**Rationale**:
- Runtime type validation with clear error messages
- JSON serialization/deserialization
- Seamless integration with typer (CLI argument validation)
- Python 3.13+ with full type hints support
- Foundation for Phase II (API validation)

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| `dataclasses` (stdlib) | No runtime validation, no JSON serialization |
| `marshmallow` | More verbose schema definition, slower |
| `attrs` | No built-in validation, requires additional libraries |

**References**:
- https://docs.pydantic.dev/latest/
- https://docs.pydantic.dev/latest/concepts/models/

### Testing: pytest

**Decision**: Use `pytest>=7.4.0` with `pytest-cov>=4.1.0` and `pytest-mock>=3.12.0`.

**Rationale**:
- Industry standard for Python testing
- Rich assertion introspection (better error messages)
- Fixture system for setup/teardown
- Built-in coverage reporting
- Easy mocking of dependencies

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| `unittest` (stdlib) | Verbose, less readable, complex fixtures |
| `nose2` | Deprecated/unmaintained project |

**References**:
- https://docs.pytest.org/
- https://pytest-cov.readthedocs.io/

## Architecture Patterns

### Service Layer Pattern

**Decision**: Separate business logic from CLI using service classes.

**Pattern**:
```python
# Service interface (protocol)
class TaskServiceProtocol(Protocol):
    def create(self, title: str, ...) -> Task: ...
    def get_by_id(self, task_id: int) -> Task | None: ...
    def list_all(self) -> list[Task]: ...
    # ...

# Implementation
class TaskService:
    def __init__(self, store: TaskStoreProtocol) -> None:
        self._store = store
    # ... business logic
```

**Benefits**:
- **SRP**: Services own business rules, CLI handles I/O
- **Testability**: Services tested without CLI setup
- **Reusability**: Services can be reused in Phase II web API
- **OCP**: New storage backends via protocol injection

### Repository Pattern (In-Memory)

**Decision**: Use repository pattern with in-memory storage.

**Pattern**:
```python
class InMemoryTaskStore:
    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def save(self, task: Task) -> Task: ...
    def find_by_id(self, task_id: int) -> Task | None: ...
    def find_all(self) -> list[Task]: ...
    # ...
```

**Benefits**:
- Clear storage interface (protocol)
- Easy to swap for database in Phase II
- Simple testing with in-memory fixtures

### Menu State Machine

**Decision**: Use state machine pattern for menu navigation.

**Pattern**:
```python
class MenuState(Enum):
    MAIN = "main"
    TASK_MANAGEMENT = "task_management"
    USER_MANAGEMENT = "user_management"
    # ...

class MenuService:
    def __init__(self) -> None:
        self._state: MenuState = MenuState.MAIN
        self._history: list[MenuState] = []

    def navigate(self, option: str) -> None:
        # Update state based on option
        # Push to history for "Back" support
```

**Benefits**:
- Clear current menu tracking
- Consistent navigation (Back, Exit)
- Easy to add new menus

## Best Practices

### Error Handling

**Principle**: Never let exceptions escape to CLI.

**Pattern**:
```python
def safe_execute(action: Callable, error_prefix: str = "") -> None:
    try:
        action()
    except ValidationError as e:
        console.print(f"[ERROR] {error_prefix}{e}", style="red")
    except NotFoundError as e:
        console.print(f"[ERROR] {e}", style="red")
    except Exception as e:
        console.print(f"[ERROR] Unexpected error: {e}", style="red")
        logger.exception("Unexpected error")
```

### Input Validation

**Principle**: Validate early and clearly.

**Pattern**:
```python
def prompt_for_task_title(console: Console) -> str:
    while True:
        title = console.input("[bold]Enter task title:[/bold] ")
        if not title.strip():
            console.print("[ERROR] Title is required.", style="red")
            continue
        if len(title) > 200:
            console.print("[ERROR] Title too long (max 200 chars).", style="red")
            continue
        return title.strip()
```

### Color Coding (Rich)

**Principle**: Consistent color scheme from spec.

| Element | Color | Rich Style |
|---------|-------|------------|
| High Priority | Red | `red` or `bold red` |
| Medium Priority | Yellow | `yellow` or `bold yellow` |
| Low Priority | Blue | `blue` or `bold blue` |
| Done Status | Green | `green` or `bold green` |
| Success Messages | Green Panel | `panel(style="green")` |
| Error Messages | Red | `style="red"` |

## Performance Considerations

### In-Memory Operations

**Expected Performance** (all easily achievable):
- Menu transitions: <0.5s (SC-003) - trivial with in-memory
- List 1,000 tasks: <2s (SC-005) - dict lookup is O(1)
- Create task: <5s - single dict insertion

**Optimization Techniques**:
- Use dict for O(1) lookups by ID
- Pre-compute workload counts (avoid repeated iteration)
- Lazy rendering (only render visible items in tables)

## Security Considerations

### Input Sanitization

**Phase I Constraints**: No authentication, but validate all inputs.

**Measures**:
- Pydantic models enforce type and value constraints
- Length limits on all string inputs
- Enum validation for status/priority/role
- No SQL injection (no SQL)
- No command injection (no subprocess calls)

## Unknowns Resolved

All technical unknowns from the specification have been resolved:

| Unknown | Resolution |
|---------|------------|
| CLI framework | typer (modern, type-safe) |
| Terminal UI | rich (tables, panels, colors) |
| Data models | pydantic (validation, serialization) |
| Testing | pytest (industry standard) |
| Package manager | UV (constitution-specified) |
| Python version | 3.13+ (constitution-specified) |

## References

- **Project Constitution**: `.specify/memory/constitution.md`
- **Feature Specification**: `specs/001-console-task-distribution/spec.md`
- **Typer Documentation**: https://typer.tiangolo.com/
- **Rich Documentation**: https://rich.readthedocs.io/
- **Pydantic Documentation**: https://docs.pydantic.dev/
- **Pytest Documentation**: https://docs.pytest.org/
