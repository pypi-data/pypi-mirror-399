"""User model for TeamFlow Console App."""

from enum import Enum
from typing import List

from pydantic import BaseModel, Field, field_validator


class Role(str, Enum):
    """User role types."""

    ADMIN = "Admin"
    DEVELOPER = "Developer"
    DESIGNER = "Designer"


class User(BaseModel):
    """Represents a team member who can be assigned tasks."""

    id: int = Field(default=0, description="Unique user identifier")
    name: str = Field(..., min_length=1, max_length=100)
    role: Role = Field(default=Role.DEVELOPER)
    skills: List[str] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        """Validate that name is not empty or just whitespace."""
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()

    @field_validator("skills")
    @classmethod
    def skills_must_be_unique(cls, v: List[str]) -> List[str]:
        """Remove duplicate skills while preserving order."""
        seen = set()
        result = []
        for skill in v:
            skill_clean = skill.strip()
            skill_lower = skill_clean.lower()
            if skill_clean and skill_lower not in seen:
                seen.add(skill_lower)
                result.append(skill_clean)
        return result
