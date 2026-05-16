# agentity-evm

**EVM cross-registry bridge for the Agentity Protocol.**
Publish DID registration and revocation events on-chain via a Solidity smart contract, and verify agent identity status across registries using read-only EVM queries.

## Components

- **Solidity contract** (`contracts/Registry.sol`) — On-chain DID registry
- **EvmPublisher** — Python client for writing to the contract
- **EvmVerifier** — Python client for reading from the contract

## Installation

```bash
pip install agentity-evm
```

## Solidity contract

```solidity
contract AgentityRegistry {
    function register(string calldata did, bytes32 fingerprint, string calldata providerDid) external;
    function revoke(string calldata did) external;
    function rotate(string calldata oldDid, string calldata newDid) external;
    function getStatus(string calldata did) external view returns (string memory);
    function getFingerprint(string calldata did) external view returns (bytes32);
}
```

Events: `DIDRegistered`, `DIDRevoked`, `DIDRotated`

## Usage

### Publisher

```python
from agentity_evm import EvmPublisher

publisher = EvmPublisher()
publisher.connect()

# Register a DID on-chain
tx_hash = publisher.register(
    did="did:agentity:agent:7Xj3...",
    fingerprint_hex="a1b2c3...",
    provider_did="did:agentity:provider:stripe",
)
print(f"Transaction: {tx_hash}")

# Revoke
tx_hash = publisher.revoke("did:agentity:agent:7Xj3...")
```

### Verifier

```python
from agentity_evm import EvmVerifier

verifier = EvmVerifier(
    rpc_url="http://localhost:8545",
    contract_address="0x1234...",
)

result = verifier.verify("did:agentity:agent:7Xj3...")
# {"did": "...", "status": "active", "fingerprint": "0x...", "source": "evm"}
```

## Configuration

| Env var | Default | Description |
|---------|---------|-------------|
| `AGENTITY_EVM_RPC_URL` | `http://localhost:8545` | EVM RPC endpoint |
| `AGENTITY_EVM_CONTRACT` | — | Deployed contract address |
| `AGENTITY_EVM_PRIVATE_KEY` | — | Wallet private key for signing |
| `AGENTITY_EVM_CHAIN_ID` | `1337` | Chain ID (Anvil default) |

## Integration with registry

The `agentity-registry` automatically publishes to EVM when `AGENTITY_EVM_RPC_URL` is set:

```bash
AGENTITY_EVM_RPC_URL=http://localhost:8545 \
AGENTITY_EVM_CONTRACT=0x... \
AGENTITY_EVM_PRIVATE_KEY=0x... \
uvicorn agentity_registry.main:app --port 8000
```

## Deploy the contract

```bash
# Using Foundry (cast)
forge create --rpc-url http://localhost:8545 \
  --private-key 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80 \
  contracts/Registry.sol:AgentityRegistry
```

License: Apache 2.0
