# Data Model: TeamFlow Console App (Phase 1)

**Feature**: 001-console-task-distribution
**Date**: 2025-01-15
**Storage**: In-memory (Python dictionaries/lists)

## Overview

Phase 1 uses in-memory storage with three core entities: Task, User, and Team. All entities are implemented as Pydantic models for runtime validation and type safety.

## Entities

### Task

Represents a work item in the task distribution system.

**Attributes**:

| Name | Type | Required | Validation | Notes |
|------|------|----------|------------|-------|
| `id` | `int` | Yes | Auto-generated | Sequential, starts at 1 |
| `title` | `str` | Yes | 1-200 chars, non-empty | Display name |
| `description` | `str` | No | Max 1000 chars | Optional details |
| `priority` | `Priority` | Yes | Enum: High/Medium/Low | Default: Medium |
| `status` | `Status` | Yes | Enum: Todo/InProgress/Done | Default: Todo |
| `assignee_id` | `int \| None` | No | Must exist in User store | Null = Unassigned |
| `created_at` | `datetime` | Yes | Auto-generated | UTC timestamp |

**Enums**:
```python
class Priority(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class Status(str, Enum):
    TODO = "Todo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"
```

**State Transitions**:
- Status: `Todo` ⇄ `InProgress` ⇄ `Done` (bidirectional)
- Priority: Can change at any time
- Assignment: Can change at any time (including to/from None)

**Pydantic Model**:
```python
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from enum import Enum

class Priority(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class Status(str, Enum):
    TODO = "Todo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"

class Task(BaseModel):
    id: int = Field(..., description="Unique task identifier")
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Priority = Field(default=Priority.MEDIUM)
    status: Status = Field(default=Status.TODO)
    assignee_id: Optional[int] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()
```

### User

Represents a team member who can be assigned tasks.

**Attributes**:

| Name | Type | Required | Validation | Notes |
|------|------|----------|------------|-------|
| `id` | `int` | Yes | Auto-generated | Sequential, starts at 1 |
| `name` | `str` | Yes | 1-100 chars, unique | Display name |
| `role` | `Role` | Yes | Enum: Admin/Developer/Designer | User's role |
| `skills` | `list[str]` | No | List of skill names | Comma-separated input |

**Enums**:
```python
class Role(str, Enum):
    ADMIN = "Admin"
    DEVELOPER = "Developer"
    DESIGNER = "Designer"
```

**Uniqueness Constraint**:
- `name` must be unique across all users
- Case-sensitive (e.g., "John" ≠ "john")

**Pydantic Model**:
```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List

class Role(str, Enum):
    ADMIN = "Admin"
    DEVELOPER = "Developer"
    DESIGNER = "Designer"

class User(BaseModel):
    id: int = Field(..., description="Unique user identifier")
    name: str = Field(..., min_length=1, max_length=100)
    role: Role = Field(default=Role.DEVELOPER)
    skills: List[str] = Field(default_factory=list)

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()

    @field_validator('skills')
    @classmethod
    def skills_must_be_unique(cls, v: List[str]) -> List[str]:
        # Remove duplicates while preserving order
        seen = set()
        result = []
        for skill in v:
            skill_lower = skill.lower().strip()
            if skill_lower and skill_lower not in seen:
                seen.add(skill_lower)
                result.append(skill.strip())
        return result
```

### Team

Represents a group of users.

**Attributes**:

| Name | Type | Required | Validation | Notes |
|------|------|----------|------------|-------|
| `id` | `int` | Yes | Auto-generated | Sequential, starts at 1 |
| `name` | `str` | Yes | 1-100 chars, unique | Team name |
| `member_names` | `list[str]` | Yes | Non-empty list | Names must exist in User store |

**Uniqueness Constraint**:
- `name` must be unique across all teams
- Case-sensitive (e.g., "Frontend" ≠ "frontend")

**Referential Integrity**:
- All `member_names` must reference existing User `name` values

**Pydantic Model**:
```python
from pydantic import BaseModel, Field, field_validator
from typing import List

class Team(BaseModel):
    id: int = Field(..., description="Unique team identifier")
    name: str = Field(..., min_length=1, max_length=100)
    member_names: List[str] = Field(..., min_length=1)

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()

    @field_validator('member_names')
    @classmethod
    def member_names_must_be_unique(cls, v: List[str]) -> List[str]:
        # Remove duplicates while preserving order
        seen = set()
        result = []
        for name in v:
            name_clean = name.strip()
            if name_clean and name_clean not in seen:
                seen.add(name_clean)
                result.append(name_clean)
        return result
```

## Relationships

### Task → User (Many-to-One, Optional)

- A Task can be assigned to at most one User
- A User can have multiple Tasks assigned
- Represented by `Task.assignee_id` pointing to `User.id`
- Null `assignee_id` means "Unassigned"

### Team → Users (One-to-Many)

- A Team contains multiple Users
- A User can belong to multiple Teams
- Represented by `Team.member_names` containing `User.name` values
- No foreign key constraint (enforced by service layer)

## Storage Interface

### InMemoryTaskStore

```python
class TaskStoreProtocol(Protocol):
    def save(self, task: Task) -> Task: ...
    def find_by_id(self, task_id: int) -> Task | None: ...
    def find_all(self) -> list[Task]: ...
    def find_by_assignee(self, assignee_id: int) -> list[Task]: ...
    def find_by_status(self, status: Status) -> list[Task]: ...
    def find_by_priority(self, priority: Priority) -> list[Task]: ...
    def delete(self, task_id: int) -> bool: ...

class InMemoryTaskStore:
    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def save(self, task: Task) -> Task:
        if task.id == 0:
            task.id = self._next_id
            self._next_id += 1
        self._tasks[task.id] = task
        return task

    # ... other methods
```

### InMemoryUserStore

```python
class UserStoreProtocol(Protocol):
    def save(self, user: User) -> User: ...
    def find_by_id(self, user_id: int) -> User | None: ...
    def find_by_name(self, name: str) -> User | None: ...
    def find_all(self) -> list[User]: ...
    def name_exists(self, name: str) -> bool: ...

class InMemoryUserStore:
    def __init__(self) -> None:
        self._users: dict[int, User] = {}
        self._name_index: dict[str, int] = {}  # name -> id mapping
        self._next_id: int = 1

    def save(self, user: User) -> User:
        if user.id == 0:
            user.id = self._next_id
            self._next_id += 1
        self._users[user.id] = user
        self._name_index[user.name.lower()] = user.id
        return user

    # ... other methods
```

### InMemoryTeamStore

```python
class TeamStoreProtocol(Protocol):
    def save(self, team: Team) -> Team: ...
    def find_by_id(self, team_id: int) -> Team | None: ...
    def find_all(self) -> list[Team]: ...
    def name_exists(self, name: str) -> bool: ...

class InMemoryTeamStore:
    def __init__(self) -> None:
        self._teams: dict[int, Team] = {}
        self._name_index: dict[str, int] = {}  # name -> id mapping
        self._next_id: int = 1

    def save(self, team: Team) -> Team:
        if team.id == 0:
            team.id = self._next_id
            self._next_id += 1
        self._teams[team.id] = team
        self._name_index[team.name.lower()] = team.id
        return team

    # ... other methods
```

## Validation Rules

### Task Validation

| Rule | Error Message |
|------|---------------|
| Title required | "Title is required" |
| Title max 200 chars | "Title too long (max 200 characters)" |
| Priority enum | "Priority must be one of: High, Medium, Low" |
| Status enum | "Status must be one of: Todo, InProgress, Done" |
| Assignee exists | "User '{name}' not found" |

### User Validation

| Rule | Error Message |
|------|---------------|
| Name required | "Name is required" |
| Name max 100 chars | "Name too long (max 100 characters)" |
| Name unique | "User '{name}' already exists" |
| Role enum | "Role must be one of: Admin, Developer, Designer" |

### Team Validation

| Rule | Error Message |
|------|---------------|
| Name required | "Name is required" |
| Name max 100 chars | "Name too long (max 100 characters)" |
| Name unique | "Team '{name}' already exists" |
| At least one member | "Team must have at least one member" |
| Members exist | "User '{name}' not found" |

## Indexes

For in-memory performance, the following indexes are maintained:

| Store | Index | Purpose |
|-------|-------|---------|
| TaskStore | `_tasks: dict[int, Task]` | O(1) lookup by ID |
| TaskStore | (computed on query) | Filter by assignee/status/priority |
| UserStore | `_name_index: dict[str, int]` | O(1) lookup by name |
| TeamStore | `_name_index: dict[str, int]` | O(1) lookup by name |

## Data Volume Limits

Per Phase I scope:

| Entity | Max Count | Rationale |
|--------|-----------|-----------|
| Tasks | 1,000 | Per SC-005 (performance target) |
| Users | 100 | Agency of 10-50 people with some margin |
| Teams | 20 | ~2-5 teams per agency |
| Skills per User | 10 | Reasonable limit for individual skills |

## Serialization

All models support JSON serialization via Pydantic:

```python
task = Task(id=1, title="Fix bug", priority=Priority.HIGH)
json_str = task.model_dump_json()
# {"id":1,"title":"Fix bug","priority":"High","status":"Todo",...}

# Deserialize
task2 = Task.model_validate_json(json_str)
```

This enables:
- Future persistence (Phase II database export)
- API responses (Phase II REST API)
- Testing fixtures
