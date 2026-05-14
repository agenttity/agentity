# Agentity Protocol

**Open source cryptographic identity protocol for AI agents.**

Every AI agent receives a W3C-compatible DID (`did:agentity`), a signed Agent Identity Document (AID) with Ed25519 keys, and a scope system validated against service provider manifests. Delegation chains, revocation cascades, anti-replay nonces — designed for LangChain, CrewAI, Vercel AI SDK, MCP, A2A, and any HTTP infrastructure.

```
did:agentity:agent:7Xj3mK9pL2nQ8vRtYwZb4cFdHsNaEgUi
```

---

## Architecture

The protocol is organized in **four layers**, from cryptographic primitives up to user-facing tools:

```
═══════════════════════════════════════════════════════════════════
                     USER INTERFACES
═══════════════════════════════════════════════════════════════════

  ┌──────────────────────┐    ┌──────────────────────────────────┐
  │     agentity-cli     │    │      agentity-inspector          │
  │  create · inspect    │    │   Next.js dashboard · WebSocket  │
  │  verify · sign       │    │   agent list · live revocations  │
  │  manifest            │    │   scope explorer                 │
  └──────────┬───────────┘    └──────────────┬───────────────────┘
             │                               │
             │          HTTP / WS            │
             ▼                               ▼
═══════════════════════════════════════════════════════════════════
                     SERVICE LAYER
═══════════════════════════════════════════════════════════════════

  ┌──────────────────────────────────────────────────────────────┐
  │                   agentity-registry                         │
  │   FastAPI · PostgreSQL · Redis                               │
  │   POST /register · GET /did/{did} · POST /revoke · WS /ws   │
  │   lookup · status · cascade revocation · audit log           │
  └───────┬────────────────────────────────────┬─────────────────┘
          │                                    │
          │   HTTP + Agentity-Token header     │
          ▼                                    ▼
  ┌─────────────────┐                ┌──────────────────────────┐
  │  agentity-sdk   │                │  agentity-middleware     │
  │  Python / TS    │◄──────────────►│  FastAPI / Express       │
  │                 │                │  automatic token verify  │
  │  + agentity-mcp │                │                          │
  │  + agentity-a2a │                │                          │
  └────────┬────────┘                └──────────────────────────┘
           │
           │    builds on
           ▼
═══════════════════════════════════════════════════════════════════
                    IDENTITY LAYER
═══════════════════════════════════════════════════════════════════

  ┌──────────────────────────────────────────────────────────────┐
  │                   agentity-sdk                               │
  │  AgentKeyPair · AgentIdentity · RequestSigner · RequestVer.  │
  │  ProviderManifest · Scope matching · Delegation chain        │
  │  LangChain mixin · Vercel AI SDK                             │
  └────────┬──────────────────────────────────┬──────────────────┘
           │                                  │
           ▼                                  ▼
═══════════════════════════════════════════════════════════════════
                      CORE LAYER
═══════════════════════════════════════════════════════════════════

  ┌──────────────────────────────────────────────────────────────┐
  │                   agentity-core (Rust)                       │
  │  Ed25519 keypairs · SHA-256 fingerprints · base58 DIDs       │
  │  AgentIdentityDocument · Proof signing/verification          │
  │  Token encoding · Scope wildcard matching                    │
  └──────────────────────────────────────────────────────────────┘
```

### Request flow

```
Agent SDK             Middleware              Registry
    │                     │                      │
    │  1. Sign request    │                      │
    │  with Agent-Token   │                      │
    │────────────────────►│                      │
    │                     │  2. Verify token     │
    │                     │  + nonce + timestamp │
    │                     │──────────────────────►
    │                     │  3. Check status     │
    │                     │◄──────────────────────│
    │                     │  4. Valid: forward   │
    │                     │                      │
    │  5. Response        │                      │
    │◄────────────────────│                      │
```

---

## Packages

| Package | Language | Description |
|---------|----------|-------------|
| `agentity-core` | Rust | Ed25519 keys, DID generation, AID signing/verification, scope matching |
| `agentity-spec` | Markdown | RFC protocol specification (SPEC.md) |
| `agentity-sdk-python` | Python | AgentKeyPair, AgentIdentity, RequestSigner, LangChain/CrewAI integration |
| `agentity-sdk-ts` | TypeScript | Full parity SDK for Node.js/Next.js, Vercel AI SDK compatible |
| `agentity-registry` | Python | FastAPI REST registry: register, lookup, revoke (cascade), audit log, WebSocket |
| `agentity-middleware` | Python/TS | FastAPI middleware + Express middleware (automatic token verification) |
| `agentity-cli` | Python | CLI: `create`, `inspect`, `verify`, `sign`, `manifest` |
| `agentity-mcp` | Python | MCP Anthropic protocol plugin (signs tool calls) |
| `agentity-a2a` | Python | A2A Google protocol plugin (signs agent-to-agent requests) |
| `agentity-inspector` | TypeScript | Next.js dashboard — real-time agent list + WebSocket revocations |
| `agentity-manifest-gen` | TypeScript | Provider manifest JSON generator |

---

## Quick Start

### 1. Create an agent identity

```python
# Python
from agentity_sdk import AgentKeyPair

kp = AgentKeyPair()
aid = kp.create_identity(
    owner_did="did:agentity:human:alice",
    scopes=["stripe:payments:read", "calendar:events:write"],
    ttl_days=30,
)
print(f"DID: {aid.did}")
print(f"Signature valid: {aid.verify_signature()}")
```

```typescript
// TypeScript
import { AgentKeyPair, createIdentity } from '@agentity/sdk';

const kp = await AgentKeyPair.generate();
const aid = await createIdentity(kp, 'did:agentity:human:alice',
  ['stripe:payments:read'], 30);
console.log(`DID: ${aid.did}`);
```

### 2. Sign a request

```python
from agentity_sdk import RequestSigner

signer = RequestSigner(kp, aid)
headers = signer.sign_request("GET", "/api/v1/payments")
# headers = {
#   "Agentity-Token": "<base64url(AID)>.<base64url(signature)>",
#   "Agentity-Nonce": "<uuid-v4>",
#   "Agentity-Timestamp": "<ISO-8601>",
# }
```

### 3. Verify on the server side

```python
from agentity_sdk import RequestVerifier

verifier = RequestVerifier()
used_nonces = set()
aid = verifier.verify_request(headers, "GET", "/api/v1/payments",
    used_nonces=used_nonces)
# Raises PermissionError on invalid/malformed/replayed requests
```

### 4. Or use the middleware (automatic)

```python
# FastAPI
from fastapi import FastAPI
from agentity_middleware_python import AgentityMiddleware

app = FastAPI()
app.add_middleware(AgentityMiddleware, registry_url="http://localhost:8000")
```

```typescript
// Express
import { agentityMiddleware } from '@agentity/middleware-express';
app.use(agentityMiddleware({ registryUrl: 'http://localhost:8000' }));
```

---

## CLI

```bash
# Create a new agent identity
python -m agentity_cli create --owner "did:agentity:human:alice" --scope "api:read" --scope "api:write"

# Inspect an AID file
python -m agentity_cli inspect identity.json

# Verify an AID signature
python -m agentity_cli verify identity.json

# Sign a request
python -m agentity_cli sign --key identity.json --url https://api.example.com/data --method GET

# Generate a provider manifest
python -m agentity_cli manifest --name "My API" --scopes "data:read,data:write"
```

---

## Registry API

```bash
# Start (in-memory, no dependencies)
uvicorn agentity_registry.main:app --port 8000

# Start (PostgreSQL + Redis)
AGENTITY_STORE=postgres DATABASE_URL=postgresql+asyncpg://... uvicorn agentity_registry.main:app

# Or full stack with Docker
docker compose up -d
```

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check + active store type |
| `POST` | `/register` | Register an AID |
| `GET` | `/did/{did}` | Get full AID document |
| `GET` | `/did/{did}/status` | Get AID status (active/revoked/expired) |
| `POST` | `/revoke` | Revoke an AID (optional cascade) |
| `GET` | `/audit/{did}` | Get audit log for a DID |
| `GET` | `/agents` | List all registered agents |
| `WS` | `/ws` | WebSocket — real-time revocation events |

### Stack modes

| `AGENTITY_STORE` | Storage | Dependencies |
|---|---|---|
| `memory` (default) | In-memory dict | None |
| `postgres` | PostgreSQL + Redis | `docker compose up` |

---

## Architecture decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Crypto | Ed25519 | Fast, short keys (32 B), W3C standard |
| DID method | `did:agentity` | W3C compatible, self-verifying fingerprint |
| Token format | `<base64(AID)>.<base64(sig)>` | Self-contained, no lookup needed |
| Anti-replay | Nonce + timestamp (5 min window) | Stateless client, Redis TTL server-side |
| Core language | Rust | Max performance, WASM-ready for edge |
| SDK languages | Python + TypeScript | LangChain/CrewAI + Vercel AI/Next.js ecosystems |
| Registry store | Pluggable (memory → postgres) | Dev to production without code changes |
| License | Apache 2.0 | Patent protection, commercial-friendly |

---

## Development

```bash
# Clone
git clone https://github.com/agenttity/agentity.git
cd agentity

# Rust core
. "$HOME/.cargo/env"
cargo test --workspace          # 17 tests

# Python
python3 -m venv .venv && source .venv/bin/activate
pip install -e packages/agentity-sdk-python[dev]
pip install -e packages/agentity-registry[dev]
pip install -e packages/agentity-middleware/python[dev]
pip install -e packages/agentity-cli[dev]
pip install -e packages/agentity-mcp[dev]
pip install -e packages/agentity-a2a[dev]
pytest packages/agentity-sdk-python/tests
pytest packages/agentity-registry/agentity_registry/tests
pytest packages/agentity-middleware/python/tests
pytest packages/agentity-mcp/tests
pytest packages/agentity-a2a/tests
pytest packages/agentity-cli/tests   # 33 Python tests total

# TypeScript
pnpm install
pnpm build
pnpm test                           # 19 TS tests total

# All at once
cargo test --workspace && pnpm test && pytest ... # 69 tests total
```

---

## License

Apache 2.0 — see [LICENSE](LICENSE).
