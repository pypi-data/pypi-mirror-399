"""
Pobo SDK - Official Python SDK for Pobo API V2.

Product content management and webhooks.
"""

from pobo.client import PoboClient
from pobo.webhook_handler import WebhookHandler
from pobo.enums import Language, WebhookEvent
from pobo.exceptions import ApiError, ValidationError, WebhookError, PoboError
from pobo.dto import (
    LocalizedString,
    Content,
    Product,
    Category,
    Blog,
    Parameter,
    ParameterValue,
    ImportResult,
    PaginatedResponse,
    WebhookPayload,
)

__version__ = "1.0.4"

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
