# @agentity/sdk

**TypeScript SDK for the Agentity Protocol.**
Create agent identities, sign HTTP requests, and verify tokens — compatible with Vercel AI SDK, Next.js, and Node.js.

## Installation

```bash
pnpm add @agentity/sdk
```

## Usage

### Create an agent identity

```typescript
import { AgentKeyPair, createIdentity } from '@agentity/sdk';

const kp = await AgentKeyPair.generate();
const aid = await createIdentity(
  kp,
  'did:agentity:human:alice',
  ['stripe:payments:read', 'calendar:events:write'],
  30,  // ttlDays
);
console.log(`DID: ${aid.did}`);
console.log(`Signature valid: ${aid.isExpired() === false}`);
```

### Sign HTTP requests

```typescript
import { RequestSigner } from '@agentity/sdk';

const signer = new RequestSigner(kp, aid);
const headers = await signer.signRequest('GET', '/api/v1/payments');
// {
//   'Agentity-Token': '<base64(AID)>.<base64(sig)>',
//   'Agentity-Nonce': '<uuid-v4>',
//   'Agentity-Timestamp': '<ISO-8601>',
// }
```

### Verify on the server side

```typescript
import { RequestVerifier } from '@agentity/sdk';

const verifier = new RequestVerifier();
const usedNonces = new Set<string>();
const verifiedAid = await verifier.verifyRequest(
  headers, 'GET', '/api/v1/payments',
  undefined, 300, usedNonces,
);
```

### Rotate keys

```typescript
import { rotateIdentity } from '@agentity/sdk';

const newAid = await rotateIdentity(aid, kp);
console.log(newAid.version);       // 2
console.log(newAid.previousAid);   // previous AID did
```

### Provider manifest

```typescript
import { ProviderManifest, ScopeRisk } from '@agentity/sdk';

const manifest = new ProviderManifest(
  'did:agentity:provider:stripe',
  'Stripe',
  [{ id: 'payments:read', description: 'Read payments', risk: ScopeRisk.Low }],
);
```

## Public API

| Export | Description |
|--------|-------------|
| `AgentKeyPair` | Ed25519 keypair (async, noble/ed25519) |
| `createIdentity` | Create a signed AgentIdentity |
| `rotateIdentity` | Rotate to a new keypair (version+1) |
| `RequestSigner` | Sign HTTP requests |
| `RequestVerifier` | Verify tokens server-side |
| `ProviderManifest` | Publish service scope definitions |

## Tests

```bash
pnpm test
```

License: Apache 2.0
