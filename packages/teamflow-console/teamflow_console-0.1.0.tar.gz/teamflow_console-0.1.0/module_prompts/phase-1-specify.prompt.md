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
