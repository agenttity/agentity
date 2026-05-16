# Agentity Protocol — Documentation

[![CI](https://github.com/agenttity/agentity/actions/workflows/ci.yml/badge.svg)](https://github.com/agenttity/agentity/actions/workflows/ci.yml)
[![npm](https://img.shields.io/npm/v/@agentity/sdk)](https://www.npmjs.com/package/@agentity/sdk)
[![PyPI](https://img.shields.io/pypi/v/agentity-sdk-python)](https://pypi.org/project/agentity-sdk-python/)

Open source cryptographic identity protocol for AI agents. Every agent gets a verifiable DID (`did:agentity`), signed identity document, and scope-based access control.

## Quick links

| Guide | Description |
|-------|-------------|
| [Getting Started](getting-started.md) | Install, create identity, sign requests |
| [Architecture](architecture.md) | Layered design, packages, request flow |
| [Security](security.md) | Key rotation, anti-replay, delegation, OIDC |
| [Registry API](registry-api.md) | REST endpoints, WebSocket, rate limiting |
| [CLI Reference](cli.md) | `agentity create`, `inspect`, `verify`, `sign`, `manifest` |
| [Deployment](deployment.md) | Docker Compose, production config |
| [Development](development.md) | Build, test, lint — all 3 languages |

## Packages

| Package | Lang | Published |
|---------|------|-----------|
| `agentity-core` | Rust | GitHub |
| `agentity-sdk-python` | Python | [PyPI](https://pypi.org/project/agentity-sdk-python/) |
| `agentity-sdk-ts` | TypeScript | [npm](https://www.npmjs.com/package/@agentity/sdk) |
| `agentity-registry` | Python | [PyPI](https://pypi.org/project/agentity-registry/) |
| `agentity-auth` | Python | [PyPI](https://pypi.org/project/agentity-auth/) |
| `agentity-cli` | Python | [PyPI](https://pypi.org/project/agentity-cli/) |
| `agentity-middleware-python` | Python | [PyPI](https://pypi.org/project/agentity-middleware-python/) |
| `agentity-middleware-express` | TypeScript | [npm](https://www.npmjs.com/package/@agentity/middleware-express) |
| `agentity-mcp` | Python | [PyPI](https://pypi.org/project/agentity-mcp/) |
| `agentity-a2a` | Python | [PyPI](https://pypi.org/project/agentity-a2a/) |
| `agentity-inspector` | TypeScript | private (Next.js) |
| `agentity-manifest-gen` | TypeScript | [npm](https://www.npmjs.com/package/@agentity/manifest-gen) |
| `agentity-evm` | Python | PyPI |
| `agentity-website` | TypeScript | [agentity-website.vercel.app](https://agentity-website.vercel.app) |

## Resources

- [Protocol specification](../packages/agentity-spec/SPEC.md)
- [GitHub](https://github.com/agenttity/agentity)
- [License: Apache 2.0](../LICENSE)
