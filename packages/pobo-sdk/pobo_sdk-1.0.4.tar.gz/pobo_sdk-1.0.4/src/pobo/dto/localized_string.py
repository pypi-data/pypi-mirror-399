"""Localized string DTO."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from pobo.enums import Language


class LocalizedString(BaseModel):
    """A string with translations for multiple languages."""

    model_config = ConfigDict(extra="allow")

    default: str | None = None
    cs: str | None = None
    sk: str | None = None
    en: str | None = None
    de: str | None = None
    pl: str | None = None
    hu: str | None = None

    @classmethod
    def create(cls, default_value: str) -> LocalizedString:
        """Create a LocalizedString with a default value."""
        return cls(default=default_value)

    def with_translation(self, language: Language | str, value: str) -> LocalizedString:
        """Return a new LocalizedString with an additional translation."""
        data = self.model_dump(exclude_none=True)
        data[str(language)] = value
        return LocalizedString.model_validate(data)

    def get(self, language: Language | str) -> str | None:
        """Get translation for a specific language."""
        return getattr(self, str(language), None)

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary, excluding None values."""
        return self.model_dump(exclude_none=True)
