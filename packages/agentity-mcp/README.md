# agentity-mcp

**MCP (Model Context Protocol) plugin for Agentity.**
Wrap any MCP server to inject Agentity identity into tool calls — enabling scoped, verifiable agent-to-tool requests.

## Installation

```bash
pip install agentity-mcp
```

## Usage

```python
from agentity_mcp import McpServerWrapper

# Wrap an MCP server with Agentity identity
wrapper = McpServerWrapper()

print(f"Agent DID: {wrapper.agent_did}")
print(f"Scopes: {wrapper.agent_scope}")

# Get signed headers for any MCP request
headers = wrapper.get_headers(method="POST", path="/tools/call", body=b'{}')
# {
#   "Agentity-Token": "<base64(AID)>.<base64(sig)>",
#   "Agentity-Nonce": "<uuid-v4>",
#   "Agentity-Timestamp": "<ISO-8601>",
# }
```

### Custom keypair and identity

```python
from agentity_sdk import AgentKeyPair
from agentity_mcp import McpServerWrapper

kp = AgentKeyPair()
aid = kp.create_identity(
    owner_did="did:agentity:human:alice",
    scopes=["mcp:tool:call", "mcp:resource:read"],
    ttl_days=30,
)

wrapper = McpServerWrapper(keypair=kp, identity=aid)
```

## Default scopes

When no identity is provided, `McpServerWrapper` auto-creates one with scopes:
- `mcp:tool:call`
- `mcp:resource:read`

## API

| Method / Property | Description |
|---|---|
| `McpServerWrapper(keypair?, identity?)` | Create wrapper, auto-generates identity if omitted |
| `.get_headers(method, path, body?)` | Get signed Agentity headers for an MCP request |
| `.agent_did` | The agent's DID string |
| `.agent_scope` | The agent's scope list |

License: Apache 2.0
