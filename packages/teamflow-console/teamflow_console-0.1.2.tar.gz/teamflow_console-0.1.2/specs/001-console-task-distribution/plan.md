# Implementation Plan: TeamFlow Console App (Phase 1)

**Branch**: `001-console-task-distribution` | **Date**: 2025-01-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-console-task-distribution/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

TeamFlow Console App (Phase 1) is an **in-memory Python command-line interface** for task distribution in small agencies. The system features an **interactive menu-driven UX** where users navigate via numbered options and arrow keys—no command memorization required. Core capabilities include task CRUD, user/team management, task assignment, and filtered views. The application uses in-memory storage (data resets on exit) as the foundation for later evolution into a full web CRM with database persistence, authentication, and AI-powered features in subsequent phases.

**Technical Approach**: Use Python 3.13+ with Typer for CLI structure and Rich for terminal UI. Implement service layer separation (TaskService, UserService) with Pydantic models for data validation. Follow TDD with pytest targeting 80%+ coverage.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: typer (CLI framework), rich (terminal UI), pydantic (data validation)
**Storage**: In-memory (Python dictionaries/lists) - no database for Phase I
**Testing**: pytest, pytest-cov, pytest-mock (for 80%+ coverage target)
**Target Platform**: Cross-platform console (Linux, macOS, Windows) via Python terminal
**Project Type**: Single project (CLI application)
**Performance Goals**:
- Menu transitions: <0.5s (SC-003)
- First task creation: <60s for new users (SC-001)
- List/filter operations: <2s for 1,000 tasks (SC-005)
**Constraints**:
- In-memory only (no persistence)
- No authentication (Phase I constraint)
- No external APIs or services
- Single-user session focus
**Scale/Scope**:
- Up to 1,000 tasks in memory
- Up to 100 users
- Up to 20 teams
- Single-terminal session (no multi-user concurrency)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Specialized Agents & Skills First**: Reviewed existing agents/skills - none directly applicable to console app development (focused on OpenAI SDK, Better Auth, deployment, etc.). Custom implementation appropriate for this phase.
- [x] **SOLID Principles**: Service layer separation planned (TaskService, UserService) following SRP. Protocol-based interfaces for future extensibility (OCP/DIP).
- [x] **DRY**: Shared utilities module planned for common validation, menu rendering logic.
- [x] **TDD**: pytest with 80%+ coverage target. Test structure: unit/ (models, services), integration/ (CLI workflows), contract/ (Pydantic validation).
- [x] **Type Safety**: Pydantic models for all entities. Type hints on all functions. No `any` types allowed.
- [x] **Security**: Phase I has no auth (per constitution), but input validation via Pydantic on all user inputs.
- [x] **Performance**: Targets defined in spec (SC-001, SC-003, SC-005). In-memory operations expected to meet all targets.
- [x] **Code Style**: Black formatter, isort for imports, pylint for linting, 100-char line limit.
- [x] **MCP Integration**: Not applicable for Phase I (no MCP tools needed for in-memory CLI).
- [x] **Phase I Constraints**: NO database (in-memory only), NO authentication, simple commands with clear output—all compliant.

**Constitution Status**: ✅ PASSED - All gates satisfied. No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/001-console-task-distribution/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── menu-flow.md     # Menu navigation contract
│   └── cli-commands.md  # CLI command contracts (optional fallback)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── main.py              # Entry point (typer CLI)
├── models/
│   ├── __init__.py
│   ├── task.py          # Task Pydantic model
│   ├── user.py          # User Pydantic model
│   └── team.py          # Team Pydantic model
├── services/
│   ├── __init__.py
│   ├── task_service.py  # Task business logic
│   ├── user_service.py  # User business logic
│   └── menu_service.py  # Menu navigation logic
├── cli/
│   ├── __init__.py
│   ├── menus.py         # Menu definitions and rendering
│   └── prompts.py       # Interactive prompt handlers
└── lib/
    ├── __init__.py
    ├── formatting.py    # Rich table/panel formatting
    ├── validation.py    # Input validation helpers
    └── storage.py       # In-memory storage singleton

tests/
├── __init__.py
├── conftest.py          # Pytest fixtures
├── unit/
│   ├── test_models.py   # Pydantic model validation tests
│   ├── test_services.py # Service logic tests
│   └── test_storage.py  # In-memory storage tests
├── integration/
│   ├── test_menu_flow.py    # Menu navigation tests
│   ├── test_task_workflow.py # End-to-end task operations
│   └── test_user_workflow.py # User/team creation tests
└── contract/
    ├── test_cli_contracts.py # CLI command interface tests
    └── test_validation_contracts.py # Pydantic validation tests
```

**Structure Decision**: Single project structure (Option 1) selected because this is a console CLI application with no frontend/backend separation. All code resides under `src/` with clear separation of models (data), services (business logic), cli (interface), and lib (utilities). Tests follow pytest conventions with unit/integration/contract separation.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | No violations | Constitution gates all passed |

---

## Phase 0: Research

*Status: Complete - No external research needed*

All technical decisions are based on:
1. Constitution-specified stack (Python 3.13+, typer, rich, pydantic, pytest)
2. Phase I constraints (in-memory, no auth, no database)
3. Spec requirements (interactive menu UX, 46 functional requirements)

### Technology Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|-------------------------|
| **typer** for CLI | Modern, type-safe CLI framework with automatic help generation. Built-in subcommand support fits menu structure. | click (older, more boilerplate), argparse (stdlib, more verbose) |
| **rich** for terminal UI | Beautiful tables, panels, progress bars. Syntax highlighting for error messages. Built-in menu rendering capabilities. | bullet (simpler, less features), blessed (curses-like, more complex), texttable (tables only) |
| **pydantic** for models | Runtime validation, type safety, JSON serialization. Integrates with typer. Clear error messages. | dataclasses (stdlib, no validation), marshmallow (more verbose) |
| **pytest** for testing | Industry standard, rich assertion introspection, fixtures for setup/teardown. Coverage reporting built-in. | unittest (stdlib, more verbose), nose2 (deprecated) |

---

## Phase 1: Design

### Data Model

See [data-model.md](./data-model.md) for complete entity definitions.

**Entity Summary:**
- **Task**: id, title, description, priority (High/Medium/Low), status (Todo/InProgress/Done), assignee_id, created_at
- **User**: name (unique), role (Admin/Developer/Designer), skills (list[str])
- **Team**: name (unique), member_names (list[str])

**Relationships:**
- Task → User (many-to-one, optional via assignee_id)
- Team → Users (one-to-many, via member_names)

**State Transitions:**
- Task status: Todo → InProgress → Done (bidirectional allowed)
- Task priority: Can change at any time
- Task assignment: Can change at any time (including to/from Unassigned)

### API Contracts

See [contracts/](./contracts/) for interface definitions.

**CLI Menu Interface:**
```
Main Menu:
  - Display: Numbered list with keyboard shortcut hints
  - Input: Single digit (1-5) or letter (c, l, q) or arrow keys + Enter
  - Output: Navigate to submenu or execute action

Task Management Submenu:
  - Display: Numbered list (Create, List, Update, Complete, Delete, Back)
  - Input: Single digit (0-6)
  - Output: Execute action or return to main menu

Prompts:
  - Title: Free text (required, non-empty)
  - Description: Free text (optional)
  - Priority: Numbered selection [1] High [2] Medium [3] Low
  - Assignee: Numbered selection [0] Unassigned [1+] User names
  - Role: Numbered selection [1] Admin [2] Developer [3] Designer
```

**Optional CLI Commands (FR-044):**
```
teamflow create task "<title>" [--priority <High|Medium|Low>] [--assign-to <name>]
teamflow list [--status <status>] [--priority <priority>] [--assignee <name>]
teamflow complete <task-id>
teamflow delete <task-id>
teamflow create user <name> --role <Admin|Developer|Designer> [--skills <csv>]
teamflow create team <name> --members <csv-names>
```

### Quick Start

See [quickstart.md](./quickstart.md) for setup and usage instructions.

**Development Setup:**
```bash
# Install UV (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install typer rich pydantic pytest pytest-cov pytest-mock

# Run application
python -m src.main

# Run tests
pytest --cov=src --cov-report=term-missing
```

**First Run Experience:**
1. Launch `python -m src.main`
2. See main menu with 5 options
3. Press `1` → Task Management submenu
4. Press `1` → Create Task prompt
5. Enter title, description (skip), priority (1=High), assignee (0=Unassigned)
6. Task created in under 60 seconds (SC-001)

---

## Architecture Decisions

### Service Layer Pattern

**Decision**: Separate business logic from CLI interface using service classes.

**Rationale**:
- **SRP**: Services handle logic, CLI handles I/O
- **Testability**: Services can be tested without CLI setup
- **Future-proofing**: Services can be reused in Phase II (web API)

**Architecture:**
```
┌─────────────────────────────────────┐
│         CLI Layer (typer)           │
│  - Commands, menus, prompts         │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│       Service Layer                 │
│  - TaskService, UserService         │
│  - Business logic, validation       │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Pydantic Models             │
│  - Task, User, Team                 │
│  - Data validation, serialization   │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      In-Memory Storage              │
│  - Global dict/lists                │
│  - TaskRepository, UserRepository   │
└─────────────────────────────────────┘
```

### Menu State Management

**Decision**: Use a state machine pattern for menu navigation.

**Rationale**:
- Clear current menu tracking
- Easy to add new menus
- Handles "Back" and "Exit" consistently

**State Diagram:**
```
        [Launch]
           │
           ▼
    [Main Menu]
           │
     ┌─────┼─────┐
     │     │     │
     ▼     ▼     ▼
[Task] [User] [View]  ────▶ [Exit]
     │     │     │
     ▼     ▼     ▼
[Action][Action][Filter]
     │     │     │
     └─────┴─────┘
           │
           ▼
    [Return to Main]
```

### Error Handling Strategy

**Decision**: Never raise exceptions to CLI—catch and display user-friendly messages.

**Pattern**:
```python
try:
    # Business logic
except TaskNotFoundError as e:
    console.print(f"[ERROR] {e}", style="red")
    # Re-prompt or return to menu
except ValidationError as e:
    console.print(f"[ERROR] Invalid input: {e}", style="red")
    # Re-prompt with current value preserved
```

---

## Testing Strategy

### Unit Tests (Target: 80%+ coverage)

**Models** (`tests/unit/test_models.py`):
- Pydantic validation (required fields, enum values)
- Model methods (if any)
- Serialization/deserialization

**Services** (`tests/unit/test_services.py`):
- TaskService: CRUD operations, assignment logic
- UserService: User/team creation, uniqueness validation
- MenuService: Navigation state, option filtering

**Storage** (`tests/unit/test_storage.py`):
- InMemoryTaskStore: CRUD, queries, filtering
- InMemoryUserStore: CRUD, uniqueness, queries

### Integration Tests

**Menu Flow** (`tests/integration/test_menu_flow.py`):
- Navigate main menu → submenu → action → back
- Keyboard shortcut (c, l, q) functionality
- Arrow key navigation (if terminal supports)

**Workflows** (`tests/integration/test_task_workflow.py`):
- Create → List → Update → Complete → Delete
- Create → Assign → Filter by assignee
- Error scenarios: invalid ID, duplicate user, etc.

### Contract Tests

**CLI Interface** (`tests/contract/test_cli_contracts.py`):
- Verify menu options match spec (numbered, correct labels)
- Verify prompt text matches spec ("Enter task title:", etc.)
- Verify error messages match edge cases

**Validation** (`tests/contract/test_validation_contracts.py`):
- Pydantic model validation rules
- Input sanitization (empty strings, invalid numbers, etc.)

---

## Dependencies

### Runtime Dependencies

```txt
# Core
typer>=0.12.0          # CLI framework
rich>=13.7.0           # Terminal UI
pydantic>=2.5.0        # Data validation

# Testing (dev)
pytest>=7.4.0          # Test runner
pytest-cov>=4.1.0      # Coverage reporting
pytest-mock>=3.12.0    # Mocking support
```

### Development Tools

```txt
# Code quality
black>=23.12.0         # Formatter
isort>=5.13.0          # Import sorting
pylint>=3.0.0          # Linting

# Type checking
mypy>=1.7.0            # Static type checking
```

---

## Next Steps

1. **Immediate**: Run `/sp.tasks` to generate actionable implementation tasks
2. **After Tasks**: Run `/sp.implement` to execute the implementation
3. **During Implementation**: Run tests frequently (`pytest -xvs`)
4. **Completion**: Verify all success criteria (SC-001 through SC-010)

---

## Appendix: Phase Evolution

This console app (Phase I) evolves as follows:

| Phase | Additions | Changes to Current Code |
|-------|-----------|-------------------------|
| I | In-memory CLI | **Current** - foundation |
| II | PostgreSQL, Better Auth, REST API | Service layer reused, new API layer |
| III | OpenAI Agents SDK, MCP tools | New chatbot interface, same models |
| IV | Docker, Kubernetes, Helm | Containerization, same CLI core |
| V | Kafka, Dapr, microservices | Event-driven extensions |

**Design for Evolution**: Service interfaces use protocols (abstract base classes) to enable swapping in-memory storage for database (Phase II) without changing business logic.
