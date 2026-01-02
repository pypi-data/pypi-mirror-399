"""Import result DTO."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ImportResult(BaseModel):
    """Result of a bulk import operation."""

    success: bool = True
    imported: int = 0
    updated: int = 0
    skipped: int = 0
    errors: list[dict[str, Any]] = Field(default_factory=list)
    values_imported: int | None = None
    values_updated: int | None = None

    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0
