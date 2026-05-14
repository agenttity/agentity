"""Agentity A2A Plugin — signs A2A agent-to-agent requests with Agentity identity."""

from typing import Optional
from agentity_sdk import AgentKeyPair, AgentIdentity, RequestSigner


class A2AClient:
    """A2A (Agent-to-Agent) client with Agentity identity."""

    def __init__(self, keypair: Optional[AgentKeyPair] = None, identity: Optional[AgentIdentity] = None):
        self._kp = keypair or AgentKeyPair()
        self._aid = identity or self._kp.create_identity(
            "did:agentity:human:a2a-client",
            ["a2a:agent:send", "a2a:message:receive"],
            ttl_days=30,
        )
        self._signer = RequestSigner(self._kp, self._aid)

    async def send_request(self, url: str, method: str = "POST", body: Optional[bytes] = None) -> dict:
        import httpx
        headers = self._signer.sign_headers(url, method, body)
        async with httpx.AsyncClient() as client:
            resp = await client.request(method, url, headers=headers, content=body)
            return {"status": resp.status_code, "body": resp.text}

    @property
    def agent_did(self) -> str:
        return self._aid.did

    @property
    def agent_scope(self) -> list[str]:
        return self._aid.scope
