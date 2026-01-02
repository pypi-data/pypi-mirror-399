"""Service layer template with sentinel pattern for optional parameters.

This template demonstrates the correct way to handle optional parameters
that can be explicitly set to None vs. not provided at all.
"""

from typing import Protocol, Optional


# ============================================================================
# SENTINEL PATTERN - MUST be at MODULE LEVEL (not inside method!)
# ============================================================================

_UNSET = object()


# ============================================================================
# STORAGE PROTOCOL
# ============================================================================

class EntityStoreProtocol(Protocol):
    """Protocol for entity storage operations.

    Using Protocol enables swapping storage backends without changing
    business logic (e.g., in-memory → SQLite).
    """

    def save(self, entity) -> object:
        """Save entity and return with generated ID."""
        ...

    def find_by_id(self, entity_id: int):
        """Find entity by ID, return None if not found."""
        ...

    def find_all(self) -> list:
        """Return all entities."""
        ...

    def delete(self, entity_id: int) -> bool:
        """Delete entity by ID, return True if deleted."""
        ...


# ============================================================================
# SERVICE LAYER
# ============================================================================

class EntityNotFoundError(Exception):
    """Raised when entity is not found."""

    def __init__(self, entity_id: int) -> None:
        self.entity_id = entity_id
        super().__init__(f"Entity #{entity_id} not found")


class EntityService:
    """Business logic for entity operations.

    Key patterns:
    1. Depends on Protocol (not concrete implementation)
    2. Sentinel pattern for optional parameters
    3. Raises specific exceptions for error handling
    4. Returns model instances (not dicts)
    """

    def __init__(self, store: EntityStoreProtocol) -> None:
        """Initialize service with storage backend.

        Args:
            store: Any implementation of EntityStoreProtocol
        """
        self._store = store

    def create(self, **kwargs) -> object:
        """Create a new entity.

        Returns:
            The created entity with generated ID
        """
        # Generate ID based on existing entities
        all_entities = self._store.find_all()
        new_id = max([e.id for e in all_entities], default=0) + 1

        # Create entity (use your Pydantic model here)
        entity = YourEntity(id=new_id, **kwargs)
        return self._store.save(entity)

    def get_by_id(self, entity_id: int) -> object:
        """Get entity by ID.

        Args:
            entity_id: The entity ID

        Returns:
            The entity

        Raises:
            EntityNotFoundError: If entity not found
        """
        entity = self._store.find_by_id(entity_id)
        if entity is None:
            raise EntityNotFoundError(entity_id)
        return entity

    def list_all(self) -> list:
        """Get all entities.

        Returns:
            List of all entities
        """
        return self._store.find_all()

    def update(
        self,
        entity_id: int,
        field1: str | None = None,
        field2: str | None | object = _UNSET,
        # Add more fields as needed
    ) -> object:
        """Update entity fields.

        IMPORTANT: The sentinel pattern allows us to distinguish between:
        - field2 not provided (keep existing value)
        - field2 explicitly set to None (clear the value)

        Args:
            entity_id: The entity ID
            field1: New value for field1 (None means no change)
            field2: New value for field2 (None means clear if provided)

        Returns:
            The updated entity

        Raises:
            EntityNotFoundError: If entity not found
        """
        # Get existing entity
        entity = self.get_by_id(entity_id)
        entity_dict = entity.model_dump()

        # Update only provided fields
        if field1 is not None:
            entity_dict["field1"] = field1

        # Check if field2 was explicitly passed (including None)
        # Use module-level sentinel for comparison
        if field2 is not _UNSET:
            entity_dict["field2"] = field2

        # Create updated entity and save
        updated = type(entity)(**entity_dict)
        return self._store.save(updated)

    def delete(self, entity_id: int) -> None:
        """Delete entity by ID.

        Args:
            entity_id: The entity ID

        Raises:
            EntityNotFoundError: If entity not found
        """
        if not self._store.delete(entity_id):
            raise EntityNotFoundError(entity_id)


# ============================================================================
# PYDANTIC MODEL TEMPLATE
# ============================================================================

from pydantic import BaseModel, Field


class YourEntity(BaseModel):
    """Your entity model with validation."""

    id: int
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    status: str = "todo"  # or use Enum

    class Config:
        # Enable JSON serialization
        json_encoders = {}
