"""Enums for Pobo SDK."""

from enum import Enum


class Language(str, Enum):
    """Supported languages for localized content."""

    DEFAULT = "default"
    CS = "cs"
    SK = "sk"
    EN = "en"
    DE = "de"
    PL = "pl"
    HU = "hu"


class WebhookEvent(str, Enum):
    """Webhook event types."""

    PRODUCTS_UPDATE = "products.update"
    CATEGORIES_UPDATE = "categories.update"
