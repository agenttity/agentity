# agentity-core

**Reference implementation of the Agentity Protocol crypto layer.**
Rust library — Ed25519 keys, DID generation, AID signing/verification, scope matching.

## Installation

```toml
[dependencies]
agentity-core = { git = "https://github.com/agenttity/agentity" }
```

## Usage

### Generate a keypair and DID

```rust
use agentity_core::{AgentKeyPair, AgentDid};

let kp = AgentKeyPair::generate();
let did = AgentDid::from_keypair(&kp);
println!("{}", did.as_str());
// did:agentity:agent:7Xj3mK9pL2nQ8vRtYwZb4cFdHsNaEgUi
```

### Create and verify an AID

```rust
use agentity_core::{AgentKeyPair, AgentDid, AgentIdentityDocument};
use std::collections::HashMap;

let kp = AgentKeyPair::generate();
let owner_did = AgentDid::from_parts("human", "alice_fingerprint");
let scopes = vec!["stripe:payments:read".into(), "calendar:events:write".into()];

let aid = AgentIdentityDocument::new(
    &kp,
    &owner_did,
    &scopes,
    30,         // TTL days
    None,       // parent
    0,          // delegation depth
    None,       // model
).unwrap();

assert!(aid.verify_signature());
```

### Sign and verify HTTP requests

```rust
let kp = AgentKeyPair::generate();
let did = AgentDid::from_keypair(&kp);
let nonce = uuid::Uuid::new_v4().to_string();
let timestamp = "2026-05-08T12:00:00Z";

let sig = AgentKeyPair::sign_request(
    did.as_str(), &nonce, &timestamp,
    "GET", "/api/v1/payments", "",
);

let valid = AgentKeyPair::verify_request(
    &kp.public_key_b64(), did.as_str(),
    &nonce, &timestamp,
    "GET", "/api/v1/payments", "", &sig,
);
assert!(valid);
```

### Scope matching

```rust
use agentity_core::scope::ProviderManifest;

let manifest = ProviderManifest::new("did:agentity:provider:stripe", "Stripe");
assert!(ProviderManifest::has_scope(&["stripe:payments:*"], "stripe:payments:read"));
assert!(!ProviderManifest::has_scope(&["calendar:read"], "stripe:payments:read"));
```

## Public API

| Type | Description |
|------|-------------|
| `AgentKeyPair` | Ed25519 keypair generation, signing, verification |
| `AgentDid` | `did:agentity:{type}:{fingerprint}` creation |
| `AgentIdentityDocument` | Full AID with proof, expiry, delegation |
| `ProviderManifest` | Service provider scope declarations |
| `ScopeEntry` / `ScopeRisk` | Scope definitions with risk levels |
| `AgentityError` | Error types (InvalidSignature, Expired, ScopeEscalation, etc.) |

## Tests

```bash
cargo test --workspace
cargo clippy --workspace -- -D warnings
```

License: Apache 2.0
