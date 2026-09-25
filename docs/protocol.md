# Communication Protocol

## Transport

- **HTTPS** — used for auth, registration, and management operations
- **WebSocket Secure (WSS)** — used for persistent bidirectional real-time messaging

## HTTPS Endpoints

```
POST /auth              Authenticate and obtain session token
POST /devices/register  Register a new device
GET  /devices           List registered devices
GET  /status            Health check
POST /session           Create a new session
```

## WebSocket Messages

All WebSocket messages are JSON-encoded.

### Message Envelope

```json
{
  "type": "message_type",
  "payload": {},
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Message Types

| Type | Direction | Description |
|------|-----------|-------------|
| `command` | Both | A command to be executed |
| `response` | Both | Reply to a command |
| `event` | Both | Unsolicited event emission |
| `ack` | Both | Acknowledgement of received message |
| `ping` | Both | Liveness probe |
| `pong` | Both | Liveness response |

## Bidirectional Flow

```
ANDROID                         DEBIAN

  │                              │
  │────── message ──────────────►│
  │                              │
  │◄────── response ─────────────│
  │                              │
  │◄────── event ────────────────│
  │                              │
  │────── acknowledgement ──────►│
  │                              │
```
