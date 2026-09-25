# AGENTS.md - Project guidance for autonomous agents

## Overview

Debian \u2194 Android Assistant Bridge \u2014 a secure communication layer enabling a
Debian/Linux virtual-assistant host to communicate bidirectionally with an
Android remote UI over the public Internet via a WebSocket relay gateway.

## Architecture summary

```
Android  \u2194  WSS/TLS  \u2194  Relay/Gateway  \u2194  WSS/TLS  \u2194  Debian
```

- **debian/** \u2014 Python FastAPI + asyncio assistant core, connection manager, API, device identity
- **android/** \u2014 Kotlin Android app, WebSocket client, device identity
- **relay/** \u2014 Python gateway: authentication, routing, session management, HTTPS + WSS
- **docs/** \u2014 architecture, protocol, security, deployment, troubleshooting
- **tests/** \u2014 pytest suites (run with `pytest`)
- **scripts/** \u2013 DevOps: setup, deployment, certificate generation

## Tech stack

| Component  | Language  | Runtime   | Key libraries                        |
|------------|-----------|-----------|--------------------------------------|
| debian     | Python    | 3.11+     | FastAPI, uvicorn, websockets, asyncio |
| relay      | Python    | 3.11+     | FastAPI, websockets, cryptography, PyJWT |
| android    | Kotlin    | Android   | Android SDK, OkHttp WebSocket        |

## Coding conventions

- Python: PEP 8, type hints mandatory, `ruff` + `mypy` enforced, async-first
- Kotlin: Kotlin coding conventions, coroutines for async, AndroidX libraries

## Build & test

```bash
# Install deps (Python)
pip install -e ".[dev]"

# Lint + typecheck
ruff check .
mypy debian relay

# Run tests
pytest

# Run Debian core (local dev)
uvicorn debian.api.main:app --reload

# Run Relay gateway (local dev)
uvicorn relay.gateway.main:app --reload
```

## Phases

The project follows the roadmap in README.md (Phase 1\u2014Local comms,
Phase 2\u2014WebSocket, Phase 3\u2014Security/TLS, Phase 4\u2014Relay,
Phase 5\u2014Identity & sessions, Phase 6\u2014Global comms).
