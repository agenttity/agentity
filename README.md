# Agentity Protocol

[![CI](https://github.com/agenttity/agentity/actions/workflows/ci.yml/badge.svg)](https://github.com/agenttity/agentity/actions/workflows/ci.yml)
[![npm](https://img.shields.io/npm/v/@agentity/sdk)](https://www.npmjs.com/package/@agentity/sdk)
[![PyPI](https://img.shields.io/pypi/v/agentity-sdk-python)](https://pypi.org/project/agentity-sdk-python/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/agenttity/agentity/blob/main/LICENSE)

**EN** — Open source cryptographic identity protocol for AI agents.  
**FR** — Protocole open source d'identité cryptographique pour agents IA.

Every AI agent receives a W3C-compatible DID (`did:agentity`), a signed Agent Identity Document (AID) with Ed25519 keys, and a scope system validated against service provider manifests. Delegation chains, revocation cascades, anti-replay nonces, OIDC owner verification, rate limiting, key rotation, and signed audit logs — designed for LangChain, CrewAI, Vercel AI SDK, MCP, A2A, and any HTTP infrastructure.

> **FR** — Chaque agent IA reçoit un DID compatible W3C, un document d'identité signé (AID) avec clés Ed25519, et un système de scopes validés contre les manifestes des fournisseurs de services. Chaînes de délégation, révocations en cascade, anti-replay, vérification du propriétaire via OIDC, rate limiting, rotation de clés et logs d'audit signés — conçu pour LangChain, CrewAI, Vercel AI SDK, MCP, A2A et toute infrastructure HTTP.

```
did:agentity:agent:7Xj3mK9pL2nQ8vRtYwZb4cFdHsNaEgUi
```

---

## Architecture

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
  │   OIDC auth (/auth/login) · rate limiting · signed audit log │
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
  +  + agentity-auth│                │                          │
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
  │  Key rotation · LangChain mixin · Vercel AI SDK              │
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
| `agentity-sdk-python` | Python | AgentKeyPair, AgentIdentity, RequestSigner, LangChain/CrewAI integration, key rotation |
| `agentity-sdk-ts` | TypeScript | Full parity SDK for Node.js/Next.js, Vercel AI SDK compatible, key rotation |
| `agentity-registry` | Python | FastAPI REST registry: register, lookup, revoke (cascade), audit log, WebSocket, rate limiting |
| `agentity-auth` | Python | OIDC authentication: login via Google, GitHub, Apple, Microsoft |
| `agentity-middleware` | Python/TS | FastAPI middleware + Express middleware (automatic token verification) |
| `agentity-cli` | Python | CLI: `create`, `inspect`, `verify`, `sign`, `manifest` |
| `agentity-mcp` | Python | MCP Anthropic protocol plugin (signs tool calls) |
| `agentity-a2a` | Python | A2A Google protocol plugin (signs agent-to-agent requests) |
| `agentity-inspector` | TypeScript | Next.js dashboard — real-time agent list + WebSocket revocations |
| `agentity-manifest-gen` | TypeScript | Provider manifest JSON generator |

---

## Security features

| Feature | Package | Description |
|---------|---------|-------------|
| **OIDC auth** | `agentity-auth` | Login via Google/GitHub/Apple/Microsoft — verified `owner_did` |
| **Rate limiting** | `agentity-registry` | Redis-based rate limit per DID (configurable window/max) |
| **Key rotation** | SDKs | `rotate()` generates new keypair, `version+1`, links previous AID |
| **Signed audit log** | `agentity-registry` | HMAC-SHA256 signature on each audit entry, verifiable via `/audit/{did}/verify` |
| **Anti-replay** | SDKs | UUID nonce + 5 min timestamp window |
| **Delegation chain** | SDKs | Max 10 levels, child scopes ⊆ parent scopes, cascade revocation |

---

## Quick Start

### 1. Install

```bash
# Python
pip install agentity-sdk-python agentity-registry agentity-auth

# TypeScript
pnpm add @agentity/sdk
```

### 2. Create an agent identity

```python
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
import { AgentKeyPair, createIdentity } from '@agentity/sdk';

const kp = await AgentKeyPair.generate();
const aid = await createIdentity(kp, 'did:agentity:human:alice',
  ['stripe:payments:read'], 30);
console.log(`DID: ${aid.did}`);
```

### 3. Sign a request

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

### 4. Verify on the server side

```python
from agentity_sdk import RequestVerifier

verifier = RequestVerifier()
used_nonces = set()
aid = verifier.verify_request(headers, "GET", "/api/v1/payments",
    used_nonces=used_nonces)
# Raises PermissionError on invalid/malformed/replayed requests
```

### 5. Or use the middleware (automatic)

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

### 6. Rotate keys

```python
# Python
new_aid = kp.rotate(aid, ttl_days=90)
print(f"New version: {new_aid.version}")  # 2
print(f"Previous AID: {new_aid.previousAid}")
```

```typescript
// TypeScript
import { rotateIdentity } from '@agentity/sdk';
const newAid = await rotateIdentity(aid, kp);
```

---

## CLI

```bash
# Create a new agent identity
python -m agentity_cli create --owner "did:agentity:human:alice" \
  --scope "api:read" --scope "api:write" --output agent.json

# Inspect an AID file
python -m agentity_cli inspect agent.json

# Verify an AID signature
python -m agentity_cli verify agent.json

# Sign a request
python -m agentity_cli sign --key agent.json \
  --url https://api.example.com/data --method GET

# Generate a provider manifest
python -m agentity_cli manifest --name "My API" --scopes "data:read,data:write"
```

---

## Registry API

```bash
# Start (in-memory, no dependencies)
uvicorn agentity_registry.main:app --port 8000

# Start with OIDC auth (Google + GitHub)
cp .env.example .env   # fill in credentials
uvicorn agentity_registry.main:app --port 8765

# Start (PostgreSQL + Redis)
AGENTITY_STORE=postgres docker compose up -d
```

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check + active store type + auth status |
| `GET` | `/auth/login/{provider}` | OIDC login (google, github, apple, microsoft) |
| `GET` | `/auth/callback/{provider}` | OIDC callback |
| `GET` | `/auth/session/{token}` | Get verified owner session |
| `POST` | `/register` | Register an AID |
| `GET` | `/did/{did}` | Get full AID document |
| `GET` | `/did/{did}/status` | Get AID status (active/revoked/expired) |
| `POST` | `/revoke` | Revoke an AID (optional cascade) |
| `GET` | `/audit/{did}` | Get signed audit log for a DID |
| `GET` | `/audit/{did}/verify` | Verify audit entry signature |
| `GET` | `/agents` | List all registered agents |
| `WS` | `/ws` | WebSocket — real-time revocation events |

Headers rate limiting retourne `X-RateLimit-Remaining` sur chaque réponse.

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
| OIDC | Google, GitHub, Apple, MS | Verified owner_human_ → trust chain |
| Rate limiting | Redis per-DID | Configurable window + max requests |
| Audit log | HMAC-SHA256 signed | Non-repudiation, verifiable |
| Key rotation | `version+1`, `previousAid` link | Compromised key mitigation |
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
cargo test --workspace                            # 17 tests

# Python
python3 -m venv .venv && source .venv/bin/activate
pip install -e packages/agentity-sdk-python[dev]
pip install -e packages/agentity-registry[dev]
pip install -e packages/agentity-auth[dev]
pip install -e packages/agentity-middleware/python[dev]
pip install -e packages/agentity-cli[dev]
pip install -e packages/agentity-mcp[dev]
pip install -e packages/agentity-a2a[dev]

pytest packages/agentity-sdk-python/tests          # 10 tests (incl. rotation)
pytest packages/agentity-registry/agentity_registry/tests  # 6 tests
pytest packages/agentity-auth/agentity_auth/tests  # 5 tests
pytest packages/agentity-middleware/python/tests   # 6 tests
pytest packages/agentity-mcp/tests                 # 4 tests
pytest packages/agentity-a2a/tests                 # 4 tests
pytest packages/agentity-cli/tests                 # 4 tests

# TypeScript
pnpm install --ignore-scripts
pnpm build
pnpm test                                          # 19 TS tests total

# All at once
cargo test --workspace && pnpm test && pytest ...  # 74 tests total
```

---

## License

Apache 2.0 — see [LICENSE](LICENSE).
