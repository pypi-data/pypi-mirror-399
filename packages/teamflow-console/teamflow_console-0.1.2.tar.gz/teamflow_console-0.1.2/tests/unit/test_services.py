"""Unit tests for TaskService."""

import pytest

from lib.storage import InMemoryTaskStore
from models.task import Priority, Status, Task
from services.task_service import TaskNotFoundError, TaskService


class TestTaskService:
    """Tests for TaskService business logic."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.store = InMemoryTaskStore()
        self.service = TaskService(self.store)

    def test_create_task_generates_id(self) -> None:
        """Test that creating a task generates an ID."""
        task = self.service.create("Test Task", priority=Priority.HIGH)
        assert task.id == 1
        assert task.title == "Test Task"
        assert task.priority == Priority.HIGH
        assert task.status == Status.TODO

    def test_create_task_with_defaults(self) -> None:
        """Test creating a task with default values."""
        task = self.service.create("Default Task")
        assert task.priority == Priority.MEDIUM
        assert task.status == Status.TODO
        assert task.assignee_id is None

    def test_create_task_with_all_fields(self) -> None:
        """Test creating a task with all fields specified."""
        task = self.service.create(
            title="Full Task",
            description="A description",
            priority=Priority.HIGH,
            status=Status.IN_PROGRESS,
            assignee_id=5,
        )
        assert task.title == "Full Task"
        assert task.description == "A description"
        assert task.priority == Priority.HIGH
        assert task.status == Status.IN_PROGRESS
        assert task.assignee_id == 5

    def test_get_by_id_returns_task(self) -> None:
        """Test getting a task by ID."""
        created = self.service.create("Test Task")
        fetched = self.service.get_by_id(created.id)
        assert fetched.id == created.id
        assert fetched.title == "Test Task"

    def test_get_by_id_raises_error_when_not_found(self) -> None:
        """Test that get_by_id raises TaskNotFoundError when task not found."""
        with pytest.raises(TaskNotFoundError):
            self.service.get_by_id(999)

    def test_list_all_returns_all_tasks(self) -> None:
        """Test listing all tasks."""
        self.service.create("Task 1")
        self.service.create("Task 2")
        self.service.create("Task 3")

        tasks = self.service.list_all()
        assert len(tasks) == 3
        titles = [t.title for t in tasks]
        assert "Task 1" in titles
        assert "Task 2" in titles
        assert "Task 3" in titles

    def test_update_status_changes_status(self) -> None:
        """Test updating task status."""
        task = self.service.create("Test Task")
        assert task.status == Status.TODO

        updated = self.service.update_status(task.id, Status.IN_PROGRESS)
        assert updated.status == Status.IN_PROGRESS

        updated = self.service.update_status(task.id, Status.DONE)
        assert updated.status == Status.DONE

    def test_update_task_fields(self) -> None:
        """Test updating individual task fields."""
        task = self.service.create("Original Title")

        # Update title
        updated = self.service.update(task.id, title="Updated Title")
        assert updated.title == "Updated Title"

        # Update priority
        updated = self.service.update(task.id, priority=Priority.HIGH)
        assert updated.priority == Priority.HIGH

        # Update multiple fields
        updated = self.service.update(
            task.id,
            title="New Title",
            description="New Description",
            priority=Priority.LOW,
        )
        assert updated.title == "New Title"
        assert updated.description == "New Description"
        assert updated.priority == Priority.LOW

    def test_delete_task_removes_task(self) -> None:
        """Test deleting a task."""
        task = self.service.create("Test Task")
        assert len(self.service.list_all()) == 1

        self.service.delete(task.id)
        assert len(self.service.list_all()) == 0

    def test_delete_raises_error_when_not_found(self) -> None:
        """Test that delete raises TaskNotFoundError when task not found."""
        with pytest.raises(TaskNotFoundError):
            self.service.delete(999)

    def test_assign_task_to_user(self) -> None:
        """Test assigning a task to a user."""
        task = self.service.create("Test Task")
        assert task.assignee_id is None

        updated = self.service.assign(task.id, assignee_id=5)
        assert updated.assignee_id == 5

    def test_unassign_task(self) -> None:
        """Test unassigning a task."""
        task = self.service.create("Test Task", assignee_id=5)

        updated = self.service.assign(task.id, assignee_id=None)
        assert updated.assignee_id is None

    def test_filter_by_status(self) -> None:
        """Test filtering tasks by status."""
        self.service.create("Task 1", status=Status.TODO)
        self.service.create("Task 2", status=Status.IN_PROGRESS)
        self.service.create("Task 3", status=Status.TODO)

        todo_tasks = self.service.filter_by_status(Status.TODO)
        assert len(todo_tasks) == 2

        in_progress = self.service.filter_by_status(Status.IN_PROGRESS)
        assert len(in_progress) == 1

    def test_filter_by_priority(self) -> None:
        """Test filtering tasks by priority."""
        self.service.create("Task 1", priority=Priority.HIGH)
        self.service.create("Task 2", priority=Priority.MEDIUM)
        self.service.create("Task 3", priority=Priority.HIGH)

        high_tasks = self.service.filter_by_priority(Priority.HIGH)
        assert len(high_tasks) == 2

        medium_tasks = self.service.filter_by_priority(Priority.MEDIUM)
        assert len(medium_tasks) == 1

    def test_filter_by_assignee(self) -> None:
        """Test filtering tasks by assignee."""
        self.service.create("Task 1", assignee_id=1)
        self.service.create("Task 2", assignee_id=2)
        self.service.create("Task 3")  # Unassigned

        user1_tasks = self.service.filter_by_assignee(1)
        assert len(user1_tasks) == 1

        unassigned = self.service.filter_by_assignee(None)
        assert len(unassigned) == 1
