"""Localized string DTO."""

from __future__ import annotations

from typing import Dict, Optional, Union

from pydantic import BaseModel, ConfigDict

from pobo.enums import Language


class LocalizedString(BaseModel):
    """A string with translations for multiple languages."""

    model_config = ConfigDict(extra="allow")

    default: Optional[str] = None
    cs: Optional[str] = None
    sk: Optional[str] = None
    en: Optional[str] = None
    de: Optional[str] = None
    pl: Optional[str] = None
    hu: Optional[str] = None

    @classmethod
    def create(cls, default_value: str) -> LocalizedString:
        """Create a LocalizedString with a default value."""
        return cls(default=default_value)

    def _get_language_key(self, language: Union[Language, str]) -> str:
        """Get the string key for a language."""
        if isinstance(language, Language):
            return language.value
        return language

    def with_translation(self, language: Union[Language, str], value: str) -> LocalizedString:
        """Return a new LocalizedString with an additional translation."""
        data = self.model_dump(exclude_none=True)
        key = self._get_language_key(language)
        data[key] = value
        return LocalizedString.model_validate(data)

    def get(self, language: Union[Language, str]) -> Optional[str]:
        """Get translation for a specific language."""
        key = self._get_language_key(language)
        return getattr(self, key, None)

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary, excluding None values."""
        return self.model_dump(exclude_none=True)
