"""Exceptions for Pobo SDK."""

from typing import Any


class PoboError(Exception):
    """Base exception for Pobo SDK."""

    pass


class ApiError(PoboError):
    """API error with HTTP status code and response body."""

    def __init__(
        self,
        message: str,
        http_code: int | None = None,
        response_body: Any = None,
    ) -> None:
        super().__init__(message)
        self.http_code = http_code
        self.response_body = response_body

    @classmethod
    def unauthorized(cls) -> "ApiError":
        return cls("Authorization token required", http_code=401)

    @classmethod
    def from_response(cls, http_code: int, body: Any) -> "ApiError":
        if isinstance(body, dict):
            message = body.get("error") or body.get("message") or "API error"
        else:
            message = "API error"
        return cls(message, http_code=http_code, response_body=body)


class ValidationError(PoboError):
    """Validation error with field errors."""

    def __init__(self, message: str, errors: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.errors = errors or {}

    @classmethod
    def empty_payload(cls) -> "ValidationError":
        return cls("Payload cannot be empty")

    @classmethod
    def too_many_items(cls, count: int, max_items: int) -> "ValidationError":
        return cls(f"Too many items: {count} provided, maximum is {max_items}")


class WebhookError(PoboError):
    """Webhook validation error."""

    @classmethod
    def missing_signature(cls) -> "WebhookError":
        return cls("Missing webhook signature")

    @classmethod
    def invalid_signature(cls) -> "WebhookError":
        return cls("Invalid webhook signature")

    @classmethod
    def invalid_payload(cls) -> "WebhookError":
        return cls("Invalid webhook payload")
