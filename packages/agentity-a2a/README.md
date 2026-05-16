# agentity-a2a

**A2A (Agent-to-Agent) protocol plugin for Agentity.**
Sign and verify inter-agent communication using the Agentity identity layer — enabling scoped, auditable agent-to-agent requests.

## Installation

```bash
pip install agentity-a2a
```

## Usage

```python
import asyncio
from agentity_a2a import A2AClient

async def main():
    # Create an A2A client with Agentity identity
    client = A2AClient()

    print(f"Agent DID: {client.agent_did}")
    print(f"Scopes: {client.agent_scope}")

    # Send a signed A2A request
    result = await client.send_request(
        url="https://api.agent-service.com/agent/message",
        method="POST",
        body=b'{"type": "task", "payload": "..."}',
    )
    print(f"Status: {result['status']}")
    print(f"Body: {result['body']}")

asyncio.run(main())
```

### Custom keypair and identity

```python
from agentity_sdk import AgentKeyPair
from agentity_a2a import A2AClient

kp = AgentKeyPair()
aid = kp.create_identity(
    owner_did="did:agentity:human:alice",
    scopes=["a2a:agent:send", "a2a:message:receive"],
    ttl_days=30,
)

client = A2AClient(keypair=kp, identity=aid)
```

## Default scopes

When no identity is provided, `A2AClient` auto-creates one with scopes:
- `a2a:agent:send`
- `a2a:message:receive`

## API

| Method / Property | Description |
|---|---|
| `A2AClient(keypair?, identity?)` | Create client, auto-generates identity if omitted |
| `async send_request(url, method, body?)` | Send signed A2A HTTP request |
| `.agent_did` | The agent's DID string |
| `.agent_scope` | The agent's scope list |

License: Apache 2.0
