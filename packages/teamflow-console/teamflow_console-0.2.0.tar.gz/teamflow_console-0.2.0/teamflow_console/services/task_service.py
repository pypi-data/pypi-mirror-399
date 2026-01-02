"""Task service for TeamFlow Console App.

This module contains the business logic for task operations.
It follows the Single Responsibility Principle by separating
business logic from CLI interface and storage.
"""

from typing import Protocol

from teamflow_console.models.task import Priority, Status, Task

# Sentinel value to detect when assignee_id parameter was not provided
_UNSET = object()


class TaskStoreProtocol(Protocol):
    """Protocol defining the interface for task storage operations."""

    def save(self, task: Task) -> Task: ...

    def find_by_id(self, task_id: int) -> Task | None: ...

    def find_all(self) -> list[Task]: ...

    def find_by_assignee(self, assignee_id: int) -> list[Task]: ...

    def find_by_status(self, status: Status) -> list[Task]: ...

    def find_by_priority(self, priority: Priority) -> list[Task]: ...

    def delete(self, task_id: int) -> bool: ...


class TaskNotFoundError(Exception):
    """Raised when a task is not found."""

    def __init__(self, task_id: int) -> None:
        self.task_id = task_id
        super().__init__(f"Task #{task_id} not found")


class TaskService:
    """Business logic for task operations."""

    def __init__(self, store: TaskStoreProtocol, user_service=None) -> None:
        """Initialize task service with a storage backend.

        Args:
            store: The task storage backend
            user_service: Optional UserService for name lookups
        """
        self._store = store
        self._user_service = user_service

    def create(
        self,
        title: str,
        description: str | None = None,
        priority: Priority = Priority.MEDIUM,
        status: Status = Status.TODO,
        assignee_id: int | None = None,
    ) -> Task:
        """Create a new task.

        Args:
            title: Task title (required)
            description: Optional task description
            priority: Task priority (default: Medium)
            status: Initial status (default: Todo)
            assignee_id: Optional user ID to assign task to

        Returns:
            The created task with generated ID
        """
        task = Task(
            id=0,  # ID will be assigned by storage
            title=title,
            description=description,
            priority=priority,
            status=status,
            assignee_id=assignee_id,
        )
        return self._store.save(task)

    def get_by_id(self, task_id: int) -> Task:
        """Get a task by ID.

        Args:
            task_id: The task ID

        Returns:
            The task

        Raises:
            TaskNotFoundError: If task not found
        """
        task = self._store.find_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def list_all(self) -> list[Task]:
        """Get all tasks.

        Returns:
            List of all tasks
        """
        return self._store.find_all()

    def update_status(self, task_id: int, new_status: Status) -> Task:
        """Update the status of a task.

        Args:
            task_id: The task ID
            new_status: The new status

        Returns:
            The updated task

        Raises:
            TaskNotFoundError: If task not found
        """
        task = self.get_by_id(task_id)
        task_dict = task.model_dump()
        task_dict["status"] = new_status
        updated = Task(**task_dict)
        return self._store.save(updated)

    def update(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
        priority: Priority | None = None,
        status: Status | None = None,
        assignee_id: int | None | object = _UNSET,
    ) -> Task:
        """Update task fields.

        Args:
            task_id: The task ID
            title: New title (optional)
            description: New description (optional)
            priority: New priority (optional)
            status: New status (optional)
            assignee_id: New assignee (optional), use _UNSET sentinel to omit

        Returns:
            The updated task

        Raises:
            TaskNotFoundError: If task not found
        """
        task = self.get_by_id(task_id)
        task_dict = task.model_dump()

        if title is not None:
            task_dict["title"] = title
        if description is not None:
            task_dict["description"] = description
        if priority is not None:
            task_dict["priority"] = priority
        if status is not None:
            task_dict["status"] = status
        # Check if assignee_id was explicitly passed (including None)
        # Use module-level sentinel for comparison
        if assignee_id is not _UNSET:
            task_dict["assignee_id"] = assignee_id

        updated = Task(**task_dict)
        return self._store.save(updated)

    def delete(self, task_id: int) -> None:
        """Delete a task.

        Args:
            task_id: The task ID

        Raises:
            TaskNotFoundError: If task not found
        """
        if not self._store.delete(task_id):
            raise TaskNotFoundError(task_id)

    def assign(self, task_id: int, assignee_id: int | None) -> Task:
        """Assign or reassign a task to a user.

        Args:
            task_id: The task ID
            assignee_id: The user ID, or None to unassign

        Returns:
            The updated task

        Raises:
            TaskNotFoundError: If task not found
        """
        return self.update(task_id, assignee_id=assignee_id)

    def get_assignee_name(self, task_id: int) -> str:
        """Get the name of the user assigned to a task.

        Args:
            task_id: The task ID

        Returns:
            The assignee name, or "Unassigned" if not assigned

        Raises:
            TaskNotFoundError: If task not found
        """
        task = self.get_by_id(task_id)
        if task.assignee_id is None:
            return "Unassigned"

        if self._user_service is not None:
            try:
                user = self._user_service.get_by_id(task.assignee_id)
                return user.name
            except Exception:
                # User not found, return ID
                return f"User #{task.assignee_id}"

        return f"User #{task.assignee_id}"

    def filter_by_status(self, status: Status) -> list[Task]:
        """Get all tasks with a specific status.

        Args:
            status: The status to filter by

        Returns:
            List of tasks with the specified status
        """
        return self._store.find_by_status(status)

    def filter_by_priority(self, priority: Priority) -> list[Task]:
        """Get all tasks with a specific priority.

        Args:
            priority: The priority to filter by

        Returns:
            List of tasks with the specified priority
        """
        return self._store.find_by_priority(priority)

    def filter_by_assignee(self, assignee_id: int | None) -> list[Task]:
        """Get all tasks assigned to a user (or unassigned).

        Args:
            assignee_id: The user ID, or None for unassigned tasks

        Returns:
            List of tasks matching the assignee filter
        """
        if assignee_id is None:
            return [t for t in self.list_all() if t.assignee_id is None]
        return self._store.find_by_assignee(assignee_id)
