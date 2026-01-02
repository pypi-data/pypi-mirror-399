"""Content DTO for HTML and marketplace content."""

from __future__ import annotations

from pydantic import BaseModel

from pobo.enums import Language


class Content(BaseModel):
    """HTML and marketplace content for multiple languages."""

    html: dict[str, str] = {}
    marketplace: dict[str, str] = {}

    def get_html(self, language: Language | str) -> str | None:
        """Get HTML content for a specific language."""
        return self.html.get(str(language))

    def get_marketplace(self, language: Language | str) -> str | None:
        """Get marketplace content for a specific language."""
        return self.marketplace.get(str(language))

    @property
    def html_default(self) -> str | None:
        """Get default HTML content."""
        return self.html.get("default")

    @property
    def marketplace_default(self) -> str | None:
        """Get default marketplace content."""
        return self.marketplace.get("default")
