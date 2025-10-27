"""
WebSocket broadcasting for trade events.

Provides a lightweight in-memory pub/sub so connected clients receive
real-time trade notifications. Intended for development/demo use and not
backed by an external message broker.
"""

import asyncio
import json
import logging
from typing import Set

from fastapi import WebSocket


logger = logging.getLogger(__name__)


class TradeEventManager:
    """Manage WebSocket connections for trade events."""

    def __init__(self) -> None:
        self._connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        """Accept and track a WebSocket connection."""
        await websocket.accept()
        async with self._lock:
            self._connections.add(websocket)
        logger.info("WebSocket connected. active=%s", len(self._connections))

    async def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        async with self._lock:
            self._connections.discard(websocket)
        logger.info("WebSocket disconnected. active=%s", len(self._connections))

    async def broadcast(self, message: dict) -> None:
        """Broadcast a message to all connected clients."""
        async with self._lock:
            connections = list(self._connections)

        if not connections:
            return

        payload = json.dumps(message, default=str)

        disconnects = []
        for websocket in connections:
            try:
                await websocket.send_text(payload)
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("WebSocket send failed: %s", exc)
                disconnects.append(websocket)

        for websocket in disconnects:
            await self.disconnect(websocket)


trade_event_manager = TradeEventManager()

