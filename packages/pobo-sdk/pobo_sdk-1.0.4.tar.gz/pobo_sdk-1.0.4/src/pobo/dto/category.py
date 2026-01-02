"""Category DTO."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from pobo.dto.localized_string import LocalizedString
from pobo.dto.content import Content


class Category(BaseModel):
    """Category data transfer object."""

    id: str
    is_visible: bool
    name: LocalizedString
    url: LocalizedString
    description: LocalizedString | None = None
    seo_title: LocalizedString | None = None
    seo_description: LocalizedString | None = None
    content: Content | None = None
    images: list[str] = Field(default_factory=list)
    guid: str | None = None
    is_loaded: bool | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def to_api_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API request."""
        data: dict[str, Any] = {
            "id": self.id,
            "is_visible": self.is_visible,
            "name": self.name.to_dict(),
            "url": self.url.to_dict(),
        }

        if self.description:
            data["description"] = self.description.to_dict()
        if self.seo_title:
            data["seo_title"] = self.seo_title.to_dict()
        if self.seo_description:
            data["seo_description"] = self.seo_description.to_dict()
        if self.images:
            data["images"] = self.images

        return data
