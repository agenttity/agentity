# agentity-registry

**FastAPI REST registry for the Agentity Protocol.**
Register agent identities, lookup DID status, revoke tokens, stream events via WebSocket — with OIDC auth, rate limiting, and signed audit logs.

## Installation

```bash
pip install agentity-registry
```

## Quick start

```bash
# In-memory (no dependencies)
uvicorn agentity_registry.main:app --port 8000

# With OIDC auth
cp .env.example .env   # fill in Google/GitHub credentials
uvicorn agentity_registry.main:app --port 8765

# Production (PostgreSQL + Redis)
AGENTITY_STORE=postgres docker compose up -d
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check + store + auth info |
| `POST` | `/register` | Register an agent AID |
| `GET` | `/did/{did}` | Get full AID document |
| `GET` | `/did/{did}/status` | Get AID status (active/revoked/expired) |
| `POST` | `/revoke` | Revoke an AID (optional cascade) |
| `GET` | `/agents` | List all registered agents |
| `GET` | `/audit` | Get all audit log entries |
| `GET` | `/audit/{did}` | Get audit log for a specific DID |
| `GET` | `/audit/{did}/verify` | Verify an audit entry signature |
| `WS` | `/ws` | Real-time event stream (created/revoked) |

### Authentication endpoints (if OIDC enabled)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/auth/login/{provider}` | OIDC login (google, github, apple, microsoft) |
| `GET` | `/auth/callback/{provider}` | OIDC callback |
| `GET` | `/auth/session/{token}` | Get verified owner session |

## Configuration

| Env var | Default | Description |
|---------|---------|-------------|
| `AGENTITY_STORE` | `memory` | `memory` or `postgres` |
| `REDIS_URL` | `redis://localhost:6379` | Redis for rate limiting |
| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection |
| `AGENTITY_EVM_RPC_URL` | — | Optional EVM bridge RPC |

### OIDC env vars

`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `APPLE_CLIENT_ID`, `APPLE_CLIENT_SECRET`, `MICROSOFT_CLIENT_ID`, `MICROSOFT_CLIENT_SECRET`

## Features

- **Pluggable storage** — InMemoryStore (dev) / PostgresStore (prod)
- **Rate limiting** — Redis-backed, 100 req/min per DID, `X-RateLimit-Remaining` header
- **Signed audit log** — HMAC-SHA256 on each entry, verifiable
- **WebSocket broadcasts** — Real-time revocation events
- **EVM bridge** — Optional on-chain DID registration (via `agentity-evm`)

## Tests

```bash
pip install -e .[dev]
pytest agentity_registry/tests/
```

License: Apache 2.0
