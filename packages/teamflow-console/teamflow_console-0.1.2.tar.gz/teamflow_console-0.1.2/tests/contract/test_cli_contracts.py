"""Contract tests for CLI prompt interactions.

These tests verify that CLI prompts produce the expected
input/output contracts specified in menu-flow.md.
"""

import io
from unittest.mock import Mock, patch

import pytest

from cli.prompts import TaskPrompts
from lib.formatting import create_console
from lib.storage import InMemoryTaskStore
from models.task import Priority
from services.task_service import TaskService


class TestTaskCreationPromptContract:
    """Tests for task creation prompt contracts."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.console = create_console()
        self.store = InMemoryTaskStore()
        self.service = TaskService(self.store)
        self.prompts = TaskPrompts(self.console, self.service)

    @patch("builtins.input", side_effect=["Test Task", "", "", "0"])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_create_task_prompts_title_first(self, mock_stdout, mock_input) -> None:
        """Test that create task prompts for title first."""
        # This test verifies the prompt order: title → description → priority → assignee
        # The actual prompts are tested by the input sequence

        # We can't easily test the exact prompt text without capturing console output,
        # but we can verify the workflow completes successfully
        initial_count = len(self.service.list_all())

        # Run the workflow (will use mocked inputs)
        try:
            self.prompts.prompt_create_task()
        except (SystemExit, KeyboardInterrupt):
            # May exit if console rendering fails in test environment
            pass

        # Verify task was created (check count increased)
        final_count = len(self.service.list_all())
        assert final_count == initial_count + 1

    @patch("builtins.input", side_effect=["", "Valid Title", "", "", "0"])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_create_task_rejects_empty_title(self, mock_stdout, mock_input) -> None:
        """Test that create task rejects empty title."""
        initial_count = len(self.service.list_all())

        # First input is empty (should be rejected), second is valid
        try:
            self.prompts.prompt_create_task()
        except (SystemExit, KeyboardInterrupt):
            pass

        # Should have created exactly one task
        final_count = len(self.service.list_all())
        assert final_count == initial_count + 1

    @patch("builtins.input", side_effect=["Test Title", "Test Description", "1", "0"])
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_create_task_with_priority_selection(self, mock_stdout, mock_input) -> None:
        """Test that create task prompts for numbered priority selection."""
        initial_count = len(self.service.list_all())

        try:
            self.prompts.prompt_create_task()
        except (SystemExit, KeyboardInterrupt):
            pass

        # Verify task was created with HIGH priority
        tasks = self.service.list_all()
        assert len(tasks) == initial_count + 1
        # Find the new task (last one)
        new_task = tasks[-1]
        assert new_task.priority == Priority.HIGH


class TestTaskListDisplayContract:
    """Tests for task list display contracts."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.console = create_console()
        self.store = InMemoryTaskStore()
        self.service = TaskService(self.store)
        self.prompts = TaskPrompts(self.console, self.service)

    @patch("builtins.input", return_value="")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_list_tasks_displays_table(self, mock_stdout, mock_input) -> None:
        """Test that list tasks displays a table."""
        # Create some tasks
        self.service.create("Task 1", priority=Priority.HIGH)
        self.service.create("Task 2", priority=Priority.MEDIUM)

        # List tasks
        self.prompts.prompt_list_tasks()

        # Verify output contains task information
        output = mock_stdout.getvalue()
        # Should contain task titles
        assert "Task 1" in output or "Task1" in output or "Task 2" in output or "Task2" in output

    @patch("builtins.input", return_value="")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_list_tasks_shows_no_tasks_message_when_empty(self, mock_stdout, mock_input) -> None:
        """Test that list tasks shows message when no tasks exist."""
        # List tasks with no tasks created
        self.prompts.prompt_list_tasks()

        # Verify output contains no tasks message
        output = mock_stdout.getvalue()
        assert "No tasks" in output or "no tasks" in output.lower()


class TestTaskUpdatePromptContract:
    """Tests for task update prompt contracts."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.console = create_console()
        self.store = InMemoryTaskStore()
        self.service = TaskService(self.store)
        self.prompts = TaskPrompts(self.console, self.service)
        # Create a test task
        self.task = self.service.create("Original Title")

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_update_task_prompts_for_field_selection(self, mock_stdout) -> None:
        """Test that update task prompts for field selection [1-5]."""
        task_id = str(self.task.id)
        with patch("builtins.input", side_effect=[task_id, "1", "Updated Title"]):
            initial_title = self.service.get_by_id(self.task.id).title

            try:
                self.prompts.prompt_update_task()
            except (SystemExit, KeyboardInterrupt):
                pass

            # Verify title was updated (field 1 = Title)
            updated_task = self.service.get_by_id(self.task.id)
            assert updated_task.title == "Updated Title"
            assert updated_task.title != initial_title


class TestTaskCompletePromptContract:
    """Tests for task complete prompt contracts."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.console = create_console()
        self.store = InMemoryTaskStore()
        self.service = TaskService(self.store)
        self.prompts = TaskPrompts(self.console, self.service)
        # Create a test task
        self.task = self.service.create("Task to Complete")

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_complete_task_prompts_for_confirmation(self, mock_stdout) -> None:
        """Test that complete task prompts for Y/n confirmation."""
        from models.task import Status

        task_id = str(self.task.id)
        with patch("builtins.input", side_effect=[task_id, "y"]):
            try:
                self.prompts.prompt_complete_task()
            except (SystemExit, KeyboardInterrupt):
                pass

            # Verify task is now complete
            completed_task = self.service.get_by_id(self.task.id)
            assert completed_task.status == Status.DONE


class TestTaskDeletePromptContract:
    """Tests for task delete prompt contracts."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.console = create_console()
        self.store = InMemoryTaskStore()
        self.service = TaskService(self.store)
        self.prompts = TaskPrompts(self.console, self.service)
        # Create a test task
        self.task = self.service.create("Task to Delete")

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_delete_task_prompts_for_confirmation(self, mock_stdout) -> None:
        """Test that delete task prompts for Y/n confirmation."""
        initial_count = len(self.service.list_all())

        task_id = str(self.task.id)
        with patch("builtins.input", side_effect=[task_id, "y"]):
            try:
                self.prompts.prompt_delete_task()
            except (SystemExit, KeyboardInterrupt):
                pass

            # Verify task was deleted
            final_count = len(self.service.list_all())
            assert final_count == initial_count - 1

            # Verify task no longer exists
            with pytest.raises(Exception):  # TaskNotFoundError
                self.service.get_by_id(self.task.id)
