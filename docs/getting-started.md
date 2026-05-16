# Getting Started

## Install

### Python

```bash
pip install agentity-sdk-python agentity-registry agentity-auth
```

### TypeScript

```bash
pnpm add @agentity/sdk @agentity/middleware-express
```

## 1. Create an agent identity

```python
from agentity_sdk import AgentKeyPair

kp = AgentKeyPair()
aid = kp.create_identity(
    owner_did="did:agentity:human:alice",
    scopes=["stripe:payments:read", "calendar:events:write"],
    ttl_days=30,
)
print(f"DID: {aid.did}")
```

```typescript
import { AgentKeyPair, createIdentity } from '@agentity/sdk';

const kp = await AgentKeyPair.generate();
const aid = await createIdentity(kp, 'did:agentity:human:alice',
  ['stripe:payments:read'], 30);
```

## 2. Sign a request

```python
from agentity_sdk import RequestSigner

signer = RequestSigner(kp, aid)
headers = signer.sign_request("GET", "/api/v1/payments")
# {
#   "Agentity-Token": "<base64(AID)>.<base64(sig)>",
#   "Agentity-Nonce": "<uuid-v4>",
#   "Agentity-Timestamp": "<ISO-8601>",
# }
```

## 3. Verify on the server

```python
from agentity_sdk import RequestVerifier

verifier = RequestVerifier()
used_nonces = set()
aid = verifier.verify_request(headers, "GET", "/api/v1/payments",
    used_nonces=used_nonces)
```

## 4. Use middleware (automatic)

```python
from fastapi import FastAPI
from agentity_middleware_python import AgentityMiddleware

app = FastAPI()
app.add_middleware(AgentityMiddleware, registry_url="http://localhost:8000")
```

```typescript
import { agentityMiddleware } from '@agentity/middleware-express';
app.use(agentityMiddleware({ registryUrl: 'http://localhost:8000' }));
```

## 5. Register with the registry

```bash
uvicorn agentity_registry.main:app --port 8000
```

```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"did": "did:agentity:agent:...", "aid_json": "{...}", "public_key_b64": "...", "scopes": ["..."], "owner_did": "did:agentity:human:alice", "ttl_days": 30}'
```

## Next steps

- [Architecture overview](architecture.md)
- [Registry API reference](registry-api.md)
- [CLI commands](cli.md)
- [Deployment guide](deployment.md)
