# agentity-sdk-python

**Python SDK for the Agentity Protocol.**
Create agent identities, sign HTTP requests, verify tokens, integrate with LangChain and CrewAI.

## Installation

```bash
pip install agentity-sdk-python
```

## Usage

### Create an agent identity

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

### Sign HTTP requests

```python
from agentity_sdk import RequestSigner

signer = RequestSigner(kp, aid)
headers = signer.sign_request("GET", "/api/v1/payments")
# {
#   "Agentity-Token": "<base64(AID)>.<base64(sig)>",
#   "Agentity-Nonce": "<uuid-v4>",
#   "Agentity-Timestamp": "<ISO-8601>",
# }
```

### Verify on the server side

```python
from agentity_sdk import RequestVerifier

verifier = RequestVerifier()
used_nonces = set()
aid = verifier.verify_request(
    headers, "GET", "/api/v1/payments",
    used_nonces=used_nonces,
)
```

### Rotate keys

```python
new_aid = kp.rotate(aid, ttl_days=90)
print(f"Version: {new_aid.version}")       # 2
print(f"Previous AID: {new_aid.previousAid}")
```

### LangChain integration

```python
from agentity_sdk.integrations.langchain import AgentityLangChainMixin

class MyAgent(AgentityLangChainMixin):
    def run(self):
        headers = self._agentity_sign_headers("POST", "https://api.example.com/data")
        print(f"Agent DID: {self.agentity_did()}")
```

### Provider manifest

```python
from agentity_sdk import ProviderManifest, ScopeEntry, ScopeRisk

manifest = ProviderManifest(
    provider="did:agentity:provider:stripe",
    name="Stripe",
    description="Payment processing API",
    scopes=[
        ScopeEntry(id="payments:read", description="Read payments", risk=ScopeRisk.LOW),
        ScopeEntry(id="payments:write", description="Create payments", risk=ScopeRisk.HIGH),
    ],
)
```

## Public API

| Export | Description |
|--------|-------------|
| `AgentKeyPair` | Ed25519 keypair + `create_identity()` + `rotate()` |
| `AgentIdentity` | Pydantic model — DID, scopes, proof, status |
| `AgentDid` | DID string builder |
| `RequestSigner` | Sign HTTP requests with Agentity headers |
| `RequestVerifier` | Verify tokens server-side |
| `ProviderManifest` | Publish service scope definitions |
| `AgentityLangChainMixin` | Mixin for LangChain agents |

## Tests

```bash
pip install -e .[dev]
pytest tests/
```

License: Apache 2.0
