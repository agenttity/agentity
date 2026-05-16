# Registry API Reference

## Start the registry

```bash
# In-memory (dev, no deps)
uvicorn agentity_registry.main:app --port 8000

# With OIDC
cp .env.example .env
uvicorn agentity_registry.main:app --port 8765

# Production (PostgreSQL + Redis)
AGENTITY_STORE=postgres docker compose up -d
```

## Endpoints

### Health

```
GET /health
```

Response:
```json
{
  "status": "ok",
  "store": "memory",
  "auth": true,
  "uptime": 3600
}
```

### Register an AID

```
POST /register
Content-Type: application/json

{
  "did": "did:agentity:agent:7Xj3mK9pL2nQ8vRtYwZb4cFdHsNaEgUi",
  "aid_json": "{...}",
  "public_key_b64": "Base64urlEncodedPublicKey",
  "scopes": ["stripe:payments:read"],
  "owner_did": "did:agentity:human:alice",
  "ttl_days": 30
}
```

Response: `200` with `{"did": "...", "status": "active", "created": "..."}`

### Lookup DID

```
GET /did/{did}
```

Returns the full AID JSON document.

### Check status

```
GET /did/{did}/status
```

Response:
```json
{ "did": "...", "status": "active", "updatedAt": "2026-05-08T12:00:00Z" }
```

### List agents

```
GET /agents
```

Returns `AgentInfo[]` — all registered agents with DID, status, owner, scopes, timestamps.

### Revoke

```
POST /revoke
Content-Type: application/json

{
  "did": "did:agentity:agent:7Xj3mK9pL2nQ8vRtYwZb4cFdHsNaEgUi",
  "reason": "Compromised key",
  "cascade": true
}
```

If `cascade: true`, all descendants are also revoked.

### Audit log

```
GET /audit                    # All entries
GET /audit/{did}              # Entries for a specific DID
GET /audit/{did}/verify?signature=&event=&timestamp=  # Verify entry
```

Audit entries are HMAC-SHA256 signed for non-repudiation.

### WebSocket

```
WS /ws
```

Real-time events:
```json
{ "type": "created",    "did": "...", "timestamp": "..." }
{ "type": "revocation", "did": "...", "timestamp": "..." }
```

### OIDC endpoints (if auth mounted)

```
GET /auth/login/{provider}       # Redirect to OAuth2
GET /auth/callback/{provider}    # Exchange code for session
GET /auth/session/{token}        # Get owner info
GET /auth/me                     # Current owner from Agentity-Session header
POST /auth/register-verified     # Verify owner_did matches session
```

Providers: `google`, `github`, `apple`, `microsoft`

## Headers

| Header | Direction | Description |
|--------|-----------|-------------|
| `Agentity-Token` | Request | Signed AID token |
| `Agentity-Nonce` | Request | UUID v4 anti-replay |
| `Agentity-Timestamp` | Request | ISO-8601 timestamp |
| `Agentity-Session` | Request | OIDC session token |
| `X-RateLimit-Remaining` | Response | Remaining requests in window |
| `X-Agent-DID` | Request | Agent DID for rate limiting |

## HTTP status codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Malformed request |
| 401 | Missing or invalid token |
| 403 | Signature invalid, expired, revoked, or insufficient scope |
| 404 | DID not found |
| 429 | Rate limit exceeded |
