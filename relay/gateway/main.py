"""Main FastAPI application for the relay gateway.

The gateway serves:
  - HTTPS endpoints for auth, registration, and session management
  - WSS endpoints for real-time bidirectional message forwarding
"""

from __future__ import annotations

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from relay.authentication.token import TokenManager, TokenPayload
from relay.sessions.manager import SessionManager

logger = logging.getLogger("relay")

# ---------------------------------------------------------------------------
# Services (singletons for the application lifetime)
# ---------------------------------------------------------------------------

token_manager = TokenManager()
session_manager = SessionManager(token_manager=token_manager)


# ---------------------------------------------------------------------------
# Pydantic request models
# ---------------------------------------------------------------------------


class DeviceRegisterRequest(BaseModel):
    device_id: str
    type: str
    platform: str
    public_key: str = ""


class AuthRequest(BaseModel):
    device_id: str
    signed_token: str = ""


class SessionCreateRequest(BaseModel):
    device_id: str
    paired_device_id: str


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Relay gateway starting up")
    yield
    logger.info("Relay gateway shutting down")


app = FastAPI(
    title="LinkBridge Relay Gateway",
    description="WebSocket relay gateway for the Debian ↔ Android assistant bridge.",
    version="0.1.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# HTTPS endpoints
# ---------------------------------------------------------------------------


@app.get("/status")
async def status() -> dict[str, str]:
    return {"status": "healthy", "service": "relay-gateway"}


@app.post("/devices/register")
async def register_device(req: DeviceRegisterRequest) -> dict[str, Any]:
    """Register a new device."""
    success, token, err = token_manager.register_device(
        device_id=req.device_id,
        device_type=req.type,
        platform=req.platform,
        public_key=req.public_key,
    )
    if not success:
        raise HTTPException(status_code=409, detail=err or "Registration failed")
    return {"device_id": req.device_id, "access_token": token}


@app.post("/auth")
async def authenticate(req: AuthRequest) -> dict[str, Any]:
    """Authenticate a device and return a session token."""
    payload = token_manager.validate_access_token(req.signed_token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    session_token = session_manager.create_session(payload.device_id)
    return {"session_token": session_token}


@app.post("/session")
async def create_session(req: SessionCreateRequest) -> dict[str, Any]:
    """Create a session between two paired devices."""
    token = token_manager.issue_session_token(
        device_id=req.device_id,
        paired_device_id=req.paired_device_id,
    )
    return {"session_token": token}


# ---------------------------------------------------------------------------
# WebSocket endpoint
# ---------------------------------------------------------------------------


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """WebSocket entry point for device connections.

    Flow:
      1. Accept connection
      2. Receive ``auth`` message with a session token
      3. Validate token and attach to session
      4. Forward messages between paired peers
    """
    await ws.accept()
    try:
        # First message must be auth
        raw = await ws.receive_text()
        msg = json.loads(raw)
        if msg.get("type") != "auth":
            await ws.close(code=4001)
            return

        token = msg.get("token", "")
        payload = token_manager.validate_session_token(token)
        if payload is None:
            await ws.close(code=4001)
            return

        device_id = payload.device_id

        # Register connection in session manager
        await session_manager.attach_connection(device_id, ws)

        # Message loop
        while True:
            raw = await ws.receive_text()
            forwarded = await session_manager.route_message(device_id, raw)
            if not forwarded:
                # No peer connected; could buffer or drop
                logger.debug("No peer for device %s", device_id)

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected: %s", device_id)
    except Exception as exc:
        logger.exception("WebSocket error: %s", exc)
    finally:
        if "device_id" in dir():
            await session_manager.detach_connection(device_id)
        await ws.close()
