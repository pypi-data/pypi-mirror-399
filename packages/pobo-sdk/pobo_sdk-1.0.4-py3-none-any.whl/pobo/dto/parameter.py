"""Parameter DTOs."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ParameterValue(BaseModel):
    """Parameter value data transfer object."""

    id: int
    value: str

    def to_api_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API request."""
        return {"id": self.id, "value": self.value}


class Parameter(BaseModel):
    """Parameter data transfer object."""

    id: int
    name: str
    values: list[ParameterValue] = Field(default_factory=list)

    def to_api_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API request."""
        return {
            "id": self.id,
            "name": self.name,
            "values": [v.to_api_dict() for v in self.values],
        }
