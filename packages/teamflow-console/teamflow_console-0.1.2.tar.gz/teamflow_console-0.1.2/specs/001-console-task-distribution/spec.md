# Feature Specification: TeamFlow Console App (Phase 1)

**Feature Branch**: `001-console-task-distribution`
**Created**: 2025-01-15
**Status**: Draft
**Input**: User description: "Phase 1: TeamFlow Console App Specification Prompt - In-Memory Python CLI for Task Distribution with CRUD operations, User/Team management, and Rich UI with Interactive Menu for ease of use"

## UX Model Overview

**Primary Interaction**: Interactive Menu-Driven Interface
- Users navigate through numbered menu options (1, 2, 3...)
- No commands to memorize - all actions visible on screen
- Arrow keys or number selection for navigation
- Sub-menus for complex operations
- Prompts guide users through data entry step-by-step

**Example Main Menu Display:**
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
│ Select option [1-5]: _                      │
└─────────────────────────────────────────────┘
```

**Fallback Commands**: For advanced users, CLI commands still work
- Supports both interactive menu AND direct CLI commands
- Power users can bypass menus for speed

---

## User Scenarios & Testing *(mandatory)*

### User Story 0 - Interactive Menu Navigation (Priority: P0) 🎯 Foundation

As a New User, I want an interactive menu that shows me all available actions so that I can use the system without memorizing any commands.

**Why this priority**: Without discoverable navigation, users cannot access any features. This is the entry point to all functionality.

**Independent Test**: Can be tested by launching the application and navigating through menu options using number keys or arrow keys. Delivers immediate usability for first-time users.

**Acceptance Scenarios**:

1. **Given** the application launches, **When** I see the main menu, **Then** I see a numbered list of all available options (Task Management, User Management, View Tasks, View Resources, Exit)
2. **Given** the main menu is displayed, **When** I press "1" or select "Task Management", **Then** I see the Task Management sub-menu with options (Create Task, List Tasks, Update Task, Complete Task, Delete Task, Back)
3. **Given** any sub-menu is displayed, **When** I select "Back" or press "0", **Then** I return to the previous menu
4. **Given** I am navigating menus, **When** I use arrow keys, **Then** the selection highlight moves up/down and I can press Enter to confirm
5. **Given** the application is running, **When** I select "Exit" from main menu, **Then** the application closes with a goodbye message

---

### User Story 1 - Task Lifecycle Management (Priority: P1) 🎯 MVP

As an Agency Team Member, I want to create, view, update, and complete tasks through interactive prompts so that I can track my work without leaving my terminal or memorizing commands.

**Why this priority**: This is the core value proposition - without the ability to manage tasks, the system has no purpose. Task CRUD is the foundation for all other features.

**Independent Test**: Can be fully tested by creating tasks through interactive prompts, listing them, updating details, and marking complete. Delivers immediate value as a personal task tracker even without team features.

**Acceptance Scenarios**:

1. **Given** I selected "Create Task" from the menu, **When** prompted "Enter task title:", I type "Fix Navbar" and press Enter, **Then** the system prompts for description (optional), priority (shows numbered list: 1=High, 2=Medium, 3=Low), and creates the task with my selections
2. **Given** I selected "Create Task" and entered title "Fix Navbar", **When** prompted for priority, I see "[1] High [2] Medium [3] Low" and select "1", **Then** the task is created with "High" priority
3. **Given** task #1 exists, **When** I select "List Tasks" from the menu, **Then** I see a formatted table showing ID, Title, Priority, Assigned To, and Status columns with task #1 included
4. **Given** task #1 exists, **When** I select "Complete Task" from the menu and enter task ID "1", **Then** task #1 status changes to "Done" and I see a green success message
5. **Given** task #1 exists, **When** I select "Delete Task" from the menu and confirm the deletion, **Then** task #1 is removed and no longer appears in listings

---

### User Story 2 - Task Assignment & Distribution (Priority: P2)

As an Agency Manager, I want to assign tasks to specific team members through interactive selection so that work is distributed clearly without typing user names.

**Why this priority**: Task assignment transforms this from a personal todo list into a team tool. This is the key differentiator for agencies.

**Independent Test**: Can be tested by creating users, then assigning tasks by selecting from a numbered list of users.

**Acceptance Scenarios**:

1. **Given** users Sarah, John, and Mike exist, **When** I create a task and reach the "Assign to" prompt, **Then** I see "[0] Unassigned [1] Sarah [2] John [3] Mike" and can select by number
2. **Given** task #1 is assigned to Sarah, **When** I select "List Tasks" and choose filter by assignee, **Then** I see "[1] Sarah [2] John [3] Mike" and after selecting "1", I see only Sarah's tasks
3. **Given** task #1 is unassigned, **When** I select "Assign Task" from the menu, enter "1", and select "Sarah" from the user list, **Then** task #1 is now assigned to Sarah
4. **Given** I try to assign a task but no users exist, **When** I reach the assignee selection prompt, **Then** I see "No users available. Create users first in User Management." and the task is created as unassigned

---

### User Story 3 - Team & Resource Management (Priority: P3)

As an Agency Manager, I want to create users and teams with roles and skills through guided prompts so that I can model my agency structure and see team workload.

**Why this priority**: Resource management provides context for task assignment and enables workload balancing. Important for agencies but not required for basic task tracking.

**Independent Test**: Can be tested by creating users with roles/skills through prompts, creating teams, and listing resources to see workload summaries.

**Acceptance Scenarios**:

1. **Given** I selected "Create User" from the menu, **When** prompted for name, role (shows numbered list: 1=Admin, 2=Developer, 3=Designer), and skills, I enter "John", select "2" (Developer), and type "Python,FastAPI", **Then** user John is created with Developer role and Python/FastAPI skills
2. **Given** users John and Sarah exist, **When** I select "Create Team" and enter team name "Frontend Squad", I see members list "[1] John [2] Sarah]" and can select multiple members, **Then** team "Frontend Squad" is created containing selected users
3. **Given** John has 3 active tasks, **When** I select "View Resources" from the menu, **Then** I see John displayed with "Role: Developer | Tasks: 3 active | Skills: Python, FastAPI"
4. **Given** multiple teams exist, **When** I select "View Teams", **Then** I see all teams with their members and each member's task count

---

### User Story 4 - Task Filtering & Views (Priority: P4)

As a Team Member, I want to filter tasks by status, priority, and assignee through menu selections so that I can focus on specific work items without typing filter commands.

**Why this priority**: Filtering improves productivity but doesn't block core functionality. Tasks can still be found without filters.

**Independent Test**: Can be tested by creating tasks with various statuses/priorities/assignees and using menu-driven filters to verify correct subset is displayed.

**Acceptance Scenarios**:

1. **Given** tasks with Todo, In Progress, and Done statuses exist, **When** I select "Filter Tasks" and choose status filter, I see "[1] Todo [2] In Progress [3] Done" and select "1", **Then** only Todo tasks are displayed
2. **Given** tasks with High, Medium, Low priorities exist, **When** I select "Filter by Priority" and choose "[1] High", **Then** only High priority tasks are displayed, with priority shown in red
3. **Given** tasks assigned to different users, **When** I select "Filter by Assignee" and choose a user from the list, **Then** only that user's tasks are displayed
4. **Given** tasks exist, **When** I select "Show All Tasks", **Then** all tasks are displayed regardless of filters, and Done tasks show status in green

---

### User Story 5 - Quick Actions (Priority: P5)

As a Frequent User, I want keyboard shortcuts for common actions so that I can work quickly without navigating through multiple menus.

**Why this priority**: Power users appreciate shortcuts for speed, but they're optional - menus always work.

**Independent Test**: Can be tested by pressing keyboard shortcuts and verifying they perform the expected action.

**Acceptance Scenarios**:

1. **Given** I am at the main menu, **When** I press "c" (create), **Then** the system goes directly to "Create Task" prompt
2. **Given** I am at the main menu, **When** I press "l" (list), **Then** the system displays all tasks
3. **Given** I am viewing the task list, **When** I press a task number like "3", **Then** the system shows task details and offers actions (Complete, Edit, Delete, Back)
4. **Given** I am at any screen, **When** I press "q" or Escape, **Then** the system returns to the main menu

---

### Edge Cases

- What happens when a user enters an invalid menu option?
  - System displays "Invalid option. Please enter a number between X and Y" and re-prompts
- What happens when a user enters nothing (just presses Enter) at a required prompt?
  - System displays "This field is required" and re-promrompts
- What happens when deleting a task that is already deleted?
  - System displays error "Task #N not found" and returns to task list
- What happens when listing with a filter that matches no tasks?
  - System displays "No tasks found matching your criteria. Press Enter to continue."
- What happens when creating a task without a title (user presses Enter immediately)?
  - System displays "Title is required. Please enter a title:" and re-prompts
- What happens when creating a user with a duplicate name?
  - System displays error "User 'Name' already exists. Please choose a different name."
- What happens when data is lost on application exit (in-memory constraint)?
  - System displays warning on first launch: "⚠️  Data is stored in-memory only. All data will be lost on exit."
- What happens when assigning a task to a user who is already at maximum capacity?
  - System allows assignment but shows a warning when user has 5+ active tasks: "Warning: User 'Name' has N active tasks (high workload). Continue? [Y/n]"
- What happens when user enters text when a number is expected (e.g., priority selection)?
  - System displays "Please enter a number" and re-prompts with the options
- What happens when no users exist during task creation?
  - Task is created as unassigned, and system shows "Task created. Tip: Create users to assign tasks."

## Requirements *(mandatory)*

### Functional Requirements

**Interactive Menu Requirements:**
- **FR-000**: System MUST display an interactive main menu with numbered options for all major features upon launch
- **FR-001**: System MUST support menu navigation using number keys (1, 2, 3...)
- **FR-002**: System MUST support menu navigation using arrow keys with visual highlight of selected option; when arrow keys are not supported by terminal, system MUST automatically fall back to number-key-only navigation
- **FR-002a**: System MUST detect terminal capabilities on launch; if arrow key detection fails, system MUST display menu without arrow key hints and rely solely on number keys
- **FR-003**: System MUST display sub-menus for complex operations (e.g., Task Management shows: Create, List, Update, Complete, Delete, Back)
- **FR-004**: System MUST provide a "Back" option (number 0 or "b") in all sub-menus to return to previous menu
- **FR-005**: System MUST allow users to exit the application from the main menu
- **FR-006**: System MUST display keyboard shortcuts hint at the bottom of main menu (e.g., "c=Create, l=List, q=Quit")

**Task Management Requirements:**
- **FR-007**: System MUST guide users through task creation with step-by-step prompts (title → description → priority → assignee)
- **FR-008**: System MUST generate a unique sequential ID for each task
- **FR-009**: System MUST allow users to update task details through interactive prompts
- **FR-010**: System MUST allow users to mark a task as complete through menu selection
- **FR-011**: System MUST allow users to delete tasks by ID with confirmation prompt
- **FR-012**: System MUST default new tasks to "Todo" status and "Medium" priority if not specified
- **FR-013**: System MUST display priority selection as a numbered list: [1] High [2] Medium [3] Low
- **FR-014**: System MUST display assignee selection as a numbered list: [0] Unassigned [1] User1 [2] User2 ...

**Task Assignment Requirements:**
- **FR-015**: System MUST allow users to assign a task by selecting from a numbered list of users
- **FR-016**: System MUST allow tasks to be created without an assignee (Unassigned option at position 0)
- **FR-017**: System MUST allow re-assigning tasks through the task detail view
- **FR-018**: System MUST display "No users available" message when assigning but no users exist
- **FR-019**: System MUST display assignee name as "Unassigned" when no user is assigned

**User & Team Management Requirements:**
- **FR-020**: System MUST guide users through user creation with prompts: name → role selection → skills
- **FR-021**: System MUST display role selection as a numbered list: [1] Admin [2] Developer [3] Designer
- **FR-022**: System MUST allow users to create teams by selecting members from a numbered list
- **FR-023**: System MUST prevent duplicate user names and display appropriate error
- **FR-024**: System MUST calculate and display each user's active task count (excluding "Done" status)
- **FR-024a**: System MUST display a workload warning when assigning a task to a user who has 5 or more active tasks; warning format: "Warning: User 'Name' has N active tasks (high workload). Continue? [Y/n]"

**View & Filtering Requirements:**
- **FR-025**: System MUST display all tasks in a tabular format with columns: ID, Title, Priority, Assigned To, Status
- **FR-026**: System MUST offer filtering options through a menu: [1] All Tasks [2] By Status [3] By Priority [4] By Assignee
- **FR-027**: System MUST list all users with their roles, skills, and active task counts
- **FR-028**: System MUST list all teams with their members and each member's workload

**Keyboard Shortcut Requirements:**
- **FR-029**: System MUST support "c" key to go to Create Task from main menu
- **FR-030**: System MUST support "l" key to list all tasks from main menu
- **FR-031**: System MUST support "q" or Escape key to return to main menu from any screen
- **FR-032**: System MUST support pressing a task number in the task list to view task details

**Visual Feedback Requirements:**
- **FR-033**: System MUST highlight the currently selected menu option when using arrow keys by displaying the selected option text in **bold reverse video** (inverted foreground/background colors) or with a `→` arrow prefix to the option text
- **FR-033a**: System MUST render menu borders using Unicode box-drawing characters: `─` (U+2500) for horizontal lines, `│` (U+2502) for vertical lines, `┌` (U+250C), `┐` (U+2510), `└` (U+2514), `┘` (U+2518) for corners; fall back to ASCII `-`, `|`, `+` if Unicode not supported
- **FR-034**: System MUST display High priority tasks in red color
- **FR-035**: System MUST display Done status in green color
- **FR-036**: System MUST display success messages in green panels
- **FR-037**: System MUST display error messages in red color
- **FR-038**: System MUST display Medium priority in yellow color
- **FR-039**: System MUST display Low priority in blue color

**Error Handling Requirements:**
- **FR-040**: System MUST display user-friendly error messages for all invalid operations
- **FR-041**: System MUST re-prompt when invalid input is provided (e.g., text when number expected)
- **FR-042**: System MUST validate task IDs exist before update/delete operations
- **FR-043**: System MUST display confirmation prompt before destructive operations (delete)

**CLI Fallback Requirements (Optional/Advanced):**
- **FR-044**: System MAY support direct CLI commands for power users (e.g., `teamflow create task "Fix bug" --priority high`)
- **FR-045**: System MAY display command hints at the bottom of screens for users who want to learn shortcuts

### Key Entities

- **Task**: Represents a work item with attributes: unique ID, title (required), description (optional), priority (High/Medium/Low), status (Todo/In Progress/Done), assignee (User or null), created timestamp
- **User**: Represents a team member with attributes: unique name, role (Admin/Developer/Designer), skills (list of strings), relationship to Tasks (many-to-one via assignee)
- **Team**: Represents a group of users with attributes: unique name, members (list of Users), relationship to Users (one-to-many)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of new users can navigate to and complete their first task creation within 60 seconds without documentation
- **SC-002**: Users can navigate to any feature using only the arrow keys and Enter button
- **SC-003**: Menu transitions complete in under 0.5 seconds with no noticeable lag
- **SC-004**: Users can create a task with full details (title, description, priority, assignee) in under 30 seconds using interactive prompts
- **SC-005**: System supports up to 1,000 tasks with list/filter operations completing in under 2 seconds
- **SC-006**: Color-coded visual feedback (red for errors/high priority, green for success/done status) is immediately recognizable without prior explanation
- **SC-007**: All error messages provide clear guidance including what went wrong and what to do next (e.g., "Invalid option. Please enter a number between 1 and 5.")
- **SC-008**: Users can return to the main menu from any screen using a single key press (q or Escape)
- **SC-009**: 90% of users report they don't need to memorize any commands to use the system effectively
- **SC-010**: Keyboard shortcuts work consistently across all screens (c=create, l=list, q=quit/back)
