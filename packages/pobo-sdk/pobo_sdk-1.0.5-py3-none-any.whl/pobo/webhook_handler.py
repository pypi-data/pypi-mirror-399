"""Webhook handler for Pobo webhooks."""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any, Optional, Union

from pobo.dto.webhook_payload import WebhookPayload
from pobo.exceptions import WebhookError


class WebhookHandler:
    """Handler for Pobo webhook requests."""

    SIGNATURE_HEADER = "X-Webhook-Signature"

    def __init__(self, webhook_secret: str) -> None:
        self.webhook_secret = webhook_secret

    def handle(self, payload: Union[str, bytes], signature: Optional[str]) -> WebhookPayload:
        """
        Validate and parse webhook payload.

        Args:
            payload: Raw request body as string or bytes
            signature: Value of X-Webhook-Signature header

        Returns:
            Parsed WebhookPayload

        Raises:
            WebhookError: If signature is missing, invalid, or payload is malformed
        """
        if not signature:
            raise WebhookError.missing_signature()

        if isinstance(payload, str):
            payload_bytes = payload.encode("utf-8")
        else:
            payload_bytes = payload

        if not self._verify_signature(payload_bytes, signature):
            raise WebhookError.invalid_signature()

        try:
            data = json.loads(payload_bytes)
            return WebhookPayload.model_validate(data)
        except (json.JSONDecodeError, ValueError) as e:
            raise WebhookError.invalid_payload() from e

    def handle_request(self, request: Any) -> WebhookPayload:
        """
        Handle webhook from a web framework request object.

        Works with Django, Flask, and other frameworks that have
        request.body and request.headers.

        Args:
            request: Web framework request object

        Returns:
            Parsed WebhookPayload
        """
        # Get body
        if hasattr(request, "body"):
            # Django
            payload = request.body
        elif hasattr(request, "data"):
            # Flask
            payload = request.data
        elif hasattr(request, "get_data"):
            # Flask alternative
            payload = request.get_data()
        else:
            raise WebhookError.invalid_payload()

        # Get signature
        signature = None
        if hasattr(request, "headers"):
            signature = request.headers.get(self.SIGNATURE_HEADER)
        elif hasattr(request, "META"):
            # Django
            signature = request.META.get("HTTP_X_WEBHOOK_SIGNATURE")

        return self.handle(payload, signature)

    def _verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify HMAC-SHA256 signature."""
        expected = hmac.new(
            self.webhook_secret.encode("utf-8"),
            payload,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(expected, signature)
