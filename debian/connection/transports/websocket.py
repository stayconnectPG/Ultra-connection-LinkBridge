"""WebSocket transport implementation (Phase 2+)."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import websockets.client
from websockets.client import connect as ws_connect
from websockets.exceptions import ConnectionClosed

logger = logging.getLogger(__name__)


class WebSocketTransport:
    """WebSocket-based :class:`~debian.connection.manager.Transport`."""

    def __init__(
        self,
        uri: str,
        headers: dict[str, str] | None = None,
        ping_interval: float = 20.0,
    ) -> None:
        self._uri = uri
        self._headers = headers or {}
        self._ping_interval = ping_interval
        self._conn: websockets.client.WebSocketClientProtocol | None = None
        self._recv_queue: asyncio.Queue[str | None] = asyncio.Queue()

    async def connect(self) -> None:
        self._conn = await ws_connect(
            self._uri,
            extra_headers=self._headers,
            ping_interval=self._ping_interval,
        )
        asyncio.create_task(self._reader_loop())
        logger.info("WebSocket connected to %s", self._uri)

    async def disconnect(self) -> None:
        if self._conn and not self._conn.closed:
            await self._conn.close()
        self._conn = None
        await self._recv_queue.put(None)

    async def send(self, data: str) -> None:
        if self._conn is None or self._conn.closed:
            raise ConnectionError("WebSocket not connected")
        await self._conn.send(data)

    async def receive(self) -> str | None:
        return await self._recv_queue.get()

    async def _reader_loop(self) -> None:
        """Background coroutine that reads incoming frames into the queue."""
        if self._conn is None:
            return
        try:
            async for raw in self._conn:
                await self._recv_queue.put(raw.decode("utf-8"))
        except ConnectionClosed:
            logger.warning("WebSocket connection closed")
            await self._recv_queue.put(None)
        except Exception as exc:
            logger.exception("WebSocket reader error: %s", exc)
            await self._recv_queue.put(None)
