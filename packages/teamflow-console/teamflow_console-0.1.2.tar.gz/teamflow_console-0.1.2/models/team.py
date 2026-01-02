"""Team model for TeamFlow Console App."""

from typing import List

from pydantic import BaseModel, Field, field_validator


class Team(BaseModel):
    """Represents a group of users."""

    id: int = Field(default=0, description="Unique team identifier")
    name: str = Field(..., min_length=1, max_length=100)
    member_names: List[str] = Field(..., min_length=1)

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        """Validate that name is not empty or just whitespace."""
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()

    @field_validator("member_names")
    @classmethod
    def member_names_must_be_unique(cls, v: List[str]) -> List[str]:
        """Remove duplicate member names (case-insensitive) while preserving order."""
        seen = set()
        result = []
        for name in v:
            name_clean = name.strip()
            # Case-insensitive deduplication
            name_lower = name_clean.lower()
            if name_clean and name_lower not in seen:
                seen.add(name_lower)
                result.append(name_clean)
        return result
