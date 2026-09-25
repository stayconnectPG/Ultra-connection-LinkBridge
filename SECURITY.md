# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue:

1. **Do NOT** open a public GitHub issue.
2. **Do NOT** commit any fix to a public branch.
3. Email your findings to the maintainers with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact assessment
   - Proposed fix (if any)

## Security Architecture

The LinkBridge system implements defense in depth:

### TLS
- All transport uses TLS 1.3 (WSS/HTTPS)
- No plaintext communication over public networks

### Authentication
- JWT-based token system with expiration
- Short-lived session tokens for WebSocket connections
- Device registration requires pairing approval

### Authorization
- Only paired devices can exchange messages
- Relay never acts as a man-in-the-middle for message content

### Credential Storage
- Debian: OS keyring (`keyring` library)
- Android: Android Keystore
- Relay: Tokens are hashed; raw tokens are never persisted

### Input Validation
- All WebSocket messages validated against envelope schema
- Rate limiting prevents abuse
- Malformed payloads are rejected

### Audit Logging
- All connection attempts logged
- Authentication events recorded
- Session lifecycle events tracked

## Disclosure Policy

- We will acknowledge your report within 48 hours
- We will provide a fix within 7 days for critical issues
- We will credit you in the release notes (unless you prefer anonymity)
