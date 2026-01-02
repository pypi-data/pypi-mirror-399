"""Team service for TeamFlow Console App.

This module contains the business logic for team operations.
"""

from typing import Protocol

from ..models.team import Team


class TeamStoreProtocol(Protocol):
    """Protocol defining the interface for team storage operations."""

    def save(self, team: Team) -> Team: ...

    def find_by_id(self, team_id: int) -> Team | None: ...

    def find_all(self) -> list[Team]: ...

    def name_exists(self, name: str) -> bool: ...


class TeamNotFoundError(Exception):
    """Raised when a team is not found."""

    def __init__(self, team_id: int | str) -> None:
        self.team_id = team_id
        if isinstance(team_id, int):
            super().__init__(f"Team #{team_id} not found")
        else:
            super().__init__(f"Team '{team_id}' not found")


class DuplicateTeamNameError(Exception):
    """Raised when attempting to create a team with a duplicate name."""

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"Team '{name}' already exists")


class TeamService:
    """Business logic for team operations."""

    def __init__(self, store: TeamStoreProtocol) -> None:
        """Initialize team service with a storage backend."""
        self._store = store

    def create(self, name: str, member_names: list[str]) -> Team:
        """Create a new team.

        Args:
            name: Team name (must be unique)
            member_names: List of user names to be members

        Returns:
            The created team with generated ID

        Raises:
            DuplicateTeamNameError: If team name already exists
        """
        if self._store.name_exists(name):
            raise DuplicateTeamNameError(name)

        team = Team(
            id=0,  # ID will be assigned by storage
            name=name,
            member_names=member_names,
        )
        return self._store.save(team)

    def get_by_id(self, team_id: int) -> Team:
        """Get a team by ID.

        Args:
            team_id: The team ID

        Returns:
            The team

        Raises:
            TeamNotFoundError: If team not found
        """
        team = self._store.find_by_id(team_id)
        if team is None:
            raise TeamNotFoundError(team_id)
        return team

    def list_all(self) -> list[Team]:
        """Get all teams.

        Returns:
            List of all teams
        """
        return self._store.find_all()

    def name_exists(self, name: str) -> bool:
        """Check if a team name already exists.

        Args:
            name: The team name to check

        Returns:
            True if name exists, False otherwise
        """
        return self._store.name_exists(name)
