# Security

## Overview

The Agentity Protocol implements defense-in-depth across six security mechanisms:

| Mechanism | Scope | Description |
|-----------|-------|-------------|
| Ed25519 signatures | Per-request | All requests carry a signed token |
| Anti-replay | Per-request | Nonce + timestamp window |
| Key rotation | Per-identity | Versioned keys with previousAid links |
| Delegation chains | Per-tree | Max 10 levels, cascade revocation |
| OIDC auth | Per-owner | Verified human ownership via Google/GitHub/Apple/MS |
| Rate limiting | Per-DID | Redis-backed configurable window |

## 1. Ed25519 signatures

Every agent has an Ed25519 keypair. All identity documents (AIDs) are self-signed. Each HTTP request carries:

```
Agentity-Token: <base64url(AID_json)>.<base64url(signature)>
Agentity-Nonce: <uuid-v4>
Agentity-Timestamp: <ISO-8601>
```

The signature covers:

```
SHA-256(did + nonce + timestamp + method + path + body_hash)
```

Verification steps:
1. Decode token → AID JSON + signature
2. Extract public key from AID
3. Verify Ed25519 signature on the signed payload
4. Check AID not expired
5. Check status via registry (`active`)
6. Validate scopes against provider manifest

## 2. Anti-replay

- Each request includes a UUID v4 nonce
- Timestamps must be within ±300 seconds of server time
- Nonces are tracked server-side (in-memory Set or Redis) with TTL matching the tolerance window
- Replayed nonces: HTTP 403

## 3. Key rotation

When a key is rotated:

```
agentity_sdk/
  AgentKeyPair.rotate(previous_aid, ttl_days=90)
```

- New Ed25519 keypair generated
- New AID gets `version = previous.version + 1`
- `previousAid` field links to old AID
- Old AID status → `expired`
- Audit log records the rotation

Rotate proactively on a schedule or when a compromise is suspected.

## 4. Delegation chains

```
Root owner (human)         delegationDepth: 0
  └─ Agent A               delegationDepth: 1, parent: root
       └─ Agent B          delegationDepth: 2, parent: A
            └─ Agent C     delegationDepth: 3, parent: B
```

Rules:
- Max 10 levels of delegation
- Child scopes must be a subset of parent scopes (no scope escalation)
- Revoking a parent cascades to all descendants
- Each AID's `parent` field contains the parent's DID

## 5. OIDC owner verification

Human ownership is verified via OAuth2:

1. User logs in via Google/GitHub
2. Agentity creates a `did:agentity:human:{fingerprint}` from the provider's user ID
3. Session token binds the owner DID
4. Registry accepts registration only with verified `owner_did`
5. API: `GET /auth/login/google`, `GET /auth/callback/google`, `POST /register`

Apple and Microsoft providers are also supported but require client credentials.

## 6. Rate limiting

- Redis-backed per-DID
- Default: 100 requests / 60 second window
- Response header: `X-RateLimit-Remaining`
- HTTP 429 when exhausted

## 7. Signed audit log

Every registry event (create, revoke, rotate) is logged with:

- HMAC-SHA256 signature
- DID, event type, timestamp, actor, reason
- Verifiable via `GET /audit/{did}/verify`

## Threat model

| Threat | Mitigation |
|--------|------------|
| Token theft | Anti-replay (nonce + timestamp), short tolerance |
| Key compromise | Rotation, old key marked expired |
| Scope escalation | Delegation requires subset, manifest validation |
| Replay attack | Nonce tracking, 5 min window |
| DID hijacking | Ed25519 signature verification |
| Spam | Rate limiting per DID |
| Impersonation | OIDC owner verification |
| Unauthorized registration | Verified owner_did matching session |
