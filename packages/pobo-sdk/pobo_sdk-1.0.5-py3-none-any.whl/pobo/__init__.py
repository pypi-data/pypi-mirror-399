"""
Pobo SDK - Official Python SDK for Pobo API V2.

Product content management and webhooks.
"""

from pobo.client import PoboClient
from pobo.dto import (
    Blog,
    Category,
    Content,
    ImportResult,
    LocalizedString,
    PaginatedResponse,
    Parameter,
    ParameterValue,
    Product,
    WebhookPayload,
)
from pobo.enums import Language, WebhookEvent
from pobo.exceptions import ApiError, PoboError, ValidationError, WebhookError
from pobo.webhook_handler import WebhookHandler

__version__ = "1.0.5"

__all__ = [
    # Client
    "PoboClient",
    "WebhookHandler",
    # Enums
    "Language",
    "WebhookEvent",
    # Exceptions
    "PoboError",
    "ApiError",
    "ValidationError",
    "WebhookError",
    # DTOs
    "LocalizedString",
    "Content",
    "Product",
    "Category",
    "Blog",
    "Parameter",
    "ParameterValue",
    "ImportResult",
    "PaginatedResponse",
    "WebhookPayload",
]
