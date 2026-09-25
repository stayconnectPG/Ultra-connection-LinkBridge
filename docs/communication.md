# Communication Layer

## HTTPS

HTTPS is used for stateless operations:

- **Authentication** — exchanging credentials for session tokens
- **Device registration** — onboarding new devices into the system
- **Device management** — listing, querying, and revoking devices
- **Session management** — creating and tearing down sessions

All HTTPS traffic runs over TLS 1.3. The relay server terminates TLS.

## WebSocket (WSS)

WebSocket Secure is used for the persistent, bidirectional communication channel
between each device and the relay.

```
Android  ⇄  WSS  ⇄  Relay  ⇄  WSS  ⇄  Debian
```

### Lifecycle

1. **Connect** — device opens WSS connection to relay
2. **Authenticate** — device sends JWT/access token; relay validates
3. **Identify** — relay confirms device identity and type
4. **Route** — relay binds the connection to a session/pairing
5. **Forward** — messages are forwarded between paired peers
6. **Disconnect** — connection closed; session marked inactive

## Local Communication (Phase 1)

In early development, devices on the same network may communicate directly
over TCP or WebSocket before TLS and relay infrastructure are introduced.
