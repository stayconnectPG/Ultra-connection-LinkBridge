"""Connection manager abstraction.

The assistant core interacts with the connection manager through a standard
interface, allowing the transport (WebSocket, USB, local WiFi) to be swapped
without modifying core logic.

Example::

    manager = ConnectionManager(transport=WebSocketTransport())
    await manager.connect()
    await manager.send(message)
"""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Protocol, runtime_checkable

logger = logging.getLogger(__name__)


class ConnectionState(str, Enum):
    """Lifecycle states for a connection."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    ERROR = "error"


class MessageType(str, Enum):
    """Message types exchanged between peers."""

    COMMAND = "command"
    RESPONSE = "response"
    EVENT = "event"
    ACK = "ack"
    PING = "ping"
    PONG = "pong"
    AUTH = "auth"


@dataclass
class Message:
    """Envelope for a single message on the bridge."""

    type: MessageType
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime | None = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

    def model_dump(self) -> dict[str, Any]:
        """Serialize message to a plain dict (JSON-friendly)."""
        return {
            "type": self.type.value,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Message:
        """Deserialize a message from a plain dict."""
        ts = data.get("timestamp")
        return cls(
            type=MessageType(data["type"]),
            payload=data.get("payload", {}),
            timestamp=datetime.fromisoformat(ts) if ts else None,
        )


@runtime_checkable
class Transport(Protocol):
    """Protocol every transport implementation must satisfy."""

    async def connect(self) -> None: ...
    async def disconnect(self) -> None: ...
    async def send(self, data: str) -> None: ...
    async def receive(self) -> str | None: ...


class ConnectionManager:
    """High-level connection manager.

    Wraps a :class:`Transport` and provides message send/receive with
    automatic ack handling, ping/pong keepalive, and state management.
    """

    def __init__(self, transport: Transport, keepalive_interval: float = 30.0) -> None:
        self._transport = transport
        self._state: ConnectionState = ConnectionState.DISCONNECTED
        self._keepalive_interval = keepalive_interval
        self._keepalive_task: asyncio.Task[None] | None = None

    @property
    def state(self) -> ConnectionState:
        return self._state

    async def connect(self) -> None:
        """Open the underlying transport and start keepalive."""
        self._state = ConnectionState.CONNECTING
        await self._transport.connect()
        self._state = ConnectionState.CONNECTED
        self._keepalive_task = asyncio.create_task(self._keepalive_loop())
        logger.info("Connection established via %s", type(self._transport).__name__)

    async def disconnect(self) -> None:
        """Close the connection gracefully."""
        self._state = ConnectionState.DISCONNECTING
        if self._keepalive_task:
            self._keepalive_task.cancel()
            self._keepalive_task = None
        await self._transport.disconnect()
        self._state = ConnectionState.DISCONNECTED
        logger.info("Connection closed")

    async def send(self, message: Message) -> None:
        """Serialize and send a message."""
        import json

        payload = json.dumps(message.model_dump())
        await self._transport.send(payload)

    async def receive(self) -> Message | None:
        """Receive and deserialize a message."""
        import json

        raw = await self._transport.receive()
        if raw is None:
            return None
        return Message.from_dict(json.loads(raw))

    async def _keepalive_loop(self) -> None:
        """Periodically send ping messages to keep the connection alive."""
        try:
            while True:
                await asyncio.sleep(self._keepalive_interval)
                await self.send(Message(type=MessageType.PING, payload={}))
        except asyncio.CancelledError:
            return
