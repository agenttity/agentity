"""Agentity EVM bridge — register, revoke, and verify DIDs on-chain."""

import os
from typing import Optional

from pydantic import BaseModel
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

# Default ABI for AgentityRegistry contract
CONTRACT_ABI = [
    {
        "inputs": [{"internalType": "string", "name": "did", "type": "string"}, {"internalType": "bytes32", "name": "fingerprint", "type": "bytes32"}, {"internalType": "string", "name": "providerDid", "type": "string"}],
        "name": "register", "outputs": [], "stateMutability": "nonpayable", "type": "function",
    },
    {
        "inputs": [{"internalType": "string", "name": "did", "type": "string"}],
        "name": "revoke", "outputs": [], "stateMutability": "nonpayable", "type": "function",
    },
    {
        "inputs": [{"internalType": "string", "name": "oldDid", "type": "string"}, {"internalType": "string", "name": "newDid", "type": "string"}],
        "name": "rotate", "outputs": [], "stateMutability": "nonpayable", "type": "function",
    },
    {
        "inputs": [{"internalType": "string", "name": "did", "type": "string"}],
        "name": "getStatus", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function",
    },
    {
        "inputs": [{"internalType": "string", "name": "did", "type": "string"}],
        "name": "getFingerprint", "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}], "stateMutability": "view", "type": "function",
    },
    {
        "inputs": [],
        "name": "didCount", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function",
    },
]


class EvmConfig(BaseModel):
    rpc_url: str = "http://localhost:8545"
    contract_address: str = ""
    private_key: str = ""
    chain_id: int = 1337  # Anvil default


class EvmPublisher:
    """Publishes DID events to an EVM contract."""

    def __init__(self, config: Optional[EvmConfig] = None):
        self._cfg = config or EvmConfig(
            rpc_url=os.getenv("AGENTITY_EVM_RPC_URL", "http://localhost:8545"),
            contract_address=os.getenv("AGENTITY_EVM_CONTRACT", ""),
            private_key=os.getenv("AGENTITY_EVM_PRIVATE_KEY", ""),
            chain_id=int(os.getenv("AGENTITY_EVM_CHAIN_ID", "1337")),
        )
        self._w3: Optional[Web3] = None
        self._contract: Optional = None

    def connect(self):
        if not self._cfg.contract_address or not self._cfg.private_key:
            return False
        self._w3 = Web3(Web3.HTTPProvider(self._cfg.rpc_url))
        self._w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        if not self._w3.is_connected():
            return False
        self._contract = self._w3.eth.contract(
            address=Web3.to_checksum_address(self._cfg.contract_address),
            abi=CONTRACT_ABI,
        )
        return True

    def _account(self):
        return self._w3.eth.account.from_key(self._cfg.private_key)

    def register(self, did: str, fingerprint_hex: str, provider_did: str = "") -> str:
        """Register a DID on-chain. Returns transaction hash."""
        acct = self._account()
        tx = self._contract.functions.register(did, bytes.fromhex(fingerprint_hex), provider_did).build_transaction({
            "from": acct.address,
            "nonce": self._w3.eth.get_transaction_count(acct.address),
            "chainId": self._cfg.chain_id,
        })
        signed = acct.sign_transaction(tx)
        tx_hash = self._w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self._w3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt.transaction_hash.hex()

    def revoke(self, did: str) -> str:
        acct = self._account()
        tx = self._contract.functions.revoke(did).build_transaction({
            "from": acct.address,
            "nonce": self._w3.eth.get_transaction_count(acct.address),
            "chainId": self._cfg.chain_id,
        })
        signed = acct.sign_transaction(tx)
        tx_hash = self._w3.eth.send_raw_transaction(signed.raw_transaction)
        self._w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_hash.hex()

    def get_status(self, did: str) -> str:
        if not self._contract:
            return "unknown"
        return self._contract.functions.getStatus(did).call()

    def get_fingerprint(self, did: str) -> str:
        if not self._contract:
            return ""
        return "0x" + self._contract.functions.getFingerprint(did).call().hex()


class EvmVerifier:
    """Verifies DID status against an EVM contract (read-only)."""

    def __init__(self, rpc_url: str, contract_address: str):
        self._w3 = Web3(Web3.HTTPProvider(rpc_url))
        self._w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        self._contract = self._w3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=[c for c in CONTRACT_ABI if c["stateMutability"] == "view"],
        )

    def verify(self, did: str) -> dict:
        try:
            status = self._contract.functions.getStatus(did).call()
            fingerprint = ""
            if status != "not_found":
                fingerprint = "0x" + self._contract.functions.getFingerprint(did).call().hex()
            return {"did": did, "status": status, "fingerprint": fingerprint, "source": "evm"}
        except Exception:
            return {"did": did, "status": "unknown", "fingerprint": "", "source": "evm"}
