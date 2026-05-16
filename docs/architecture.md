# Architecture

## Layered design

```
┌─────────────────────────────────────┐
│         USER INTERFACES             │
│  agentity-cli  agentity-inspector   │
│  agentity-website                   │
├─────────────────────────────────────┤
│         SERVICE LAYER               │
│  agentity-registry (FastAPI)        │
│  agentity-auth (OIDC)               │
├─────────────────────────────────────┤
│         MIDDLEWARE                  │
│  agentity-middleware-python         │
│  agentity-middleware-express        │
├─────────────────────────────────────┤
│         SDK                         │
│  agentity-sdk-python                │
│  agentity-sdk-ts                    │
│  agentity-mcp / agentity-a2a        │
├─────────────────────────────────────┤
│         CORE                        │
│  agentity-core (Rust)               │
│  Ed25519 · SHA-256 · base58         │
└─────────────────────────────────────┘
```

## Request flow

```
Agent SDK             Middleware              Registry
    │                     │                      │
    │  1. Sign request    │                      │
    │  with Agentity-Token│                      │
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

## Package roles

| Layer | Package | Role |
|-------|---------|------|
| Core | `agentity-core` | Crypto primitives: Ed25519, DID generation, AID signing, scope matching |
| SDK | `agentity-sdk-python` | Python: identity creation, request signing/verification, LangChain integration |
| SDK | `agentity-sdk-ts` | TypeScript: same API, Vercel AI SDK compatible |
| Plugin | `agentity-mcp` | Wrap MCP servers with identity |
| Plugin | `agentity-a2a` | Sign agent-to-agent requests |
| Middleware | `agentity-middleware-python` | FastAPI automatic token verification |
| Middleware | `agentity-middleware-express` | Express automatic token verification |
| Service | `agentity-registry` | DID registration, lookup, revocation, audit, WebSocket |
| Service | `agentity-auth` | OIDC login for owner verification |
| Service | `agentity-evm` | EVM cross-registry bridge |
| UI | `agentity-cli` | Command-line tool |
| UI | `agentity-inspector` | Web dashboard with live revocations |
| UI | `agentity-website` | Landing page |

## DID method

Format: `did:agentity:{type}:{base58-fingerprint}`

| Type | Example |
|------|---------|
| `agent` | `did:agentity:agent:7Xj3mK9pL2nQ8v...` |
| `human` | `did:agentity:human:aBcDeFgHiJkLm...` |
| `org` | `did:agentity:org:XyZ123AbC456...` |
| `provider` | `did:agentity:provider:Stripe9f8e...` |

The fingerprint is SHA-256 of the Ed25519 public key, encoded in base58.

## Store modes

| Mode | Storage | Dependencies | Use case |
|------|---------|--------------|----------|
| `memory` | In-memory dict | None | Dev, testing |
| `postgres` | PostgreSQL + Redis | Docker Compose | Production |

Select via `AGENTITY_STORE` env var.

## Cross-registry (EVM)

The optional EVM bridge publishes DID events on-chain:

- `register()` → `DIDRegistered` event
- `revoke()` → `DIDRevoked` event
- `rotate()` → `DIDRotated` event

Read-only verification works across any registry instance using the contract's `getStatus()` and `getFingerprint()` functions.

## Security model

See the [Security guide](security.md) for details on:
- Key rotation (version+1, previousAid link)
- Anti-replay (nonce + 5 min timestamp window)
- Delegation chains (max 10 levels, cascade revocation)
- OIDC owner verification
- Rate limiting (Redis, per-DID)
- Signed audit log (HMAC-SHA256)
