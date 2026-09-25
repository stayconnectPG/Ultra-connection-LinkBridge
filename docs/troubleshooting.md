# Troubleshooting

## Connection Issues

### Device cannot connect to relay

1. Verify relay server is running: `ps aux | grep uvicorn`
2. Check firewall: `ufw status` or cloud security groups
3. Confirm TLS certificate is valid and not expired
4. Test connectivity: `openssl s_client -connect relay.example.com:443`

### WebSocket disconnects immediately

1. Check server logs for authentication errors
2. Verify session token is valid and not expired
3. Ensure device IDs match the pairing record

### Authentication failures

1. Confirm JWT secret is set and consistent across services
2. Check token expiration time
3. Verify device was properly registered

## Logging

### Relay logs

```bash
journalctl -u relay-server -f
```

### Debian assistant logs

```bash
# If running with uvicorn
uvicorn debian.api.main:app --log-level debug
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `403 Forbidden` | Invalid or expired token | Re-authenticate |
| `404 Device not found` | Device not registered | Register device first |
| `409 Conflict` | Pairing already exists | Revoke and re-pair |
| `429 Too Many Requests` | Rate limited | Back off and retry |

## Phase Checklist

If features are not working, verify you have completed earlier phases:

1. **Phase 1** — Local communication established
2. **Phase 2** — WebSocket channels working
3. **Phase 3** — TLS certificates valid
4. **Phase 4** — Relay server reachable from both networks
5. **Phase 5** — Device registered and paired
6. **Phase 6** — Global DNS/ingress configured
