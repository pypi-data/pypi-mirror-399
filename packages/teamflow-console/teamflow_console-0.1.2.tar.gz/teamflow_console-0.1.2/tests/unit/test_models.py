"""Unit tests for Pydantic models."""

import pytest

from models.task import Priority, Status, Task
from models.team import Team
from models.user import Role, User


class TestTaskModel:
    """Tests for Task Pydantic model."""

    def test_task_with_minimum_fields(self) -> None:
        """Test creating a task with minimum required fields."""
        task = Task(id=1, title="Test Task")
        assert task.id == 1
        assert task.title == "Test Task"
        assert task.priority == Priority.MEDIUM
        assert task.status == Status.TODO
        assert task.description is None
        assert task.assignee_id is None

    def test_task_with_all_fields(self) -> None:
        """Test creating a task with all fields."""
        task = Task(
            id=1,
            title="Test Task",
            description="A description",
            priority=Priority.HIGH,
            status=Status.IN_PROGRESS,
            assignee_id=5,
        )
        assert task.title == "Test Task"
        assert task.description == "A description"
        assert task.priority == Priority.HIGH
        assert task.status == Status.IN_PROGRESS
        assert task.assignee_id == 5

    def test_title_validation_empty_string_raises_error(self) -> None:
        """Test that empty title raises validation error."""
        with pytest.raises(ValueError):
            Task(id=1, title="")

    def test_title_validation_whitespace_only_raises_error(self) -> None:
        """Test that whitespace-only title raises validation error."""
        with pytest.raises(ValueError):
            Task(id=1, title="   ")

    def test_title_validation_strips_whitespace(self) -> None:
        """Test that title whitespace is stripped."""
        task = Task(id=1, title="  Test Task  ")
        assert task.title == "Test Task"

    def test_title_too_long_raises_error(self) -> None:
        """Test that title exceeding max length raises validation error."""
        with pytest.raises(ValueError):
            Task(id=1, title="x" * 201)

    def test_description_max_length(self) -> None:
        """Test that description has max length constraint."""
        # Valid description
        task = Task(id=1, title="Test", description="x" * 1000)
        assert task.description == "x" * 1000

        # Too long
        with pytest.raises(ValueError):
            Task(id=1, title="Test", description="x" * 1001)

    def test_priority_enum_values(self) -> None:
        """Test Priority enum has correct values."""
        assert Priority.HIGH.value == "High"
        assert Priority.MEDIUM.value == "Medium"
        assert Priority.LOW.value == "Low"

    def test_status_enum_values(self) -> None:
        """Test Status enum has correct values."""
        assert Status.TODO.value == "Todo"
        assert Status.IN_PROGRESS.value == "InProgress"
        assert Status.DONE.value == "Done"


class TestUserModel:
    """Tests for User Pydantic model."""

    def test_user_with_minimum_fields(self) -> None:
        """Test creating a user with minimum required fields."""
        user = User(id=1, name="John")
        assert user.id == 1
        assert user.name == "John"
        assert user.role == Role.DEVELOPER
        assert user.skills == []

    def test_user_with_all_fields(self) -> None:
        """Test creating a user with all fields."""
        user = User(
            id=1,
            name="Jane",
            role=Role.ADMIN,
            skills=["Python", "FastAPI"],
        )
        assert user.name == "Jane"
        assert user.role == Role.ADMIN
        assert user.skills == ["Python", "FastAPI"]

    def test_name_validation_empty_string_raises_error(self) -> None:
        """Test that empty name raises validation error."""
        with pytest.raises(ValueError):
            User(id=1, name="")

    def test_name_validation_strips_whitespace(self) -> None:
        """Test that name whitespace is stripped."""
        user = User(id=1, name="  John  ")
        assert user.name == "John"

    def test_skills_deduplication(self) -> None:
        """Test that duplicate skills are removed."""
        user = User(
            id=1,
            name="John",
            skills=["Python", "python", "FastAPI", "FastAPI", "SQL"],
        )
        assert len(user.skills) == 3  # Python, FastAPI, SQL (case-insensitive dedup)
        assert "Python" in user.skills
        assert "FastAPI" in user.skills
        assert "SQL" in user.skills

    def test_skills_whitespace_stripped(self) -> None:
        """Test that skill whitespace is stripped."""
        user = User(id=1, name="John", skills=[" Python ", " FastAPI "])
        assert user.skills == ["Python", "FastAPI"]

    def test_role_enum_values(self) -> None:
        """Test Role enum has correct values."""
        assert Role.ADMIN.value == "Admin"
        assert Role.DEVELOPER.value == "Developer"
        assert Role.DESIGNER.value == "Designer"


class TestTeamModel:
    """Tests for Team Pydantic model."""

    def test_team_with_required_fields(self) -> None:
        """Test creating a team with required fields."""
        team = Team(id=1, name="Frontend Squad", member_names=["John", "Jane"])
        assert team.id == 1
        assert team.name == "Frontend Squad"
        assert team.member_names == ["John", "Jane"]

    def test_member_names_deduplication(self) -> None:
        """Test that duplicate member names are removed."""
        team = Team(
            id=1,
            name="Frontend Squad",
            member_names=["John", "john", "Jane", "Jane"],
        )
        assert len(team.member_names) == 2  # John, Jane (case-insensitive dedup)
        assert "John" in team.member_names
        assert "Jane" in team.member_names

    def test_member_names_whitespace_stripped(self) -> None:
        """Test that member name whitespace is stripped."""
        team = Team(
            id=1,
            name="Frontend Squad",
            member_names=[" John ", " Jane "],
        )
        assert team.member_names == ["John", "Jane"]

    def test_member_names_empty_list_raises_error(self) -> None:
        """Test that empty member_names list raises validation error."""
        with pytest.raises(ValueError):
            Team(id=1, name="Empty Team", member_names=[])

    def test_name_validation_empty_string_raises_error(self) -> None:
        """Test that empty name raises validation error."""
        with pytest.raises(ValueError):
            Team(id=1, name="", member_names=["John"])
