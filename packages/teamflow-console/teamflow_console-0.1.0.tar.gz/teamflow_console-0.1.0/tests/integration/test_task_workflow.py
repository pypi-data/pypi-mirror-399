"""Integration tests for task workflow.

This module tests end-to-end workflows for task management:
Create→List→Update→Complete→Delete
"""

import pytest

from lib.storage import InMemoryTaskStore
from models.task import Priority, Status
from services.task_service import TaskNotFoundError, TaskService


class TestTaskNumberSelection:
    """Integration tests for task number selection (US5 - FR-032)."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.store = InMemoryTaskStore()
        self.service = TaskService(self.store)

    def test_task_number_selection_retrieves_correct_task(self) -> None:
        """Test that pressing a number in task list retrieves the correct task (FR-032)."""
        # Create multiple tasks
        task1 = self.service.create("First Task", priority=Priority.HIGH)
        task2 = self.service.create("Second Task", priority=Priority.MEDIUM)
        task3 = self.service.create("Third Task", priority=Priority.LOW)

        # List all tasks
        tasks = self.service.list_all()
        assert len(tasks) == 3

        # Simulate pressing number 2 (1-indexed, so index 1)
        selected_task = tasks[1]  # Should be task2
        assert selected_task.id == task2.id
        assert selected_task.title == "Second Task"

    def test_task_number_selection_with_more_than_nine_tasks(self) -> None:
        """Test that only first 9 tasks are selectable by number (FR-032)."""
        # Create 12 tasks
        for i in range(12):
            self.service.create(f"Task {i+1}")

        tasks = self.service.list_all()
        assert len(tasks) == 12

        # Only first 9 should be directly accessible by number
        # This is enforced by UI limiting, but we verify the data structure
        selectable = tasks[:9]
        assert len(selectable) == 9
        assert selectable[0].title == "Task 1"
        assert selectable[8].title == "Task 9"

    def test_task_number_selection_with_filtered_list(self) -> None:
        """Test task number selection works correctly with filtered views (FR-032)."""
        # Create tasks with different statuses
        todo1 = self.service.create("Todo 1", status=Status.TODO)
        todo2 = self.service.create("Todo 2", status=Status.TODO)
        in_progress = self.service.create("In Progress 1", status=Status.IN_PROGRESS)
        done = self.service.create("Done 1", status=Status.DONE)

        # Filter to only TODO tasks
        todo_tasks = self.service.filter_by_status(Status.TODO)
        assert len(todo_tasks) == 2

        # Pressing 1 should select the first TODO task
        selected = todo_tasks[0]
        assert selected.id == todo1.id
        assert selected.title == "Todo 1"


class TestTaskWorkflow:
    """Tests for complete task workflow integration."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.store = InMemoryTaskStore()
        self.service = TaskService(self.store)

    def test_create_list_update_complete_delete_workflow(self) -> None:
        """Test complete task lifecycle: Create→List→Update→Complete→Delete."""
        # Step 1: Create a task
        task = self.service.create(
            title="Fix Navbar Bug",
            description="Navbar doesn't collapse on mobile",
            priority=Priority.HIGH,
        )
        assert task.id == 1
        assert task.title == "Fix Navbar Bug"
        assert task.status == Status.TODO
        assert task.priority == Priority.HIGH

        # Step 2: List tasks (verify it appears)
        tasks = self.service.list_all()
        assert len(tasks) == 1
        assert tasks[0].id == 1
        assert tasks[0].title == "Fix Navbar Bug"

        # Step 3: Update task
        updated = self.service.update(
            task.id,
            title="Fix Navbar Mobile Collapse",
            priority=Priority.MEDIUM,
        )
        assert updated.title == "Fix Navbar Mobile Collapse"
        assert updated.priority == Priority.MEDIUM
        assert updated.status == Status.TODO  # Status unchanged

        # Step 4: Complete task
        completed = self.service.update_status(task.id, Status.DONE)
        assert completed.status == Status.DONE

        # Step 5: Delete task
        self.service.delete(task.id)
        tasks = self.service.list_all()
        assert len(tasks) == 0

    def test_create_multiple_tasks_and_list(self) -> None:
        """Test creating multiple tasks and listing them all."""
        # Create multiple tasks
        self.service.create("Task 1", priority=Priority.HIGH)
        self.service.create("Task 2", priority=Priority.MEDIUM)
        self.service.create("Task 3", priority=Priority.LOW)

        # List all tasks
        tasks = self.service.list_all()
        assert len(tasks) == 3

        titles = [t.title for t in tasks]
        assert "Task 1" in titles
        assert "Task 2" in titles
        assert "Task 3" in titles

    def test_update_task_status_through_workflow(self) -> None:
        """Test status transitions: Todo→InProgress→Done."""
        task = self.service.create("Test Task")

        # Todo → InProgress
        in_progress = self.service.update_status(task.id, Status.IN_PROGRESS)
        assert in_progress.status == Status.IN_PROGRESS

        # InProgress → Done
        done = self.service.update_status(task.id, Status.DONE)
        assert done.status == Status.DONE

    def test_filtering_after_creating_multiple_tasks(self) -> None:
        """Test filtering tasks by status and priority after creating multiple."""
        # Create tasks with various statuses and priorities
        self.service.create("High Priority Todo", priority=Priority.HIGH, status=Status.TODO)
        self.service.create("Medium Priority Todo", priority=Priority.MEDIUM, status=Status.TODO)
        self.service.create(
            "High Priority InProgress", priority=Priority.HIGH, status=Status.IN_PROGRESS
        )
        self.service.create("Low Priority Done", priority=Priority.LOW, status=Status.DONE)

        # Filter by status
        todo_tasks = self.service.filter_by_status(Status.TODO)
        assert len(todo_tasks) == 2

        in_progress_tasks = self.service.filter_by_status(Status.IN_PROGRESS)
        assert len(in_progress_tasks) == 1

        done_tasks = self.service.filter_by_status(Status.DONE)
        assert len(done_tasks) == 1

        # Filter by priority
        high_tasks = self.service.filter_by_priority(Priority.HIGH)
        assert len(high_tasks) == 2

        medium_tasks = self.service.filter_by_priority(Priority.MEDIUM)
        assert len(medium_tasks) == 1

        low_tasks = self.service.filter_by_priority(Priority.LOW)
        assert len(low_tasks) == 1

    def test_assign_and_filter_by_assignee(self) -> None:
        """Test assigning tasks to users and filtering by assignee."""
        # Create tasks
        task1 = self.service.create("Task for User 1", assignee_id=1)
        task2 = self.service.create("Task for User 2", assignee_id=2)
        task3 = self.service.create("Unassigned Task")

        # Filter by assignee
        user1_tasks = self.service.filter_by_assignee(1)
        assert len(user1_tasks) == 1
        assert user1_tasks[0].id == task1.id

        user2_tasks = self.service.filter_by_assignee(2)
        assert len(user2_tasks) == 1
        assert user2_tasks[0].id == task2.id

        unassigned_tasks = self.service.filter_by_assignee(None)
        assert len(unassigned_tasks) == 1
        assert unassigned_tasks[0].id == task3.id

    def test_update_assignee_workflow(self) -> None:
        """Test updating task assignee through workflow."""
        # Create unassigned task
        task = self.service.create("Unassigned Task")
        assert task.assignee_id is None

        # Assign to user 1
        assigned = self.service.assign(task.id, assignee_id=1)
        assert assigned.assignee_id == 1

        # Reassign to user 2
        reassigned = self.service.assign(task.id, assignee_id=2)
        assert reassigned.assignee_id == 2

        # Unassign
        unassigned = self.service.assign(task.id, assignee_id=None)
        assert unassigned.assignee_id is None


class TestTaskWorkflowErrorScenarios:
    """Tests for error scenarios in task workflow."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.store = InMemoryTaskStore()
        self.service = TaskService(self.store)

    def test_update_nonexistent_task_raises_error(self) -> None:
        """Test updating a non-existent task raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError):
            self.service.update(999, title="New Title")

    def test_delete_nonexistent_task_raises_error(self) -> None:
        """Test deleting a non-existent task raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError):
            self.service.delete(999)

    def test_complete_nonexistent_task_raises_error(self) -> None:
        """Test completing a non-existent task raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError):
            self.service.update_status(999, Status.DONE)

    def test_get_nonexistent_task_raises_error(self) -> None:
        """Test getting a non-existent task raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError):
            self.service.get_by_id(999)

    def test_assign_nonexistent_task_raises_error(self) -> None:
        """Test assigning a non-existent task raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError):
            self.service.assign(999, assignee_id=1)
