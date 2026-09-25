"""Device identity representation and persistence.

Each device in the bridge has a unique identity used for pairing,
authentication, and routing.
"""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import keyring
except ImportError:  # keyring optional at early stage
    keyring = None  # type: ignore[assignment]


@dataclass
class DeviceIdentity:
    """Logical identity of a device on the bridge."""

    device_id: str
    device_type: str  # "server", "android", "assistant"
    platform: str  # "debian", "android"
    public_key: str = ""
    created_at: str = ""

    def model_dump(self) -> dict[str, Any]:
        return {
            "device_id": self.device_id,
            "type": self.device_type,
            "platform": self.platform,
            "public_key": self.public_key,
            "created_at": self.created_at,
        }

    @classmethod
    def generate(
        cls,
        device_type: str = "server",
        platform: str = "debian",
        public_key: str = "",
    ) -> DeviceIdentity:
        """Generate a new random device identity."""
        return cls(
            device_id=f"{platform}-{uuid.uuid4().hex[:8]}",
            device_type=device_type,
            platform=platform,
            public_key=public_key,
        )


class DeviceIdentityStore:
    """Persists device identity to the local filesystem.

    In Phase 5+ credentials will move to the OS keyring; for now we use a
    simple JSON file in the user config directory.
    """

    def __init__(self, config_dir: str | Path | None = None) -> None:
        self._config_dir = Path(config_dir or os.path.expanduser("~/.config/dab"))
        self._config_dir.mkdir(parents=True, exist_ok=True)
        self._file = self._config_dir / "device_identity.json"

    def load(self) -> DeviceIdentity | None:
        """Load the stored identity, or None if not yet created."""
        if not self._file.exists():
            return None
        import json

        data = json.loads(self._file.read_text())
        return DeviceIdentity(
            device_id=data["device_id"],
            device_type=data["type"],
            platform=data["platform"],
            public_key=data.get("public_key", ""),
            created_at=data.get("created_at", ""),
        )

    def save(self, identity: DeviceIdentity) -> None:
        """Persist a device identity."""
        import json

        self._file.write_text(json.dumps(identity.model_dump(), indent=2))
        if keyring is not None:
            keyring.set_password("dab", identity.device_id, identity.public_key)

    def get_or_create(
        self,
        device_type: str = "server",
        platform: str = "debian",
        public_key: str = "",
    ) -> DeviceIdentity:
        """Return the existing identity or create a new one."""
        existing = self.load()
        if existing is not None:
            return existing
        identity = DeviceIdentity.generate(
            device_type=device_type,
            platform=platform,
            public_key=public_key,
        )
        self.save(identity)
        return identity
