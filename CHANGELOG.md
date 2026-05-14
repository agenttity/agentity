# Changelog

## v0.1.0 — 2026-05-14

### Added
- `agentity-core` (Rust) — Ed25519 key generation, DID `did:agentity`, AID document with self-signature, scope matching with wildcards
- `agentity-sdk-python` — `AgentKeyPair`, `AgentIdentity`, `RequestSigner`, `RequestVerifier`, `ProviderManifest`, LangChain integration
- `agentity-sdk-ts` — TypeScript equivalent with `@noble/ed25519`, Vercel AI SDK compatible
- `agentity-registry` — FastAPI REST API: register, lookup, status, revoke (cascade), audit log, WebSocket real-time events
- `agentity-middleware` — FastAPI middleware (`AgentityMiddleware`) + Express middleware (`agentityMiddleware`)
- `agentity-cli` — `agentity create`, `inspect`, `verify`, `sign`, `manifest` commands
- `agentity-mcp` — MCP Anthropic protocol plugin wrapper
- `agentity-a2a` — A2A Google protocol plugin client
- `agentity-inspector` — Next.js 15 dashboard with WebSocket live revocations
- `agentity-manifest-gen` — Provider manifest JSON generator
- `agentity-spec` — Full RFC protocol specification
- `agentity-registry` — PostgreSQL + Redis store, `AGENTITY_STORE` env var, Docker Compose
- CI/CD — GitHub Actions workflows for Rust + Python + TypeScript
- E2E examples in Python and TypeScript
- License: Apache 2.0

### Published
- npm: `@agentity/sdk`, `@agentity/middleware-express`, `@agentity/manifest-gen`
- PyPI: `agentity-sdk-python`, `agentity-registry`, `agentity-middleware-python`, `agentity-mcp`

### Tests
- Rust: 17 tests
- Python: 33 tests (SDK + Registry + Middleware + MCP + A2A + CLI)
- TypeScript: 19 tests (SDK + Middleware + Manifest)
