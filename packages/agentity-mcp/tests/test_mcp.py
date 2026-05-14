import pytest
from agentity_mcp import McpServerWrapper


def test_mcp_wrapper_creates_identity():
    wrapper = McpServerWrapper()
    assert wrapper.agent_did.startswith("did:agentity:agent:")
    assert "mcp:tool:call" in wrapper.agent_scope


def test_mcp_wrapper_signs_headers():
    wrapper = McpServerWrapper()
    headers = wrapper.get_headers("POST", "/api/tool/call", b'{"input":"test"}')
    assert "Agentity-Token" in headers
    assert "Agentity-Nonce" in headers
    assert "Agentity-Timestamp" in headers


def test_mcp_custom_identity():
    from agentity_sdk import AgentKeyPair
    kp = AgentKeyPair()
    aid = kp.create_identity("did:agentity:human:mcp-custom", ["mcp:tool:call"], 30)
    wrapper = McpServerWrapper(keypair=kp, identity=aid)
    assert wrapper.agent_did == aid.did


def test_mcp_scope():
    wrapper = McpServerWrapper()
    assert "mcp:tool:call" in wrapper.agent_scope
