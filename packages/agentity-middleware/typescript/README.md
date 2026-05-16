# @agentity/middleware-express

**Express.js middleware for the Agentity Protocol.**
Automatically verify Agentity-signed HTTP requests — decode tokens, check nonce and timestamp, verify Ed25519 signatures, and attach agent identity to `req`.

## Installation

```bash
pnpm add @agentity/middleware-express
```

## Usage

```typescript
import express, { Request } from 'express';
import { agentityMiddleware } from '@agentity/middleware-express';

declare global {
  namespace Express {
    interface Request {
      agentDid?: string;
      agentScopes?: string[];
    }
  }
}

const app = express();

app.use(agentityMiddleware({
  registryUrl: 'http://localhost:8000',  // Optional
  toleranceSeconds: 300,                  // Default: 5 min
}));

app.get('/api/data', (req, res) => {
  const agentDid = req.agentDid;
  const agentScopes = req.agentScopes;
  res.json({ agent: agentDid, scopes: agentScopes });
});
```

## How it works

1. Reads `agentity-token`, `agentity-nonce`, `agentity-timestamp` from request headers
2. Validates nonce (in-memory anti-replay set)
3. Checks timestamp is within tolerance window (default ±300s)
4. Decodes AID and verifies Ed25519 signature via `AgentKeyPair.verifyRequest()`
5. If `registryUrl` is set, checks `GET /did/{did}/status` for active status
6. Sets `req.agentDid` and `req.agentScopes` on success
7. Bypasses `/health` paths automatically

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `registryUrl` | `undefined` | Registry URL for DID status verification |
| `toleranceSeconds` | `300` | Timestamp tolerance window |

## Tests

```bash
pnpm test
```

License: Apache 2.0
