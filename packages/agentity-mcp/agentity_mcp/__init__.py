"""Agentity MCP Plugin — signs MCP tool calls with Agentity identity."""

from typing import Optional
from agentity_sdk import AgentKeyPair, AgentIdentity, RequestSigner


class McpServerWrapper:
    """Wraps an MCP server to inject Agentity identity into tool calls."""

    def __init__(self, keypair: Optional[AgentKeyPair] = None, identity: Optional[AgentIdentity] = None):
        self._kp = keypair or AgentKeyPair()
        self._aid = identity or self._kp.create_identity(
            "did:agentity:human:mcp-server",
            ["mcp:tool:call", "mcp:resource:read"],
            ttl_days=30,
        )
        self._signer = RequestSigner(self._kp, self._aid)

    def get_headers(self, method: str = "GET", path: str = "/", body: Optional[bytes] = None) -> dict:
        return self._signer.sign_request(method, path, body)

    @property
    def agent_did(self) -> str:
        return self._aid.did

    @property
    def agent_scope(self) -> list[str]:
        return self._aid.scope
