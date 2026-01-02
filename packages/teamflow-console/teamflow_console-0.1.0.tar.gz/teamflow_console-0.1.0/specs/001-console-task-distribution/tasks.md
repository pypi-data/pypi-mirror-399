# Tasks: TeamFlow Console App (Phase 1)

**Input**: Design documents from `/specs/001-console-task-distribution/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/menu-flow.md ✅
**Tests**: TDD approach specified in constitution - 80%+ coverage target with pytest

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US0-US5)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths below match the plan.md project structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory structure per plan.md (src/{models,services,cli,lib}, tests/{unit,integration,contract})
- [X] T002 Create pyproject.toml with dependencies: typer>=0.12.0, rich>=13.7.0, pydantic>=2.5.0, pytest>=7.4.0, pytest-cov>=4.1.0, pytest-mock>=3.12.0
- [X] T003 [P] Create .python-version file specifying Python 3.13+
- [X] T004 [P] Create requirements.txt with development dependencies: black>=23.12.0, isort>=5.13.0, pylint>=3.0.0, mypy>=1.7.0
- [X] T005 [P] Create setup.cfg with black, isort, pylint, mypy configurations (100-char line limit)
- [X] T006 [P] Create .gitignore for Python (.venv/, __pycache__/, *.pyc, .pytest_cache/, .coverage, htmlcov/)
- [X] T007 Create README.md with quickstart instructions from quickstart.md
- [X] T008 [P] Create tests/__init__.py and tests/conftest.py with pytest fixtures for console, storage mocks
- [X] T009 [P] Create src/__init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Storage Layer (In-Memory)

- [X] T010 Create src/lib/__init__.py
- [X] T011 [P] Implement in-memory storage singleton in src/lib/storage.py with global task/user/team dicts and next_id counters
- [X] T012 [P] Implement InMemoryTaskStore class in src/lib/storage.py with save/find_by_id/find_all/delete methods per data-model.md protocol
- [X] T013 [P] Implement InMemoryUserStore class in src/lib/storage.py with save/find_by_id/find_by_name/find_all/name_exists methods per data-model.md protocol
- [X] T014 [P] Implement InMemoryTeamStore class in src/lib/storage.py with save/find_by_id/find_all/name_exists methods per data-model.md protocol

### Data Models (Pydantic)

- [X] T015 [P] Create src/models/__init__.py
- [X] T016 [P] Implement Priority enum (HIGH/MEDIUM/LOW) and Status enum (TODO/IN_PROGRESS/DONE) in src/models/task.py
- [X] T017 [P] Implement Task Pydantic model in src/models/task.py per data-model.md with validators for title, priority, status, assignee_id, created_at
- [X] T018 [P] Implement Role enum (ADMIN/DEVELOPER/DESIGNER) in src/models/user.py
- [X] T019 [P] Implement User Pydantic model in src/models/user.py per data-model.md with validators for name (unique), role, skills (deduplicated)
- [X] T020 [P] Implement Team Pydantic model in src/models/team.py per data-model.md with validators for name (unique), member_names (deduplicated)

### Service Layer Protocols

- [X] T021 Create src/services/__init__.py
- [X] T022 [P] Define TaskStoreProtocol in src/services/task_service.py with save/find_by_id/find_all/find_by_assignee/find_by_status/find_by_priority/delete methods
- [X] T023 [P] Define UserStoreProtocol in src/services/user_service.py with save/find_by_id/find_by_name/find_all/name_exists methods
- [X] T024 [P] Define TeamStoreProtocol in src/services/team_service.py with save/find_by_id/find_all/name_exists methods

### CLI Infrastructure

- [X] T025 Create src/cli/__init__.py
- [X] T026 [P] Implement Rich console instance in src/lib/formatting.py with color styles (red, green, yellow, blue, bold)
- [X] T027 [P] Implement box-drawing border rendering in src/lib/formatting.py with Unicode chars (─│┌┐└┘) and ASCII fallback (-|+)
- [X] T028 [P] Implement panel rendering in src/lib/formatting.py for success (green) and error (red) messages per menu-flow.md
- [X] T029 [P] Implement table rendering in src/lib/formatting.py for task lists with columns: ID, Title, Priority, Assigned To, Status
- [X] T030 [P] Implement input validation helpers in src/lib/validation.py for numbered selections, required text, enum validation

### Menu State Management

- [X] T031 Implement MenuState enum (MAIN, TASK_MANAGEMENT, USER_MANAGEMENT, VIEW_TASKS, VIEW_RESOURCES, EXIT) in src/services/menu_service.py
- [X] T032 Implement MenuService class in src/services/menu_service.py with state tracking, history stack for Back navigation, and current_state/getter

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 0 - Interactive Menu Navigation (Priority: P0) 🎯 Foundation

**Goal**: Enable discoverable navigation without command memorization - entry point to all functionality

**Independent Test**: Launch application, see main menu with numbered options, navigate using number keys (1-5) and arrow keys, return to previous menu with "0" or "b", exit with "5"

### Tests for US0 (TDD - Write First, Ensure Fail)

- [X] T033 [P] [US0] Create tests/unit/test_menu_service.py with MenuService state tests (initial state, transitions, history stack)
- [X] T034 [P] [US0] Create tests/integration/test_menu_flow.py with main menu display test (verify 5 options numbered 1-5)
- [X] T035 [P] [US0] Create tests/integration/test_menu_flow.py with number key navigation test (1→Task submenu, 2→User submenu, etc.)
- [X] T036 [P] [US0] Create tests/integration/test_menu_flow.py with Back/Escape navigation test (0/b returns to previous menu)

### Implementation for US0

- [X] T037 [P] [US0] Implement main menu display in src/cli/menus.py with box-drawing borders, 5 numbered options, shortcut hints per menu-flow.md
- [X] T038 [US0] Implement MenuService.navigate() in src/services/menu_service.py to handle number keys (1-5) and route to correct sub-menu state
- [X] T039 [US0] Implement MenuService.back() in src/services/menu_service.py to pop from history and return to previous state
- [X] T040 [US0] Implement terminal capability detection on launch in src/main.py (try arrow key detection, fall back to number-key-only per FR-002a)
- [X] T041 [P] [US0] Implement Task Management submenu in src/cli/menus.py with options: Create (1), List (2), Update (3), Complete (4), Delete (5), Back (0)
- [X] T042 [P] [US0] Implement User Management submenu in src/cli/menus.py with options: Create User (1), Create Team (2), List Users (3), List Teams (4), Back (0)
- [X] T043 [P] [US0] Implement View Tasks submenu in src/cli/menus.py with direct task list display
- [X] T044 [P] [US0] Implement View Resources submenu in src/cli/menus.py with user/team list display
- [X] T045 [US0] Implement Exit confirmation in src/cli/menus.py with "Are you sure you want to exit? [Y/n]" prompt
- [X] T046 [US0] Implement arrow key highlight in src/cli/menus.py with bold reverse video or → arrow prefix per FR-033
- [X] T047 [US0] Connect main menu to typer app in src/main.py with infinite menu loop

**Checkpoint**: At this point, users can navigate the entire menu structure without any functional features working yet

---

## Phase 4: User Story 1 - Task Lifecycle Management (Priority: P1) 🎯 MVP

**Goal**: Create, view, update, complete, and delete tasks through interactive prompts - core value proposition

**Independent Test**: Select "Create Task" → enter title "Fix Navbar", skip description, select priority "1" (High), select "0" (Unassigned) → see green success panel → select "List Tasks" → see task in table → select "Complete Task" → enter ID "1" → confirm → status changes to Done → select "Delete Task" → enter ID "1" → confirm → task removed

### Tests for US1 (TDD - Write First, Ensure Fail)

- [X] T048 [P] [US1] Create tests/unit/test_services.py with TaskService CRUD tests (create, find_by_id, find_all, update_status, delete)
- [X] T049 [P] [US1] Create tests/unit/test_models.py with Task Pydantic validation tests (required fields, enum values, title validator)
- [X] T050 [P] [US1] Create tests/integration/test_task_workflow.py with Create→List→Update→Complete→Delete end-to-end test
- [X] T051 [P] [US1] Create tests/contract/test_cli_contracts.py with task creation prompt contract test (verify "Enter task title:" prompt text)
- [X] T052 [P] [US1] Create tests/integration/test_task_workflow.py with error scenario tests (invalid ID, empty title validation)

### Implementation for US1

- [X] T053 [P] [US1] Implement TaskService.create() in src/services/task_service.py with ID generation, storage.save(), default Todo/Medium values
- [X] T054 [P] [US1] Implement TaskService.get_by_id() in src/services/task_service.py with storage.find_by_id() and TaskNotFoundError
- [X] T055 [P] [US1] Implement TaskService.list_all() in src/services/task_service.py with storage.find_all()
- [X] T056 [US1] Implement TaskService.update_status() in src/services/task_service.py to transition status (Todo⇄InProgress⇄Done) per data-model.md state transitions
- [X] T057 [US1] Implement TaskService.update() in src/services/task_service.py to modify title/description/priority
- [X] T058 [US1] Implement TaskService.delete() in src/services/task_service.py with storage.delete()
- [X] T059 [P] [US1] Implement create task prompt workflow in src/cli/prompts.py (title→description→priority→assignee) per menu-flow.md Step 1-4
- [X] T060 [P] [US1] Implement title prompt with validation in src/cli/prompts.py (required, 1-200 chars, non-empty, re-prompt on fail)
- [X] T061 [P] [US1] Implement description prompt in src/cli/prompts.py (optional, max 1000 chars, Enter to skip)
- [X] T062 [P] [US1] Implement priority numbered selection in src/cli/prompts.py ([1] High [2] Medium [3] Low, default=2) per menu-flow.md Step 3
- [X] T063 [US1] Implement assignee selection in src/cli/prompts.py ([0] Unassigned, show user count, "No users available" fallback) per menu-flow.md Step 4
- [X] T064 [P] [US1] Implement list tasks table rendering in src/cli/prompts.py with ID, Title, Priority (colored), Assignee, Status columns per FR-025
- [X] T065 [P] [US1] Implement priority color coding in src/cli/prompts.py (High=red, Medium=yellow, Low=blue) per FR-034/FR-038/FR-039
- [X] T066 [P] [US1] Implement status color coding in src/cli/prompts.py (Done=green) per FR-035
- [X] T067 [US1] Implement complete task workflow in src/cli/prompts.py (enter ID, validate exists, confirm Y/n, update_status to Done, show green panel)
- [X] T068 [US1] Implement update task workflow in src/cli/prompts.py (enter ID, select field [1]Title/[2]Description/[3]Priority/[4]Status/[5]Assignee/[0]Cancel, enter new value)
- [X] T069 [US1] Implement delete task workflow in src/cli/prompts.py (enter ID, validate exists, confirm Y/n with warning, delete, show green panel)
- [X] T070 [US1] Connect Task Management submenu actions to workflows in src/cli/menus.py (1→create, 2→list, 3→update, 4→complete, 5→delete)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can manage their personal task list

---

## Phase 5: User Story 2 - Task Assignment & Distribution (Priority: P2)

**Goal**: Assign tasks to team members through interactive numbered selection - transforms personal todo into team tool

**Independent Test**: Create users Sarah, John, Mike → create task → at assignee prompt see "[0] Unassigned [1] Sarah [2] John [3] Mike" → select "1" → task assigned → list tasks shows Sarah in Assigned To column → filter by assignee shows only Sarah's tasks

### Tests for US2 (TDD - Write First, Ensure Fail)

- [ ] T071 [P] [US2] Create tests/unit/test_services.py with UserService.create() tests (ID generation, name uniqueness validation)
- [ ] T072 [P] [US2] Create tests/unit/test_services.py with UserService.get_all() tests (return user list with active task counts)
- [ ] T073 [P] [US2] Create tests/integration/test_user_workflow.py with user creation workflow test (name→role→skills)
- [ ] T074 [P] [US2] Create tests/integration/test_task_workflow.py with assign→filter→verify workflow test
- [ ] T075 [P] [US2] Create tests/contract/test_validation_contracts.py with duplicate user name validation test

### Implementation for US2

- [X] T076 [P] [US2] Implement UserService.create() in src/services/user_service.py with ID generation, storage.save(), name uniqueness check
- [X] T077 [P] [US2] Implement UserService.get_by_id() in src/services/user_service.py with storage.find_by_id()
- [X] T078 [P] [US2] Implement UserService.get_by_name() in src/services/user_service.py with name index lookup
- [X] T079 [P] [US2] Implement UserService.get_all() in src/services/user_service.py with storage.find_all()
- [X] T080 [P] [US2] Implement UserService.name_exists() in src/services/user_service.py for duplicate detection
- [X] T081 [P] [US2] Implement UserService.get_active_task_count() in src/services/user_service.py (count tasks with status≠Done by user_id)
- [X] T082 [P] [US2] Implement TaskService.assign() in src/services/task_service.py with user exists validation, set assignee_id
- [X] T083 [P] [US2] Implement TaskService.get_assignee_name() in src/services/task_service.py (return "Unassigned" if None, else fetch user name)
- [X] T084 [P] [US2] Implement create user prompt in src/cli/prompts.py (name→role numbered selection→skills comma-separated) per menu-flow.md
- [X] T085 [P] [US2] Implement role numbered selection in src/cli/prompts.py ([1] Admin [2] Developer [3] Designer) per FR-021
- [X] T086 [P] [US2] Implement skills input in src/cli/prompts.py (comma-separated, optional, store as deduplicated list)
- [X] T087 [P] [US2] Implement assignee selection with task count display in src/cli/prompts.py (show "[1] Sarah (2 tasks)" per menu-flow.md)
- [X] T088 [US2] Implement workload warning (5+ active tasks) in src/cli/prompts.py per FR-024a ("Warning: User 'Name' has N active tasks. Continue? [Y/n]")
- [X] T089 [US2] Implement task assignment workflow in src/cli/prompts.py (enter task ID, show user list with counts, workload warning, call TaskService.assign())
- [X] T090 [US2] Update list tasks table to show assignee name (not ID) in src/cli/prompts.py, use "Unassigned" when None per FR-019
- [X] T091 [US2] Update TaskService.update() to support changing assignee_id in src/services/task_service.py
- [X] T092 [US2] Connect User Management submenu actions in src/cli/menus.py (1→create user, 3→list users)

**Checkpoint**: At this point, tasks can be assigned to users and viewed by assignee

---

## Phase 6: User Story 3 - Team & Resource Management (Priority: P3)

**Goal**: Create users with roles/skills, create teams with members, view resource workload summaries

**Independent Test**: Create user John (Developer, Python,FastAPI) → create team "Frontend Squad" → select members [1] John → list teams shows "Frontend Squad" with John as member → view resources shows John with "Role: Developer | Tasks: 3 active | Skills: Python, FastAPI"

### Tests for US3 (TDD - Write First, Ensure Fail)

- [ ] T093 [P] [US3] Create tests/unit/test_services.py with TeamService.create() tests (ID generation, name uniqueness, member validation)
- [ ] T094 [P] [US3] Create tests/unit/test_services.py with TeamService.get_all() tests (return team list with members)
- [ ] T095 [P] [US3] Create tests/integration/test_user_workflow.py with team creation workflow test (name→select members→validate)
- [ ] T096 [P] [US3] Create tests/integration/test_user_workflow.py with workload summary display test

### Implementation for US3

- [X] T097 [P] [US3] Implement TeamService.create() in src/services/team_service.py with ID generation, storage.save(), name uniqueness check
- [X] T098 [P] [US3] Implement TeamService.get_by_id() in src/services/team_service.py with storage.find_by_id()
- [X] T099 [P] [US3] Implement TeamService.get_all() in src/services/team_service.py with storage.find_all()
- [X] T100 [P] [US3] Implement TeamService.name_exists() in src/services/team_service.py for duplicate detection
- [X] T101 [P] [US3] Implement create team prompt in src/cli/prompts.py (team name→select members with numbered list, at least one required)
- [X] T102 [P] [US3] Implement member selection in src/cli/prompts.py (numbered list of existing users, comma-separated input, validate all exist)
- [X] T103 [US3] Implement view resources display in src/cli/prompts.py (list all users with Role, Tasks count, Skills per FR-024)
- [X] T104 [US3] Implement view teams display in src/cli/prompts.py (list all teams with member names and each member's task count per FR-028)
- [X] T105 [US3] Connect User Management submenu: create team action in src/cli/menus.py (2→create team, 4→list teams)

**Checkpoint**: At this point, users and teams can be created and viewed with workload summaries

---

## Phase 7: User Story 4 - Task Filtering & Views (Priority: P4)

**Goal**: Filter tasks by status, priority, assignee through menu-driven selections

**Independent Test**: Create tasks with various statuses/priorities/assignees → select "View Tasks" → press Enter to see filter menu → select "[2] By Status" → select "[1] Todo" → see only Todo tasks → select "[1] All Tasks" → see all tasks

### Tests for US4 (TDD - Write First, Ensure Fail)

- [ ] T106 [P] [US4] Create tests/unit/test_services.py with TaskService.filter_by_status() tests
- [ ] T107 [P] [US4] Create tests/unit/test_services.py with TaskService.filter_by_priority() tests
- [ ] T108 [P] [US4] Create tests/unit/test_services.py with TaskService.filter_by_assignee() tests
- [ ] T109 [P] [US4] Create tests/integration/test_task_workflow.py with filter→display workflow test

### Implementation for US4

- [X] T110 [P] [US4] Implement TaskService.filter_by_status() in src/services/task_service.py with status enum filtering
- [X] T111 [P] [US4] Implement TaskService.filter_by_priority() in src/services/task_service.py with priority enum filtering
- [X] T112 [P] [US4] Implement TaskService.filter_by_assignee() in src/services/task_service.py with assignee_id filtering (None for unassigned)
- [X] T113 [US4] Implement filter menu display in src/cli/prompts.py ([1] All Tasks [2] By Status [3] By Priority [4] By Assignee [0] Back) per FR-026
- [X] T114 [P] [US4] Implement status filter selection in src/cli/prompts.py ([1] Todo [2] InProgress [3] Done, display filtered list)
- [X] T115 [P] [US4] Implement priority filter selection in src/cli/prompts.py ([1] High [2] Medium [3] Low, display filtered list with colors)
- [X] T116 [P] [US4] Implement assignee filter selection in src/cli/prompts.py ([0] Unassigned + user list, display filtered list)
- [X] T117 [US4] Update list tasks to show filter menu after Enter press in src/cli/prompts.py per menu-flow.md
- [X] T118 [US4] Update task table to show "No tasks found matching your criteria" message when empty per Edge Cases

**Checkpoint**: At this point, tasks can be filtered for focused views

---

## Phase 8: User Story 5 - Quick Actions (Priority: P5)

**Goal**: Keyboard shortcuts for power users to work quickly without menu navigation

**Independent Test**: At main menu, press "c" → goes directly to Create Task prompt → press "l" → shows all tasks → in task list, press "3" → shows task #3 details with actions → press "q" at any screen → returns to main menu

### Tests for US5 (TDD - Write First, Ensure Fail)

- [x] T119 [P] [US5] Create tests/integration/test_menu_flow.py with keyboard shortcut tests (c=create, l=list, q=back)
- [x] T120 [P] [US5] Create tests/integration/test_task_workflow.py with task number selection test (press number in list→show details)

### Implementation for US5

- [X] T121 [US5] Implement "c" key handler in main menu state in src/cli/menus.py (direct to Create Task prompt) per FR-029
- [X] T122 [US5] Implement "l" key handler in main menu state in src/cli/menus.py (direct to List Tasks) per FR-030
- [X] T123 [US5] Implement "q" and Escape key handlers in all menu states in src/cli/menus.py (return to main menu) per FR-031
- [x] T124 [US5] Implement task number selection in task list view in src/cli/prompts.py (press 1-9 to view task details) per FR-032
- [x] T125 [US5] Implement task detail view in src/cli/prompts.py (show task info, offer actions: Complete/Edit/Delete/Back)
- [X] T126 [US5] Update main menu shortcuts hint to include available shortcuts per FR-006

**Checkpoint**: At this point, power users can navigate quickly with keyboard shortcuts

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [X] T127 [P] Implement in-memory data loss warning on first launch in src/main.py ("⚠️ Data is stored in-memory only. All data will be lost on exit.") per Edge Cases
- [X] T128 [P] Add comprehensive error messages for all invalid operations in src/cli/prompts.py per FR-040/FR-041 (e.g., "Invalid option. Please enter a number between X and Y.")
- [X] T129 [P] Add confirmation prompts for all destructive operations in src/cli/prompts.py per FR-043 (delete requires Y/n)
- [X] T130 [P] Add task ID validation before update/delete operations in src/services/task_service.py per FR-042
- [X] T131 [P] Implement "No tasks found matching your criteria" message for empty filter results in src/cli/prompts.py per Edge Cases
- [X] T132 [P] Implement "Task created. Tip: Create users to assign tasks." message when no users exist during creation per Edge Cases
- [x] T133 Run pytest --cov=src --cov-report=term-missing and verify 80%+ coverage target
- [x] T134 Run black --check src/ tests/ and isort --check-only src/ tests/ for code style validation
- [x] T135 Run pylint src/ for linting (address critical issues)
- [x] T136 Run mypy src/ for type checking (address major issues)
- [x] T137 Validate quickstart.md instructions work (install→run→create task→list tasks)
- [x] T138 Validate all success criteria SC-001 through SC-010 are met

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US0 (Menu) can proceed independently after Foundational
  - US1 (Task CRUD) can proceed independently after Foundational
  - US2 (Assignment) integrates with US1 but independently testable
  - US3 (Teams/Users) integrates with US1/US2 but independently testable
  - US4 (Filtering) integrates with US1/US2 but independently testable
  - US5 (Shortcuts) integrates with all stories but independently testable
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US0 (Menu)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **US1 (Tasks)**: Can start after Foundational (Phase 2) - Core story, others build on it
- **US2 (Assignment)**: Can start after Foundational (Phase 2) - Requires US1 Task model, extends task operations
- **US3 (Teams)**: Can start after Foundational (Phase 2) - Independent models, integrates with task display
- **US4 (Filtering)**: Can start after Foundational (Phase 2) - Requires US1 Task model and US2 UserService
- **US5 (Shortcuts)**: Can start after US0, US1, US2, US3, US4 - Enhancement to existing flows

### Within Each User Story

- Tests MUST be written first and FAIL before implementation (TDD)
- Models before services before CLI
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003-T009)
- All Foundational model tasks marked [P] can run in parallel (T016-T020)
- All Foundational service protocol tasks marked [P] can run in parallel (T022-T024)
- All Foundational CLI infrastructure tasks marked [P] can run in parallel (T026-T030)
- Once Foundational phase completes:
  - US0-US5 can all proceed in parallel if team capacity allows
  - Within each story, all tests marked [P] can run in parallel
  - Within each story, all models marked [P] can run in parallel

---

## Parallel Example: Foundational Phase

```bash
# Launch all Pydantic models in parallel:
T016: Implement Priority/Status enums in src/models/task.py
T018: Implement Role enum in src/models/user.py
T019: Implement User Pydantic model in src/models/user.py
T020: Implement Team Pydantic model in src/models/team.py

# Launch all CLI formatting utilities in parallel:
T026: Implement Rich console instance in src/lib/formatting.py
T027: Implement box-drawing border rendering in src/lib/formatting.py
T028: Implement panel rendering in src/lib/formatting.py
T029: Implement table rendering in src/lib/formatting.py
T030: Implement input validation helpers in src/lib/validation.py
```

---

## Implementation Strategy

### MVP First (User Story 0 + User Story 1)

1. Complete Phase 1: Setup (T001-T009)
2. Complete Phase 2: Foundational (T010-T032) - CRITICAL
3. Complete Phase 3: User Story 0 - Menu Navigation (T033-T047)
4. Complete Phase 4: User Story 1 - Task CRUD (T048-T070)
5. **STOP and VALIDATE**: Test US0+US1 independently - users can navigate menus and manage tasks
6. Deploy/demo if ready (functional personal task tracker achieved)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (no user-facing value yet)
2. Add US0 (Menu) → Navigation works (no features yet)
3. Add US1 (Tasks) → **MVP DELIVERED** - Personal task tracker functional
4. Add US2 (Assignment) → Team task distribution functional
5. Add US3 (Teams) → Resource management functional
6. Add US4 (Filtering) → Enhanced views functional
7. Add US5 (Shortcuts) → Power user features functional
8. Polish → Production-ready

### Parallel Team Strategy

With multiple developers after Foundational phase:

1. Team completes Setup + Foundational together
2. Once Foundational is done, split work:
   - **Developer A**: US0 (Menu) + US5 (Shortcuts) - UI/UX focus
   - **Developer B**: US1 (Tasks) + US4 (Filtering) - Core task logic
   - **Developer C**: US2 (Assignment) + US3 (Teams) - User/team logic
3. Stories integrate and test independently
4. Final integration in Polish phase

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [US0-US5] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests written FIRST per TDD (constitution requirement), verify they fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All file paths per plan.md project structure
- Constitution compliance: SOLID, DRY, TDD (80%+), Type Safety, No `any` types

---

## Task Count Summary

- **Total Tasks**: 138
- **Setup Phase**: 9 tasks
- **Foundational Phase**: 23 tasks (BLOCKS all stories)
- **US0 (Menu)**: 15 tasks (5 tests + 10 implementation)
- **US1 (Tasks)**: 23 tasks (5 tests + 18 implementation)
- **US2 (Assignment)**: 22 tasks (5 tests + 17 implementation)
- **US3 (Teams)**: 13 tasks (4 tests + 9 implementation)
- **US4 (Filtering)**: 13 tasks (4 tests + 9 implementation)
- **US5 (Shortcuts)**: 8 tasks (2 tests + 6 implementation)
- **Polish Phase**: 12 tasks

**Parallel Opportunities**: 40 tasks marked [P] across all phases (29% of tasks)

**Suggested MVP**: Phase 1 → Phase 2 → Phase 3 (US0) → Phase 4 (US1) = 70 tasks to functional MVP
