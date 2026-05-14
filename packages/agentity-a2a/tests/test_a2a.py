import pytest
from agentity_a2a import A2AClient


def test_a2a_client_creates_identity():
    client = A2AClient()
    assert client.agent_did.startswith("did:agentity:agent:")
    assert "a2a:agent:send" in client.agent_scope


def test_a2a_custom_identity():
    from agentity_sdk import AgentKeyPair
    kp = AgentKeyPair()
    aid = kp.create_identity("did:agentity:human:a2a-custom", ["a2a:message:receive"], 30)
    client = A2AClient(keypair=kp, identity=aid)
    assert client.agent_did == aid.did


@pytest.mark.asyncio
async def test_a2a_send_request():
    client = A2AClient()
    result = await client.send_request("https://httpbin.org/get", "GET")
    assert result["status"] == 200


@pytest.mark.asyncio
async def test_a2a_scope():
    client = A2AClient()
    assert "a2a:agent:send" in client.agent_scope
    assert "a2a:message:receive" in client.agent_scope
