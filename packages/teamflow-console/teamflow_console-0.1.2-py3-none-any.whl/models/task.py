"""Task model for TeamFlow Console App."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Priority(str, Enum):
    """Task priority levels."""

    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class Status(str, Enum):
    """Task status values."""

    TODO = "Todo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"


class Task(BaseModel):
    """Represents a work item in the task distribution system."""

    id: int = Field(default=0, description="Unique task identifier")
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Priority = Field(default=Priority.MEDIUM)
    status: Status = Field(default=Status.TODO)
    assignee_id: Optional[int] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        """Validate that title is not empty or just whitespace."""
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    @field_validator("description")
    @classmethod
    def description_must_be_stripped(cls, v: Optional[str]) -> Optional[str]:
        """Strip whitespace from description if provided."""
        if v is not None:
            return v.strip() or None
        return v
