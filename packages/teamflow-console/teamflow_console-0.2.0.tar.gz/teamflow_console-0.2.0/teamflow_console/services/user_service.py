"""User service for TeamFlow Console App.

This module contains the business logic for user operations.
"""

from typing import Protocol

from teamflow_console.models.task import Status
from teamflow_console.models.user import Role, User


class UserStoreProtocol(Protocol):
    """Protocol defining the interface for user storage operations."""

    def save(self, user: User) -> User: ...

    def find_by_id(self, user_id: int) -> User | None: ...

    def find_by_name(self, name: str) -> User | None: ...

    def find_all(self) -> list[User]: ...

    def name_exists(self, name: str) -> bool: ...


class UserNotFoundError(Exception):
    """Raised when a user is not found."""

    def __init__(self, user_id: int | str) -> None:
        self.user_id = user_id
        if isinstance(user_id, int):
            super().__init__(f"User #{user_id} not found")
        else:
            super().__init__(f"User '{user_id}' not found")


class DuplicateUserNameError(Exception):
    """Raised when attempting to create a user with a duplicate name."""

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"User '{name}' already exists")


class UserService:
    """Business logic for user operations."""

    def __init__(self, store: UserStoreProtocol, task_service=None) -> None:
        """Initialize user service with a storage backend.

        Args:
            store: The user storage backend
            task_service: Optional TaskService for active task count
        """
        self._store = store
        self._task_service = task_service

    def create(
        self, name: str, role: Role = Role.DEVELOPER, skills: list[str] | None = None
    ) -> User:
        """Create a new user.

        Args:
            name: User name (must be unique)
            role: User role (default: Developer)
            skills: Optional list of skills

        Returns:
            The created user with generated ID

        Raises:
            DuplicateUserNameError: If user name already exists
        """
        if self._store.name_exists(name):
            raise DuplicateUserNameError(name)

        user = User(
            id=0,  # ID will be assigned by storage
            name=name,
            role=role,
            skills=skills or [],
        )
        return self._store.save(user)

    def get_by_id(self, user_id: int) -> User:
        """Get a user by ID.

        Args:
            user_id: The user ID

        Returns:
            The user

        Raises:
            UserNotFoundError: If user not found
        """
        user = self._store.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(user_id)
        return user

    def get_by_name(self, name: str) -> User:
        """Get a user by name.

        Args:
            name: The user name

        Returns:
            The user

        Raises:
            UserNotFoundError: If user not found
        """
        user = self._store.find_by_name(name)
        if user is None:
            raise UserNotFoundError(name)
        return user

    def list_all(self) -> list[User]:
        """Get all users.

        Returns:
            List of all users
        """
        return self._store.find_all()

    def name_exists(self, name: str) -> bool:
        """Check if a user name already exists.

        Args:
            name: The user name to check

        Returns:
            True if name exists, False otherwise
        """
        return self._store.name_exists(name)

    def get_active_task_count(self, user_id: int) -> int:
        """Get the number of active (non-Done) tasks for a user.

        Args:
            user_id: The user ID

        Returns:
            Number of active tasks
        """
        if self._task_service is None:
            return 0

        # Get all tasks assigned to this user
        user_tasks = self._task_service._store.find_by_assignee(user_id)

        # Count only non-Done tasks
        active_count = sum(1 for task in user_tasks if task.status != Status.DONE)
        return active_count
