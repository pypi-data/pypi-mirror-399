"""In-memory storage implementation for TeamFlow Console App.

This module provides singleton storage classes for tasks, users, and teams.
All data is stored in memory and is lost when the application exits.
"""

from typing import Protocol


class TaskStoreProtocol(Protocol):
    """Protocol defining the interface for task storage operations."""

    def save(self, task: "Task") -> "Task":
        """Save a task (create or update). Returns the saved task with ID assigned."""
        ...

    def find_by_id(self, task_id: int) -> "Task | None":
        """Find a task by ID. Returns None if not found."""
        ...

    def find_all(self) -> list["Task"]:
        """Get all tasks."""
        ...

    def find_by_assignee(self, assignee_id: int) -> list["Task"]:
        """Find all tasks assigned to a user."""
        ...

    def find_by_status(self, status: "Status") -> list["Task"]:
        """Find all tasks with a specific status."""
        ...

    def find_by_priority(self, priority: "Priority") -> list["Task"]:
        """Find all tasks with a specific priority."""
        ...

    def delete(self, task_id: int) -> bool:
        """Delete a task by ID. Returns True if deleted, False if not found."""
        ...


class UserStoreProtocol(Protocol):
    """Protocol defining the interface for user storage operations."""

    def save(self, user: "User") -> "User":
        """Save a user (create or update). Returns the saved user with ID assigned."""
        ...

    def find_by_id(self, user_id: int) -> "User | None":
        """Find a user by ID. Returns None if not found."""
        ...

    def find_by_name(self, name: str) -> "User | None":
        """Find a user by name. Returns None if not found."""
        ...

    def find_all(self) -> list["User"]:
        """Get all users."""
        ...

    def name_exists(self, name: str) -> bool:
        """Check if a user name already exists."""
        ...


class TeamStoreProtocol(Protocol):
    """Protocol defining the interface for team storage operations."""

    def save(self, team: "Team") -> "Team":
        """Save a team (create or update). Returns the saved team with ID assigned."""
        ...

    def find_by_id(self, team_id: int) -> "Team | None":
        """Find a team by ID. Returns None if not found."""
        ...

    def find_all(self) -> list["Team"]:
        """Get all teams."""
        ...

    def name_exists(self, name: str) -> bool:
        """Check if a team name already exists."""
        ...


class InMemoryTaskStore:
    """In-memory storage for tasks."""

    def __init__(self) -> None:
        """Initialize empty task storage."""
        self._tasks: dict[int, "Task"] = {}
        self._next_id: int = 1

    def save(self, task: "Task") -> "Task":
        """Save a task (create or update). Returns the saved task with ID assigned."""
        # Import Task here to avoid circular imports
        from models.task import Task

        if task.id == 0:
            # Create new task - generate ID
            task_dict = task.model_dump()
            task_dict["id"] = self._next_id
            task = Task(**task_dict)
            self._next_id += 1

        self._tasks[task.id] = task
        return task

    def find_by_id(self, task_id: int) -> "Task | None":
        """Find a task by ID. Returns None if not found."""
        return self._tasks.get(task_id)

    def find_all(self) -> list["Task"]:
        """Get all tasks."""
        return list(self._tasks.values())

    def find_by_assignee(self, assignee_id: int) -> list["Task"]:
        """Find all tasks assigned to a user."""
        return [t for t in self._tasks.values() if t.assignee_id == assignee_id]

    def find_by_status(self, status: "Status") -> list["Task"]:
        """Find all tasks with a specific status."""
        return [t for t in self._tasks.values() if t.status == status]

    def find_by_priority(self, priority: "Priority") -> list["Task"]:
        """Find all tasks with a specific priority."""
        return [t for t in self._tasks.values() if t.priority == priority]

    def delete(self, task_id: int) -> bool:
        """Delete a task by ID. Returns True if deleted, False if not found."""
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False


class InMemoryUserStore:
    """In-memory storage for users."""

    def __init__(self) -> None:
        """Initialize empty user storage."""
        self._users: dict[int, "User"] = {}
        self._name_index: dict[str, int] = {}  # Lowercase name -> ID mapping
        self._next_id: int = 1

    def save(self, user: "User") -> "User":
        """Save a user (create or update). Returns the saved user with ID assigned."""
        # Import User here to avoid circular imports
        from models.user import User

        if user.id == 0:
            # Create new user - generate ID
            user_dict = user.model_dump()
            user_dict["id"] = self._next_id
            user = User(**user_dict)
            self._next_id += 1

        self._users[user.id] = user
        self._name_index[user.name.lower()] = user.id
        return user

    def find_by_id(self, user_id: int) -> "User | None":
        """Find a user by ID. Returns None if not found."""
        return self._users.get(user_id)

    def find_by_name(self, name: str) -> "User | None":
        """Find a user by name. Returns None if not found."""
        user_id = self._name_index.get(name.lower())
        if user_id is None:
            return None
        return self._users.get(user_id)

    def find_all(self) -> list["User"]:
        """Get all users."""
        return list(self._users.values())

    def name_exists(self, name: str) -> bool:
        """Check if a user name already exists."""
        return name.lower() in self._name_index


class InMemoryTeamStore:
    """In-memory storage for teams."""

    def __init__(self) -> None:
        """Initialize empty team storage."""
        self._teams: dict[int, "Team"] = {}
        self._name_index: dict[str, int] = {}  # Lowercase name -> ID mapping
        self._next_id: int = 1

    def save(self, team: "Team") -> "Team":
        """Save a team (create or update). Returns the saved team with ID assigned."""
        # Import Team here to avoid circular imports
        from models.team import Team

        if team.id == 0:
            # Create new team - generate ID
            team_dict = team.model_dump()
            team_dict["id"] = self._next_id
            team = Team(**team_dict)
            self._next_id += 1

        self._teams[team.id] = team
        self._name_index[team.name.lower()] = team.id
        return team

    def find_by_id(self, team_id: int) -> "Team | None":
        """Find a team by ID. Returns None if not found."""
        return self._teams.get(team_id)

    def find_all(self) -> list["Team"]:
        """Get all teams."""
        return list(self._teams.values())

    def name_exists(self, name: str) -> bool:
        """Check if a team name already exists."""
        return name.lower() in self._name_index


# Global singleton instances
_task_store: InMemoryTaskStore | None = None
_user_store: InMemoryUserStore | None = None
_team_store: InMemoryTeamStore | None = None


def get_task_store() -> InMemoryTaskStore:
    """Get the global task store singleton."""
    global _task_store
    if _task_store is None:
        _task_store = InMemoryTaskStore()
    return _task_store


def get_user_store() -> InMemoryUserStore:
    """Get the global user store singleton."""
    global _user_store
    if _user_store is None:
        _user_store = InMemoryUserStore()
    return _user_store


def get_team_store() -> InMemoryTeamStore:
    """Get the global team store singleton."""
    global _team_store
    if _team_store is None:
        _team_store = InMemoryTeamStore()
    return _team_store


def reset_storage() -> None:
    """Reset all storage to initial empty state. Useful for testing."""
    global _task_store, _user_store, _team_store
    _task_store = None
    _user_store = None
    _team_store = None
