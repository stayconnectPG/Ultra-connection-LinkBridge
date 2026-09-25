# Deployment

## Relay Server

The relay server is a Python FastAPI application. Deploy using:

- **Direct** — `uvicorn relay.gateway.main:app`
- **Docker** — see `scripts/setup_relay.sh`
- **Systemd** — service file provided

### Requirements

- Python 3.11+
- TLS certificate (Let's Encrypt or self-signed)
- Publicly accessible domain/port (443 for HTTPS/WSS)

## Debian Assistant

The Debian assistant runs locally on the host machine.

```bash
uvicorn debian.api.main:app --reload
```

## Android App

Build and deploy via Android Studio / Gradle:

```bash
cd android
./gradlew assembleDebug
```

## Configuration

Environment variables (all services):

| Variable | Description | Default |
|----------|-------------|---------|
| `RELAY_HOST` | Relay bind host | `0.0.0.0` |
| `RELAY_PORT` | Relay bind port | `8000` |
| `TLS_CERT` | Path to TLS certificate | |
| `TLS_KEY` | Path to TLS private key | |
| `JWT_SECRET` | JWT signing secret | |
| `SESSION_TTL` | Session lifetime (seconds) | `1800` |

## Production Checklist

- [ ] TLS 1.3 configured on relay
- [ ] HTTPS enforced (HTTP→HTTPS redirect)
- [ ] JWT secret rotated
- [ ] Firewall rules configured
- [ ] Logging and monitoring enabled
- [ ] Backup strategy for device registry
