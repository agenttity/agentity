"""Tests for agentity-evm bridge."""

import pytest
from agentity_evm import EvmConfig, EvmPublisher


def test_evm_config_defaults():
    cfg = EvmConfig()
    assert cfg.rpc_url == "http://localhost:8545"
    assert cfg.chain_id == 1337


def test_publisher_connect_no_contract():
    pub = EvmPublisher(config=EvmConfig(rpc_url="http://localhost:8545", contract_address="", private_key=""))
    assert pub.connect() is False


def test_publisher_connect_refused():
    pub = EvmPublisher(config=EvmConfig(
        rpc_url="http://localhost:9999",
        contract_address="0x0000000000000000000000000000000000000000",
        private_key="0x0000000000000000000000000000000000000000000000000000000000000001",
    ))
    assert pub.connect() is False


def test_verify_no_network():
    from agentity_evm import EvmVerifier
    ver = EvmVerifier(rpc_url="http://localhost:9999", contract_address="0x0000000000000000000000000000000000000000")
    result = ver.verify("did:agentity:agent:test")
    assert result["status"] == "unknown"
    assert result["source"] == "evm"
