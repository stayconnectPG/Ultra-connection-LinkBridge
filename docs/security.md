# Security

Security is a first-class concern in this architecture. The following measures
are required:

## TLS

- All HTTPS and WSS connections use **TLS 1.3**
- Certificates issued by a trusted CA or self-signed with proper distribution
- Relay server terminates TLS; no plain-text traffic

## Authentication

- Devices authenticate using JWT or opaque tokens
- Tokens have expiration and can be revoked
- Credentials are never stored in plaintext

## Authorization

- Relay enforces that a device may only communicate with its paired peer
- Session-based access control: only paired device IDs can exchange messages

## Device Identity

- Each device has a unique `device_id`
- Device type: `android`, `server` (Debian), or `assistant`
- Device registration requires approval or pairing code

## Token Management

- **Session tokens** — short-lived, used for WebSocket authentication
- **Refresh tokens** — for obtaining new session tokens
- **Revocation** — tokens can be invalidated server-side

## Session Security

- Sessions expire after a configurable TTL (default: 30 minutes)
- Inactivity causes automatic session teardown
- Relay does not persist message content

## Input Validation

- All inbound messages are validated against a schema
- Message rate limiting prevents abuse
- Large payloads are rejected

## Audit Logging

- All connection attempts (success and failure) are logged
- Authentication events are logged
- Session lifecycle events are logged

## Credential Storage

- Debian: credentials stored in OS key store (e.g., `keyring`)
- Android: credentials stored in Android Keystore
- Relay: tokens stored hashed; raw tokens never persisted
