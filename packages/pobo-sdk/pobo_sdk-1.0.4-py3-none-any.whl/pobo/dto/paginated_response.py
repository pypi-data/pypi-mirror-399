"""Paginated response DTO."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated API response."""

    data: list[T] = Field(default_factory=list)
    current_page: int = 1
    per_page: int = 100
    total: int = 0

    @property
    def total_pages(self) -> int:
        """Calculate total number of pages."""
        if self.per_page == 0:
            return 0
        return (self.total + self.per_page - 1) // self.per_page

    def has_more_pages(self) -> bool:
        """Check if there are more pages."""
        return self.current_page < self.total_pages
