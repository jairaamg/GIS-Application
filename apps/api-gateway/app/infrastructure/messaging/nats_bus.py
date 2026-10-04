from __future__ import annotations

import json
from typing import Any


class NatsEventBus:
    """Thin placeholder for NATS JetStream publishing."""

    def __init__(self, url: str) -> None:
        self.url = url
        self._nc = None

    async def connect(self) -> None:
        # Connection wired during service bootstrap.
        return None

    async def publish(self, subject: str, event: Any) -> None:
        payload = event.model_dump_json() if hasattr(event, "model_dump_json") else json.dumps(event)
        # Placeholder: log-only until NATS client is connected in runtime bootstrap.
        print(f"[nats-stub] publish {subject}: {payload[:200]}")
