"""Webhook payload DTO."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, field_validator


class WebhookPayload(BaseModel):
    """Webhook payload data."""

    event: str
    timestamp: datetime
    eshop_id: int

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, v: int | str | datetime) -> datetime:
        """Parse timestamp from various formats."""
        if isinstance(v, datetime):
            return v
        if isinstance(v, int):
            return datetime.fromtimestamp(v)
        return datetime.fromisoformat(v.replace("Z", "+00:00"))
