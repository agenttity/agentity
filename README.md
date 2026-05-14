# Agentity Protocol

**Open source cryptographic identity protocol for AI agents.**

Every AI agent gets a W3C-compatible DID, a signed Agent Identity Document (AID),
and a scope system validated against service provider manifests.

## Packages

| Package | Language | Description |
|---------|----------|-------------|
| `agentity-spec` | Markdown | RFC protocol specification |
| `agentity-core` | Rust | Crypto primitives, DID, AID |
| `agentity-sdk-python` | Python | SDK for Python (LangChain, CrewAI) |
| `agentity-sdk-ts` | TypeScript | SDK for TypeScript (Vercel AI SDK, Next.js) |
| `agentity-registry` | Python | REST registry API (FastAPI) |
| `agentity-middleware` | Python/TS | HTTP middleware (FastAPI, Express) |
| `agentity-cli` | Python | CLI tool |
| `agentity-mcp` | Python | MCP Anthropic protocol plugin |
| `agentity-a2a` | Python | A2A Google protocol plugin |
| `agentity-inspector` | TypeScript | Next.js dashboard UI |
| `agentity-manifest-gen` | TypeScript | Provider manifest generator |

## Quick Start

```bash
# Python SDK
pip install agentity-sdk-python

# TypeScript SDK
pnpm add @agentity/sdk

# CLI
pnpm add -g @agentity/cli
agentity create --owner "did:agentity:human:alice" --scope "stripe:payments:read"
```

## License

Apache 2.0
