---
id: 0001
title: TeamFlow Console App Specification
stage: spec
date: 2025-01-15
surface: agent
model: claude-opus-4-5-20251101
feature: 001-console-task-distribution
branch: 001-console-task-distribution
user: owais_abdullah
command: /sp.specify
labels: ["spec", "console-app", "task-distribution", "phase1", "interactive-ux"]
links:
  spec: specs/001-console-task-distribution/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/001-console-task-distribution/spec.md
 - specs/001-console-task-distribution/checklists/requirements.md
tests:
 - No tests (specification document)
---

## Prompt

# Phase 1: TeamFlow Console App Specification Prompt

You are acting as the **Chief Architect** for TeamFlow. Your goal is to generate the **Specify (Requirement Specification)** for Phase 1 of the project.

## Context
We are building **TeamFlow**, a CRM for Agencies.
**Phase 1** is the foundation: an **In-Memory Python Console Application**.
While it is a "Todo List" at its core, it must be flavored as a **Task Distribution System** for an agency, not just a personal checklist.

---

### 1. Project Overview
- **Name:** TeamFlow CLI (Phase 1)
- **Type:** Python Console Application
- **UX Goal:** Professional, color-coded, and structured output using the `rich` library.
- **Persistence:** In-Memory (Global dictionaries/lists) for this phase. Data resets on exit.

### 2. User Stories & Core Features

#### A. Agency Management (The "Team" Aspect)
*As an Agency Manager, I want to...*
- **Create Users:** Add team members with roles (Admin, Developer, Designer) and skills.
- **Create Teams:** Group users (e.g., "Frontend Squad").
- **List Resources:** View all users and teams with their current workload (count of active tasks).

#### B. Task Management (The "CRUD" Aspect)
*As a Team Member, I want to...*
- **Add Task:** Create a task with:
    - `Title` (Required)
    - `Description` (Optional)
    - `Priority` (High, Medium, Low)
    - `Status` (Todo, In Progress, Done)
- **Assign Task:** Assign a task to a specific User or leave it unassigned (Backlog).
- **Update Task:** Modify title, priority, or re-assign.
- **Complete Task:** Mark status as "Done".
- **Delete Task:** Remove a task.

#### C. Views & Reporting
*As a User, I want to...*
- **List All Tasks:** Table view showing ID, Title, Assignee, Priority, Status.
- **Filter Tasks:**
    - By Assignee (`--assignee john`)
    - By Status (`--status todo`)
    - By Priority (`--priority high`)
- **Visual Feedback:** See "High" priority in Red, "Done" status in Green.

### 3. Technical Constraints & Standards (from Constitution)
- **Language:** Python 3.13+
- **Package Manager:** UV
- **CLI Framework:** `typer` (for modern, type-safe commands)
- **UI Library:** `rich` (for tables, panels, and colors)
- **Architecture:**
    - **Service Layer:** `TaskService`, `UserService` (separate logic from CLI).
    - **Models:** Pydantic models (even if in-memory) to enforce data structure.
    - **Testing:** `pytest` with 80%+ coverage.
- **No Database:** Strictly in-memory structures (Lists/Dicts).

### 4. Acceptance Criteria Examples
- **Scenario: Create Task**
    - Input: `teamflow create task "Fix Navbar" --priority High --assign-to "Sarah"`
    - Output: `[SUCCESS] Task #1 "Fix Navbar" created and assigned to Sarah.` (Displayed in a Green Panel)
- **Scenario: List Tasks**
    - Input: `teamflow list`
    - Output: A Rich Table with columns: [ID, Title, Priority, Assigned To, Status].
- **Scenario: Invalid Assignment**
    - Input: `assign task 1 to "UnknownUser"`
    - Output: `[ERROR] User "UnknownUser" not found.` (Displayed in Red).

---

## Output Requirement
Please generate the spec file reflecting these requirements, ensuring it maps strictly to the **TeamFlow Constitution**.

## Response snapshot

Successfully created specification for TeamFlow Console App (Phase 1) at `specs/001-console-task-distribution/spec.md`.

**Specification Contents:**

**User Stories (5 prioritized):**
1. **P0 - Interactive Menu Navigation** 🎯 Foundation: No command memorization, arrow key + number selection
2. **P1 - Task Lifecycle Management** 🎯 MVP: Create, view, update, complete, delete tasks through prompts
3. **P2 - Task Assignment & Distribution**: Assign by selecting from numbered user list
4. **P3 - Team & Resource Management**: Create users/teams through guided prompts
5. **P4 - Task Filtering & Views**: Filter by menu selection
6. **P5 - Quick Actions**: Keyboard shortcuts (c=create, l=list, q=quit)

**Functional Requirements (46 total):**
- Interactive Menu (FR-000 to FR-006): Main menu, sub-menus, navigation, shortcuts hint
- Task Management (FR-007 to FR-014): Step-by-step prompts, numbered list selections
- Task Assignment (FR-015 to FR-019): Select from user list, unassigned option
- User & Team Management (FR-020 to FR-024): Guided creation, role selection
- View & Filtering (FR-025 to FR-028): Tables, filter menu
- Keyboard Shortcuts (FR-029 to FR-032): c, l, q, task number
- Visual Feedback (FR-033 to FR-039): Highlight, color coding
- Error Handling (FR-040 to FR-043): Re-prompt, validation, confirmations
- CLI Fallback (FR-044 to FR-045): Optional commands for power users

**Key Entities:**
- Task: ID, title, description, priority, status, assignee, created timestamp
- User: name, role, skills, tasks relationship
- Team: name, members, users relationship

**Success Criteria (10 measurable):**
- SC-001: 100% new users create first task within 60 seconds without documentation
- SC-002: Navigate any feature using only arrow keys + Enter
- SC-003: Menu transitions in <0.5 seconds
- SC-004: Create task with full details in <30 seconds
- SC-005: Support 1,000 tasks with <2s operations
- SC-006: Color-coded feedback immediately recognizable
- SC-007: All error messages provide clear next-step guidance
- SC-008: Return to main menu with single key (q or Escape)
- SC-009: 90% users report no command memorization needed
- SC-010: Keyboard shortcuts work consistently

**Quality Validation:** ✅ PASSED - All criteria met

## Outcome

- ✅ Impact: Complete specification for Phase 1 console app with 5 prioritized user stories (P0-P5), 46 functional requirements, and 10 measurable success criteria
- 🧪 Tests: No tests (specification document)
- 📁 Files: `specs/001-console-task-distribution/spec.md` (255 lines), `specs/001-console-task-distribution/checklists/requirements.md` (validation checklist)
- 🔁 Next prompts: `/sp.plan` to generate architecture design
- 🧠 Reflection: **Major UX improvement added** - Interactive menu-driven interface eliminates need for command memorization. All actions discoverable through numbered menus and arrow key navigation. Users can create tasks through step-by-step prompts instead of CLI flags.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Specification Quality Checklist: PASSED
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to `/sp.plan` for architecture design

## Update History (2025-01-15)

**UX Improvement Request**: User wanted improved UX so users don't have to remember commands.

**Changes Made**:
1. Added User Story 0 (P0) for Interactive Menu Navigation
2. Added UX Model Overview section with example main menu
3. Updated all user stories to use interactive prompts instead of CLI commands
4. Added 14 new functional requirements for menu navigation, numbered selections, keyboard shortcuts
5. Updated success criteria to measure discoverability and ease of use
6. Added edge cases for menu navigation errors
7. Marked CLI commands as optional fallback for power users (FR-044, FR-045)
