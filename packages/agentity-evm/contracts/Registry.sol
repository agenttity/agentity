// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

/// @title Agentity Registry — EVM cross-registry identity tracker
/// @notice Stores fingerprints and statuses of agent DIDs on-chain.
///         Any registry can publish events so other registries can verify.
contract AgentityRegistry {
    enum Status { Active, Revoked, Expired }

    struct Agent {
        bytes32 fingerprint;
        Status status;
        uint256 timestamp;
        string providerDid;
    }

    mapping(string => Agent) public agents;
    string[] private _dids;

    event DIDRegistered(string indexed did, bytes32 indexed fingerprint, address indexed registrar, uint256 timestamp);
    event DIDRevoked(string indexed did, address indexed registrar, uint256 timestamp);
    event DIDRotated(string indexed oldDid, string indexed newDid, address indexed registrar);

    /// @notice Register or update an agent DID on-chain.
    function register(string calldata did, bytes32 fingerprint, string calldata providerDid) external {
        if (keccak256(bytes(agents[did].providerDid)) == keccak256(bytes(""))) {
            _dids.push(did);
        }
        agents[did] = Agent(fingerprint, Status.Active, block.timestamp, providerDid);
        emit DIDRegistered(did, fingerprint, msg.sender, block.timestamp);
    }

    /// @notice Revoke a DID.
    function revoke(string calldata did) external {
        require(agents[did].timestamp != 0, "DID not found");
        agents[did].status = Status.Revoked;
        agents[did].timestamp = block.timestamp;
        emit DIDRevoked(did, msg.sender, block.timestamp);
    }

    /// @notice Record a key rotation (old DID → new DID).
    function rotate(string calldata oldDid, string calldata newDid) external {
        require(agents[oldDid].timestamp != 0, "Old DID not found");
        agents[oldDid].status = Status.Revoked;
        agents[oldDid].timestamp = block.timestamp;
        emit DIDRotated(oldDid, newDid, msg.sender);
    }

    /// @notice Get the status of a DID.
    function getStatus(string calldata did) external view returns (string memory) {
        Agent memory a = agents[did];
        if (a.timestamp == 0) return "not_found";
        if (a.status == Status.Active) return "active";
        if (a.status == Status.Revoked) return "revoked";
        return "expired";
    }

    /// @notice Get the fingerprint (hash of public key) for a DID.
    function getFingerprint(string calldata did) external view returns (bytes32) {
        return agents[did].fingerprint;
    }

    /// @notice Total number of registered DIDs.
    function didCount() external view returns (uint256) {
        return _dids.length;
    }
}
