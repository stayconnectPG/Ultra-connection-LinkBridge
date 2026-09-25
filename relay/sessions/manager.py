"""Session management for the relay gateway.

Tracks active WebSocket connections, pairs devices, and routes messages
between connected peers.

Responsibilities:
  * Attach/detach WebSocket connections by device ID
  * Look up the paired peer for a given sender
  * Forward (route) messages between paired peers
  * Expire sessions after inactivity
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from relay.authentication.token import TokenManager
from relay.routing.router import MessageRouter

logger = logging.getLogger(__name__)

DEFAULT_SESSION_TTL = 1800  # 30 minutes


class SessionManager:
    """Tracks connections, pairings, and routes messages."""

    def __init__(
        self,
        token_manager: TokenManager,
        session_ttl: int = DEFAULT_SESSION_TTL,
    ) -> None:
        self._token_manager = token_manager
        self._session_ttl = session_ttl
        # device_id -> (websocket, last_seen)
        self._connections: dict[str, tuple[Any, float]] = {}
        # device_id -> paired_device_id
        self._pairings: dict[str, str] = {}

        self._router = MessageRouter(
            get_peer=self._get_peer,
            deliver=self._deliver,
        )

    # -- Connection lifecycle -------------------------------------------------

    async def attach_connection(self, device_id: str, ws: Any) -> None:
        self._connections[device_id] = (ws, time.time())
        self._pairings.setdefault(device_id, device_id + "-peer")
        logger.info("Device %s connected", device_id)

    async def detach_connection(self, device_id: str) -> None:
        self._connections.pop(device_id, None)
        self._pairings.pop(device_id, None)
        logger.info("Device %s disconnected", device_id)

    def _get_peer(self, sender_id: str) -> Any | None:
        """Return the WebSocket of the paired peer, or None."""
        peer_id = self._pairings.get(sender_id)
        if peer_id is None:
            return None
        conn = self._connections.get(peer_id)
        return conn[0] if conn else None

    async def _deliver(self, peer_ws: Any, message: str) -> None:
        """Send a message to a peer WebSocket."""
        try:
            await peer_ws.send_text(message)
        except Exception as exc:
            logger.warning("Failed to deliver to peer: %s", exc)

    async def route_message(self, sender_id: str, raw_message: str) -> bool:
        """Route an incoming message to the paired peer."""
        await self._connections.get(sender_id, (None, 0))[1]  # touch? no
        return await self._router.route(sender_id, raw_message)

    async def cleanup_expired(self) -> None:
        """Remove connections idle beyond session_ttl."""
        now = time.time()
        expired = [
            dev_id
            for dev_id, (_, ts) in self._connections.items()
            if now - ts > self._session_ttl
        ]
        for dev_id in expired:
            logger.info("Cleaning up expired session for %s", dev_id)
            await self.detach_connection(dev_id)
