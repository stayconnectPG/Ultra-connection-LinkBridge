"""Token management: access tokens, session tokens, device registration.

Tokens carry claims identifying the bearer device, the paired peer, and an
expiry timestamp. Two kinds of token are issued:

* **access_token** — long-lived credential bound to a device; used to boot-
  strap sessions (e.g. when registering the Android app).
* **session_token** — short-lived (default 30 min) credential used to
  authenticate the WebSocket connection.
"""

from __future__ import annotations

import logging
import os
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

logger = logging.getLogger(__name__)

DEFAULT_SESSION_TTL = int(os.environ.get("SESSION_TTL", "1800"))
DEFAULT_ALGORITHM = "HS256"


@dataclass
class TokenPayload:
    """Decoded JWT claims."""

    device_id: str
    device_type: str = ""
    platform: str = ""
    paired_device_id: str = ""
    kind: str = "session"  # "access" or "session"
    exp: int = 0
    iat: int = 0

    def model_dump(self) -> dict[str, Any]:
        return {
            "device_id": self.device_id,
            "type": self.device_type,
            "platform": self.platform,
            "paired_device_id": self.paired_device_id,
            "kind": self.kind,
            "exp": self.exp,
            "iat": self.iat,
        }


@dataclass
class RegisteredDevice:
    """A device registered with the relay."""

    device_id: str
    device_type: str
    platform: str
    public_key: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class TokenManager:
    """Issues and validates JWTs for the relay."""

    def __init__(
        self,
        secret: str | None = None,
        algorithm: str = DEFAULT_ALGORITHM,
        session_ttl: int = DEFAULT_SESSION_TTL,
    ) -> None:
        self._secret = secret or os.environ.get("JWT_SECRET") or secrets.token_hex(32)
        self._algorithm = algorithm
        self._session_ttl = session_ttl
        self._devices: dict[str, RegisteredDevice] = {}

    # -- Device registration --------------------------------------------------

    def register_device(
        self,
        device_id: str,
        device_type: str,
        platform: str,
        public_key: str = "",
    ) -> tuple[bool, str, str | None]:
        """Register a device. Returns (success, access_token, error)."""
        if device_id in self._devices:
            return False, "", "Device already registered"
        self._devices[device_id] = RegisteredDevice(
            device_id=device_id,
            device_type=device_type,
            platform=platform,
            public_key=public_key,
        )
        token = self._issue_access_token(device_id, device_type, platform)
        logger.info("Registered device %s", device_id)
        return True, token, None

    def get_device(self, device_id: str) -> RegisteredDevice | None:
        return self._devices.get(device_id)

    # -- Token issuance -------------------------------------------------------

    def _issue_access_token(
        self, device_id: str, device_type: str, platform: str
    ) -> str:
        now = datetime.now(timezone.utc)
        claims = {
            "device_id": device_id,
            "type": device_type,
            "platform": platform,
            "kind": "access",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(days=365)).timestamp()),
        }
        return jwt.encode(claims, self._secret, algorithm=self._algorithm)

    def issue_session_token(
        self, device_id: str, paired_device_id: str = ""
    ) -> str:
        """Issue a short-lived session token for WebSocket auth."""
        now = datetime.now(timezone.utc)
        claims = {
            "device_id": device_id,
            "paired_device_id": paired_device_id,
            "kind": "session",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=self._session_ttl)).timestamp()),
        }
        return jwt.encode(claims, self._secret, algorithm=self._algorithm)

    # -- Token validation -----------------------------------------------------

    def validate_access_token(self, token: str) -> TokenPayload | None:
        return self._decode(token, expected_kind="access")

    def validate_session_token(self, token: str) -> TokenPayload | None:
        return self._decode(token, expected_kind="session")

    def _decode(self, token: str, expected_kind: str) -> TokenPayload | None:
        """Decode and validate a JWT. Returns None on failure."""
        if not token:
            return None
        try:
            claims = jwt.decode(token, self._secret, algorithms=[self._algorithm])
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as exc:
            logger.warning("Invalid token: %s", exc)
            return None

        if claims.get("kind") != expected_kind:
            logger.warning("Token kind mismatch: expected %s, got %s",
                           expected_kind, claims.get("kind"))
            return None

        return TokenPayload(
            device_id=claims["device_id"],
            device_type=claims.get("type", ""),
            platform=claims.get("platform", ""),
            paired_device_id=claims.get("paired_device_id", ""),
            kind=claims.get("kind", ""),
            exp=claims.get("exp", 0),
            iat=claims.get("iat", 0),
        )
