from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class EventEnvelope(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str
    version: int = 1
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tenant_id: str | None = None
    producer: str
    correlation_id: str
    causation_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
