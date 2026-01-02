"""Tests for WebhookHandler."""

import hashlib
import hmac
import json

import pytest

from pobo import WebhookHandler, WebhookError


class TestWebhookHandler:
    @pytest.fixture
    def secret(self):
        return "webhook-secret"

    @pytest.fixture
    def handler(self, secret):
        return WebhookHandler(webhook_secret=secret)

    def sign(self, payload: str, secret: str) -> str:
        return hmac.new(
            secret.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def test_handle_valid_payload(self, handler, secret):
        payload = json.dumps({"event": "products.update", "timestamp": 1704067200, "eshop_id": 123})
        signature = self.sign(payload, secret)

        result = handler.handle(payload, signature)

        assert result.event == "products.update"
        assert result.eshop_id == 123

    def test_handle_missing_signature(self, handler):
        payload = json.dumps({"event": "products.update"})

        with pytest.raises(WebhookError, match="Missing webhook signature"):
            handler.handle(payload, None)

    def test_handle_invalid_signature(self, handler):
        payload = json.dumps({"event": "products.update"})

        with pytest.raises(WebhookError, match="Invalid webhook signature"):
            handler.handle(payload, "invalid-signature")

    def test_handle_invalid_json(self, handler, secret):
        payload = "not json"
        signature = self.sign(payload, secret)

        with pytest.raises(WebhookError, match="Invalid webhook payload"):
            handler.handle(payload, signature)
