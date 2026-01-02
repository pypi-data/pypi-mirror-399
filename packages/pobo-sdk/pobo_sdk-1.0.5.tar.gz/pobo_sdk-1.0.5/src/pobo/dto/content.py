"""Content DTO for HTML and marketplace content."""

from __future__ import annotations

from typing import Dict, Optional, Union

from pydantic import BaseModel, Field

from pobo.enums import Language


class Content(BaseModel):
    """HTML and marketplace content for multiple languages."""

    html: Dict[str, str] = Field(default_factory=dict)
    marketplace: Dict[str, str] = Field(default_factory=dict)

    def _get_language_key(self, language: Union[Language, str]) -> str:
        """Get the string key for a language."""
        if isinstance(language, Language):
            return language.value
        return language

    def get_html(self, language: Union[Language, str]) -> Optional[str]:
        """Get HTML content for a specific language."""
        key = self._get_language_key(language)
        return self.html.get(key)

    def get_marketplace(self, language: Union[Language, str]) -> Optional[str]:
        """Get marketplace content for a specific language."""
        key = self._get_language_key(language)
        return self.marketplace.get(key)

    @property
    def html_default(self) -> Optional[str]:
        """Get default HTML content."""
        return self.html.get("default")

    @property
    def marketplace_default(self) -> Optional[str]:
        """Get default marketplace content."""
        return self.marketplace.get("default")
