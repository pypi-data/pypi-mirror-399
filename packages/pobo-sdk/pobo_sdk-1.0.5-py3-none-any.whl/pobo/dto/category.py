"""Category DTO."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from pobo.dto.content import Content
from pobo.dto.localized_string import LocalizedString


class Category(BaseModel):
    """Category data transfer object."""

    id: str
    is_visible: bool
    name: LocalizedString
    url: LocalizedString
    description: Optional[LocalizedString] = None
    seo_title: Optional[LocalizedString] = None
    seo_description: Optional[LocalizedString] = None
    content: Optional[Content] = None
    images: List[str] = Field(default_factory=list)
    guid: Optional[str] = None
    is_loaded: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_api_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request."""
        data: Dict[str, Any] = {
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
