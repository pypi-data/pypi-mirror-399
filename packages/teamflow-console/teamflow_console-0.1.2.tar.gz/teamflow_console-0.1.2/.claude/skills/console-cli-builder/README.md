# Console CLI Builder Skill

Battle-tested patterns for building interactive console CLI applications in Python, based on real-world implementation experience.

## What This Skill Provides

When invoked, this skill generates a complete interactive CLI application with:

- **Menu-driven navigation** - No commands to memorize
- **Beautiful terminal UI** - Rich panels, tables, colors
- **Type-safe data models** - Pydantic validation
- **Clean architecture** - Service layer with protocol-based storage
- **TDD setup** - Test suite with 80%+ coverage target
- **Production-ready patterns** - All lessons learned baked in

## Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Language | Python | 3.13+ |
| Package Manager | uv | latest |
| CLI Framework | typer | 0.12.0+ |
| Terminal UI | rich | 13.7.0+ |
| Data Validation | pydantic | 2.5.0+ |
| Testing | pytest | 7.4.0+ |

## File Structure

```
.claude/skills/console-cli-builder/
├── SKILL.md                           # Main skill definition
├── README.md                           # This file
├── lessons/
│   ├── LESSONS_LEARNED.md             # All bugs and fixes from experience
│   └── PREVENTION_CHECKLIST.md        # Pre-flight checks
├── templates/
│   ├── service-pattern.py              # Service layer with sentinel
│   ├── prompt-pattern.py               # Prompts with cancellation
│   └── quickstart-template.md         # Quick start guide
└── scripts/                            # Utility scripts
```

## Key Lessons Learned

### 1. Sentinel Pattern for Optional Parameters

**Problem**: Need to distinguish "parameter not provided" from "parameter explicitly set to None".

**Solution**: Define sentinel at module level:
```python
# At top of file
_UNSET = object()

def update(self, x: type | None | object = _UNSET):
    if x is not _UNSET:  # Was explicitly passed
        ...
```

### 2. Cancellation Handling

**Problem**: User presses 'q' to cancel, but app shows error.

**Solution**: Wrap create workflows in try/except:
```python
class CancelledException(Exception): pass

def prompt_create(self) -> None:
    try:
        # ... prompts ...
    except CancelledException:
        pass  # Silent return to menu
```

### 3. Rich Panel Import

**Problem**: `NameError: name 'Panel' is not defined`

**Solution**: Always import Panel:
```python
from rich.panel import Panel  # Easy to forget!
```

### 4. PYTHONPATH

**Problem**: `ModuleNotFoundError: No module named 'cli'`

**Solution**: Always set PYTHONPATH:
```bash
PYTHONPATH=src uv run python -m src.main
```

## Usage

Invoke the skill and describe your CLI app:
- What entities do you need? (tasks, users, projects, etc.)
- What operations? (create, list, update, delete, filter)
- Any special features? (assignment, teams, search)

The skill will generate:
1. Complete project structure
2. Pydantic models
3. Service layer with protocols
4. CLI interface (menus, prompts)
5. Test suite
6. Quick start guide

## Time Savings

- **With skill**: ~2-3 hours to fully functional CLI app
- **Without skill**: ~1-2 days of research and debugging

## Related Skills

- `deployment-engineer` - For deploying CLI apps
- `better-auth-integration` - For adding authentication (Phase II)

---

**Version**: 1.0.0
**Based On**: TeamFlow Console App (001-console-task-distribution)
**Last Updated**: 2025-01-28
