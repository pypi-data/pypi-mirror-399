"""Enums for Pobo SDK."""

from enum import StrEnum


class Language(StrEnum):
    """Supported languages for localized content."""

    DEFAULT = "default"
    CS = "cs"
    SK = "sk"
    EN = "en"
    DE = "de"
    PL = "pl"
    HU = "hu"


class WebhookEvent(StrEnum):
    """Webhook event types."""

    PRODUCTS_UPDATE = "products.update"
    CATEGORIES_UPDATE = "categories.update"
