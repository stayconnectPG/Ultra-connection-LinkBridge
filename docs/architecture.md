# Architecture

## Overview

The Debian ↔ Android Assistant Bridge uses a three-tier architecture connected
over the public Internet:

```
Android  ⇄  WSS/TLS  ⇄  Relay/Gateway  ⇄  WSS/TLS  ⇄  Debian
```

## Components

### Debian (Assistant Core)

- **assistant/** — Core AI assistant logic, intent processing, service orchestration
- **connection/** — Connection manager abstraction layer with pluggable transports
- **api/** — FastAPI HTTP/WebSocket endpoints exposed locally
- **device/** — Device identity, pairing, and credential management

### Android (Remote UI)

- **app/** — Android application (Activities, Views, ViewModels)
- **connection/** — WebSocket client transport implementation
- **device/** — Device identity and token storage

### Relay (Gateway)

- **gateway/** — FastAPI + websockets server, routing, session orchestration
- **authentication/** — JWT/token issuance, device authentication
- **routing/** — Message routing between paired peers
- **sessions/** — Session lifecycle, expiration, revocation

## Design Principles

1. **Geographic independence** — both devices connect to the relay independently
2. **Secure communication** — WSS/TLS 1.3 for all transport
3. **Bidirectional** — full-duplex messaging (messages, events, acknowledgements)
4. **Transport abstraction** — the assistant core knows only a connection interface

## Phases

| Phase | Description |
|-------|-------------|
| 1 | Local communication (Android ⇄ Debian on same network) |
| 2 | WebSocket transport |
| 3 | TLS authentication and encryption |
| 4 | Relay server for cross-network communication |
| 5 | Identity, sessions, pairing, tokens |
| 6 | Global production communication |
