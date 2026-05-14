"""LangChain integration for Agentity Protocol."""

from typing import Optional, Any
from agentity_sdk import AgentKeyPair, AgentIdentity, RequestSigner


class AgentityLangChainMixin:
    """Mixin to add Agentity identity to LangChain requests."""

    def __init__(self, keypair: Optional[AgentKeyPair] = None, identity: Optional[AgentIdentity] = None):
        self._agentity_keypair = keypair or AgentKeyPair()
        self._agentity_identity = identity or self._agentity_keypair.create_identity(
            "did:agentity:human:langchain-user",
            ["llm:generate:write"],
            ttl_days=30,
        )
        self._agentity_signer = RequestSigner(self._agentity_keypair, self._agentity_identity)

    def _agentity_sign_headers(self, method: str, url: str, body: Optional[bytes] = None) -> dict[str, str]:
        return self._agentity_signer.sign_headers(url, method, body)

    def agentity_did(self) -> str:
        return self._agentity_identity.did

    def agentity_scope(self) -> list[str]:
        return self._agentity_identity.scope
