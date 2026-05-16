# agentity-middleware-python

**FastAPI middleware for the Agentity Protocol.**
Automatically verify Agentity-signed requests — extract agent identity, validate nonce and timestamp, check status via registry, and inject `request.state.agent_did` + `request.state.agent_scopes`.

## Installation

```bash
pip install agentity-middleware-python
```

## Usage

```python
from fastapi import FastAPI, Request
from agentity_middleware_python import AgentityMiddleware

app = FastAPI()

# Add middleware (optional registry check)
app.add_middleware(
    AgentityMiddleware,
    registry_url="http://localhost:8000",  # Optional: verify DID status
    tolerance_seconds=300,                  # Default: 5 min
)

@app.get("/api/data")
async def get_data(request: Request):
    # Verified agent info automatically injected
    agent_did = request.state.agent_did       # "did:agentity:agent:..."
    agent_scopes = request.state.agent_scopes  # ["stripe:payments:read", ...]
    return {"agent": agent_did, "scopes": agent_scopes}
```

## What it does

1. Extracts `Agentity-Token`, `Agentity-Nonce`, `Agentity-Timestamp` headers
2. Validates nonce uniqueness (anti-replay)
3. Checks timestamp is within tolerance window (default ±300s)
4. Decodes and verifies the Ed25519 AID signature
5. If `registry_url` is set, checks `GET /did/{did}/status` for active status
6. Injects `request.state.agent_did` and `request.state.agent_scopes`
7. Returns `400` (malformed), `401` (missing), or `403` (invalid/revoked) on failure

## Error responses

| Status | Condition |
|--------|-----------|
| 400 | Missing or malformed headers |
| 401 | Token not provided |
| 403 | Invalid signature, expired, revoked, or scope violation |

## Tests

```bash
pip install -e .[dev]
pytest ../tests/
```

License: Apache 2.0
