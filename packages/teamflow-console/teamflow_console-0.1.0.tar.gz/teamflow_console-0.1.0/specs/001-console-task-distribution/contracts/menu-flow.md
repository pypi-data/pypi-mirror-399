# Menu Flow Contract

**Feature**: 001-console-task-distribution
**Date**: 2025-01-15

## Purpose

Defines the expected behavior, inputs, and outputs for all interactive menu flows in the TeamFlow Console App.

## Rendering Specifications

### Box-Drawing Characters

**Primary (Unicode)**:
- Horizontal: `─` (U+2500)
- Vertical: `│` (U+2502)
- Top-left: `┌` (U+250C), Top-right: `┐` (U+2510)
- Bottom-left: `└` (U+2514), Bottom-right: `┘` (U+2518)
- Left-T: `├` (U+251C), Right-T: `┤` (U+2524)

**Fallback (ASCII)** - Use when Unicode not supported:
- Horizontal: `-`
- Vertical: `|`
- Corners: `+`

### Visual Highlight for Selected Option

**When arrow keys are supported**, the selected option is highlighted using ONE of:
1. **Bold reverse video**: Inverted foreground/background colors
2. **Arrow prefix**: `→` character before option text

**Example with arrow prefix**:
```
┌─────────────────────────────────────────────┐
│  1. Task Management                         │
│→ 2. User & Team Management                  │  ← Selected
│  3. View Tasks                              │
└─────────────────────────────────────────────┘
```

### Terminal Compatibility Fallback

**Detection**: On launch, attempt arrow key detection. If detection fails:
1. Remove arrow key hints from shortcut display
2. Display "Use number keys to navigate" message
3. Rely solely on number-key input (1-5, 0-6)

**Fallback menu display**:
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
│ Use number keys (1-5) to navigate           │
│ Shortcuts: c=Create, l=List, q=Quit         │
│ Select option [1-5]: _                      │
└─────────────────────────────────────────────┘
```

## Main Menu

### Display Contract

**Visual Specification**:
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
│ Shortcuts: c=Create, l=List, q=Quit         │
│ Select option [1-5]: _                      │
└─────────────────────────────────────────────┘
```

**Requirements**:
- FR-000: Display numbered options 1-5
- FR-006: Display keyboard shortcut hints
- FR-002: Support arrow key navigation with visual highlight
- FR-033: Highlight selected option when using arrow keys (bold reverse video or `→` arrow)
- FR-033a: Render borders with Unicode box-drawing characters, fallback to ASCII
- FR-002a: Detect terminal capabilities; fall back to number-key-only if arrow keys unsupported

### Input Contract

| Input Type | Valid Values | Behavior |
|------------|--------------|----------|
| Number keys | `1`, `2`, `3`, `4`, `5` | Navigate to submenu or action |
| Letter shortcuts | `c`, `l`, `q` (case-insensitive) | Quick actions |
| Arrow keys | Up, Down | Move selection highlight (if terminal supports) |
| Enter | Any | Confirm selected option |
| Escape | Any | Return to main menu (from submenu) |

### Output Contract

| Selection | Destination |
|-----------|-------------|
| `1` or `Task` | Task Management submenu |
| `2` or `User` | User Management submenu |
| `3` or `View` | View Tasks (direct to list) |
| `4` or `Resources` | View Resources (direct to list) |
| `5` or `Exit` | Exit application |
| `c` | Go to Create Task prompt directly |
| `l` | Go to View Tasks directly |
| `q` | Exit application (with confirmation) |

### Error Handling

| Input | Output |
|-------|--------|
| Invalid number (e.g., `6`, `0`, `-1`) | `Invalid option. Please enter a number between 1 and 5.` |
| Invalid letter (e.g., `x`) | `Invalid option. Please enter a number between 1 and 5, or use shortcuts (c, l, q).` |
| Empty input (just Enter) | Re-prompt with same menu |

## Task Management Submenu

### Display Contract

```
┌─────────────────────────────────────────────┐
│          TASK MANAGEMENT                    │
├─────────────────────────────────────────────┤
│  1. Create Task                             │
│  2. List Tasks                              │
│  3. Update Task                              │
│  4. Complete Task                            │
│  5. Delete Task                              │
│  0. Back to Main Menu                        │
├─────────────────────────────────────────────┤
│ Select option [0-5]: _                      │
└─────────────────────────────────────────────┘
```

### Input Contract

| Input Type | Valid Values | Behavior |
|------------|--------------|----------|
| Number keys | `0`, `1`, `2`, `3`, `4`, `5` | Execute action or go back |
| Letter shortcuts | `b`, `q` (case-insensitive) | Back to main menu |
| Enter | Any | Confirm selected option |

### Output Contract

| Selection | Action |
|-----------|--------|
| `1` or `Create` | Enter Create Task workflow |
| `2` or `List` | Display all tasks (table view) |
| `3` or `Update` | Enter Update Task workflow |
| `4` or `Complete` | Enter Complete Task workflow |
| `5` or `Delete` | Enter Delete Task workflow |
| `0` or `b` or `q` | Return to Main Menu |

## Create Task Workflow

### Step 1: Title

**Display**:
```
Enter task title (or 'q' to cancel): _
```

**Validation**:
- Required: non-empty after stripping whitespace
- Max length: 200 characters
- On empty: "Title is required. Please enter a title:"
- On too long: "Title too long (max 200 characters). Please try again:"

**Cancel**: `q` returns to Task Management submenu

### Step 2: Description

**Display**:
```
Enter description (optional, press Enter to skip): _
```

**Validation**:
- Optional: empty input allowed
- Max length: 1000 characters
- On too long: "Description too long (max 1000 characters). Please try again:"

### Step 3: Priority

**Display**:
```
Select priority:
  [1] High
  [2] Medium
  [3] Low
Enter choice [1-3] (default: 2): _
```

**Validation**:
- Required: must enter `1`, `2`, or `3`
- Default: Press Enter for Medium (2)
- On invalid: "Invalid choice. Please enter a number between 1 and 3:"

### Step 4: Assignee

**Display** (when users exist):
```
Select assignee:
  [0] Unassigned
  [1] Sarah (2 tasks)
  [2] John (5 tasks)
  [3] Mike (0 tasks)
Enter choice [0-3] (default: 0): _
```

**Workload Warning** (when selected user has 5+ active tasks):
```
Warning: User 'John' has 5 active tasks (high workload). Continue? [Y/n]: _
```

**Validation**:
- Required: must enter valid option number
- Default: Press Enter for Unassigned (0)
- On invalid number: "Invalid choice. Please enter a number between 0 and N:"
- On workload warning (5+ tasks): Display warning, require Y to continue or n to cancel

**Display** (when no users exist):
```
No users available. Task will be created as Unassigned.
Press Enter to continue...
```

**Validation**:
- Required: must enter valid option number
- Default: Press Enter for Unassigned (0)
- On invalid number: "Invalid choice. Please enter a number between 0 and N:"

### Success Output

**Display**:
```
┌─────────────────────────────────────────────┐
│ [SUCCESS] Task created!                      │
│                                             │
│ ID: 1                                        │
│ Title: Fix Navbar                             │
│ Priority: High                                │
│ Status: Todo                                  │
│ Assignee: Sarah                               │
│                                             │
│ Press Enter to continue...                    │
└─────────────────────────────────────────────┘
```

## List Tasks View

### Display Contract

**Table Format**:
```
┌────────────────────────────────────────────────────────────────┐
│  Tasks                                                         │
├──────┬─────────────────┬──────────┬─────────────┬────────────┤
│  ID  │ Title           │ Priority │ Assignee    │ Status     │
├──────┼─────────────────┼──────────┼─────────────┼────────────┤
│   1  │ Fix Navbar       │ High     │ Sarah       │ Todo       │
│   2  │ Update docs      │ Medium   │ Unassigned  │ Done       │
│   3  │ Debug API        │ Low      │ John        │ InProgress │
└──────┴─────────────────┴──────────┴─────────────┴────────────┘

Press Enter to return to menu...
```

**Color Coding** (FR-034 to FR-039):
- High Priority: Red text
- Medium Priority: Yellow text
- Low Priority: Blue text
- Done Status: Green text

### Filter Menu

**Display** (after pressing Enter from list):
```
Filter Tasks:
  [1] Show All Tasks
  [2] By Status
  [3] By Priority
  [4] By Assignee
  [0] Back
Enter choice [0-4]: _
```

## Update Task Workflow

### Step 1: Select Task

**Display**:
```
Enter task ID to update (or '0' to cancel): _
```

**Validation**:
- Required: must enter valid task ID
- On not found: "Task #N not found. Press Enter to continue..."
- On `0`: Return to Task Management submenu

### Step 2: Select Field to Update

**Display**:
```
Update Task #1: Fix Navbar
  [1] Title
  [2] Description
  [3] Priority
  [4] Status
  [5] Assignee
  [0] Cancel
Enter field to update [0-5]: _
```

### Step 3: Enter New Value

**Display** (depends on field):
- Title/Description: Free text prompt
- Priority: Numbered selection [1] High [2] Medium [3] Low
- Status: Numbered selection [1] Todo [2] InProgress [3] Done
- Assignee: Numbered selection [0] Unassigned [1+] Users

### Success Output

```
┌─────────────────────────────────────────────┐
│ [SUCCESS] Task updated!                      │
│                                             │
│ ID: 1                                        │
│ Title: Fix Navbar (updated)                   │
│ Priority: High → Medium                       │
│                                             │
│ Press Enter to continue...                    │
└─────────────────────────────────────────────┘
```

## Complete Task Workflow

### Display Contract

```
Enter task ID to complete (or '0' to cancel): _
```

**Validation**:
- Required: must enter valid task ID
- On not found: "Task #N not found. Press Enter to continue..."
- On `0`: Return to Task Management submenu

### Confirmation

```
Mark task #1 "Fix Navbar" as complete? [Y/n]: _
```

**Success Output** (on Y):
```
┌─────────────────────────────────────────────┐
│ [SUCCESS] Task marked as Done!               │
│                                             │
│ ID: 1                                        │
│ Title: Fix Navbar                             │
│ Status: Todo → Done                           │
│                                             │
│ Press Enter to continue...                    │
└─────────────────────────────────────────────┘
```

## Delete Task Workflow

### Display Contract

```
Enter task ID to delete (or '0' to cancel): _
```

**Validation**:
- Required: must enter valid task ID
- On not found: "Task #N not found. Press Enter to continue..."
- On `0`: Return to Task Management submenu

### Confirmation

```
Delete task #1 "Fix Navbar"? This cannot be undone. [Y/n]: _
```

**Success Output** (on Y):
```
┌─────────────────────────────────────────────┐
│ [SUCCESS] Task deleted!                      │
│                                             │
│ Task #1 has been removed.                    │
│                                             │
│ Press Enter to continue...                    │
└─────────────────────────────────────────────┘
```

## User & Team Management Submenu

### Display Contract

```
┌─────────────────────────────────────────────┐
│       USER & TEAM MANAGEMENT                 │
├─────────────────────────────────────────────┤
│  1. Create User                             │
│  2. Create Team                             │
│  3. List All Users                           │
│  4. List All Teams                           │
│  0. Back to Main Menu                        │
├─────────────────────────────────────────────┤
│ Select option [0-4]: _                      │
└─────────────────────────────────────────────┘
```

### Create User Workflow

**Step 1: Name**
```
Enter user name (or 'q' to cancel): _
```

**Step 2: Role**
```
Select role:
  [1] Admin
  [2] Developer
  [3] Designer
Enter choice [1-3] (default: 2): _
```

**Step 3: Skills**
```
Enter skills (comma-separated, optional): _
Example: Python,FastAPI,SQL
```

### Create Team Workflow

**Step 1: Name**
```
Enter team name (or 'q' to cancel): _
```

**Step 2: Members**
```
Available users:
  [1] Sarah
  [2] John
  [3] Mike

Select members (comma-separated numbers): _
Example: 1,3 to select Sarah and Mike
```

**Validation**:
- At least one member required
- All member numbers must be valid

## Keyboard Shortcuts

### Global Shortcuts

| Key | Action | Availability |
|-----|--------|--------------|
| `c` | Go to Create Task | Main menu only |
| `l` | Go to List Tasks | Main menu only |
| `q` | Exit / Back | Any screen (with confirmation) |
| `Escape` | Back to main menu | Any screen |
| `0` | Back to previous menu | Any submenu |

### Task List Shortcuts

| Key | Action | Availability |
|-----|--------|--------------|
| Task number (e.g., `3`) | View task details | Task list view |
| `f` | Enter filter menu | Task list view |
