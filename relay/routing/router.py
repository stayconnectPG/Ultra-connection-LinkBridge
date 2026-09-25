"""Message routing between paired device connections.

The router inspects incoming messages and determines the destination peer
based on the sender's device ID and the active session pairing.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)


class MessageRouter:
    """Routes decoded messages to the correct peer connection.

    The router delegates actual delivery to a callback provided by the
    session manager, keeping this class focused on address resolution
    and message transformation.
    """

    def __init__(
        self,
        get_peer: Callable[[str], Any | None],
        deliver: Callable[[str, str], "Any"],
    ) -> None:
        self._get_peer = get_peer
        self._deliver = deliver

    async def route(self, sender_id: str, raw_message: str) -> bool:
        """Route ``raw_message`` from ``sender_id`` to its paired peer.

        Returns True if the message was delivered, False otherwise
        (e.g. peer is not connected).
        """
        peer = self._get_peer(sender_id)
        if peer is None:
            logger.debug("No peer connected for sender %s", sender_id)
            return False

        try:
            data = json.loads(raw_message)
        except json.JSONDecodeError:
            logger.warning("Malformed JSON from %s", sender_id)
            return False

        # Inject sender metadata
        data.setdefault("meta", {})
        data["meta"]["sender_id"] = sender_id

        await self._deliver(peer, json.dumps(data))
        return True
