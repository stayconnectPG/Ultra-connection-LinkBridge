# Authentication

## Device Registration

1. Device generates device ID and key pair
2. Device sends registration request to relay:
   ```
   POST /devices/register
   { "device_id": "android-001", "type": "android", "public_key": "..." }
   ```
3. Relay stores device metadata and returns registration token

## Pairing

1. One device is designated as initiator (typically Debian)
2. Initiator requests pairing code via HTTPS
3. Relay generates and returns a short-lived pairing code
4. Second device scans or enters the pairing code
5. Relay binds the two device IDs into a pairing record

## Session Creation

```
POST /session
{
  "device_id": "android-001",
  "paired_device_id": "debian-001"
}
```

Response:
```json
{
  "session_token": "eyJ...",
  "expires_at": "2024-01-01T00:30:00Z"
}
```

## WebSocket Authentication

When a device connects via WSS, it must present a valid session token:

```json
{
  "type": "auth",
  "token": "eyJ..."
}
```

The relay validates the token and, if valid, routes the connection to the
paired peer.
