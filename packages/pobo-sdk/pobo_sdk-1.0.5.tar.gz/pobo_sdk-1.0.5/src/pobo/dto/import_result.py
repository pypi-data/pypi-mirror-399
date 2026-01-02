"""Import result DTO."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ImportResult(BaseModel):
    """Result of a bulk import operation."""

    success: bool = True
    imported: int = 0
    updated: int = 0
    skipped: int = 0
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    values_imported: Optional[int] = None
    values_updated: Optional[int] = None

    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0
