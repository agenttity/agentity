# @agentity/inspector

**Next.js 15 dashboard for the Agentity Protocol.**
Real-time monitoring of all registered agents — active status, scopes, owner info, and live WebSocket revocation events.

## Usage

```bash
# Development
pnpm dev

# Production (static export)
pnpm build
pnpm start
```

## Features

- **Connection bar** — Enter any registry URL (default `http://localhost:8000`)
- **Active agents list** — All registered agents with DID, owner, scopes, status badge
- **Live revocations** — WebSocket event stream, last 20 events auto-updated
- **Status indicators** — Green = active, Red = revoked

## API usage

The inspector connects to a running `agentity-registry` instance:

```
GET {registryUrl}/agents    → AgentInfo[]
WS  ws://{registryUrl}/ws   → { type: "revocation"|"created", did, timestamp }
```

## Deployment

```bash
next build     # Static export → out/
```

The inspector is a static Next.js export — deployable to any static host (Vercel, S3, Netlify, etc.).

License: Apache 2.0
