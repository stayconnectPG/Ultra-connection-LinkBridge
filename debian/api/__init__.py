"""FastAPI application for the Debian assistant API."""

from __future__ import annotations

import logging

from fastapi import FastAPI

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Debian Assistant API",
    description="Local API for the Debian ↔ Android assistant bridge.",
    version="0.1.0",
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/status")
async def status() -> dict[str, str]:
    """Detailed service status."""
    return {"status": "healthy", "service": "debian-assistant"}
