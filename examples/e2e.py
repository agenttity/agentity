#!/usr/bin/env python3
"""Agentity Protocol — end-to-end example."""

import json
from agentity_sdk import AgentKeyPair, AgentIdentity, RequestSigner, RequestVerifier


def main():
    print("=== Agentity Protocol E2E Example ===\n")

    # 1. Create an agent identity
    print("[1] Creating agent identity...")
    kp = AgentKeyPair()
    aid = kp.create_identity(
        owner_did="did:agentity:human:alice",
        scopes=["stripe:payments:read", "calendar:events:write"],
        ttl_days=30,
        model={"provider": "anthropic", "name": "claude-sonnet-4-6", "version": "20251001"},
    )
    print(f"    DID:     {aid.did}")
    print(f"    Owner:   {aid.owner.did}")
    print(f"    Scopes:  {', '.join(aid.scope)}")
    print(f"    Expires: {aid.expires}")

    # 2. Verify the self-signed AID
    print("\n[2] Verifying AID signature...")
    assert aid.verify_signature(), "AID signature verification failed!"
    print("    ✓ Signature valid")

    # 3. Sign a request
    print("\n[3] Signing a request...")
    signer = RequestSigner(kp, aid)
    headers = signer.sign_request("GET", "/api/v1/payments")
    print(f"    Agentity-Token:     {headers['Agentity-Token'][:50]}...")
    print(f"    Agentity-Nonce:     {headers['Agentity-Nonce']}")
    print(f"    Agentity-Timestamp: {headers['Agentity-Timestamp']}")

    # 4. Verify the request
    print("\n[4] Verifying request...")
    verifier = RequestVerifier()
    used = set()
    result_aid = verifier.verify_request(headers, "GET", "/api/v1/payments", used_nonces=used)
    print(f"    ✓ Request verified (DID: {result_aid.did})")

    # 5. Replay detection
    print("\n[5] Testing replay protection...")
    try:
        verifier.verify_request(headers, "GET", "/api/v1/payments", used_nonces=used)
        print("    ✗ Replay not detected (BUG!)")
    except PermissionError as e:
        print(f"    ✓ Replay detected: {e}")

    # 6. Expired AID detection
    print("\n[6] Testing expired AID...")
    short_kp = AgentKeyPair()
    short_aid = short_kp.create_identity("did:agentity:human:bob", ["test:read"], ttl_days=0)
    assert short_aid.is_expired(), "AID should be expired!"
    print("    ✓ Expired AID correctly detected")

    # 7. Delegation chain
    print("\n[7] Creating delegation chain...")
    parent_kp = AgentKeyPair()
    parent_aid = parent_kp.create_identity(
        "did:agentity:human:alice",
        ["stripe:*:*", "calendar:events:read"],
        ttl_days=30,
    )
    child_kp = AgentKeyPair()
    child_aid = child_kp.create_identity(
        parent_aid.did,
        ["stripe:payments:read"],
        ttl_days=30,
        parent=parent_aid.did,
        delegation_depth=1,
    )
    print(f"    Parent: {parent_aid.did}")
    print(f"    Child:  {child_aid.did}")
    print(f"    Depth:  {child_aid.delegationDepth}")
    assert child_aid.parent == parent_aid.did
    assert child_aid.delegationDepth == 1
    print("    ✓ Delegation chain valid")

    # 8. Save identity to file
    print("\n[8] Saving identity...")
    output = {
        "did": aid.did,
        "publicKey": kp.public_key_b64(),
        "secretKey": kp.secret_key_b64(),
        "fingerprint": kp.fingerprint(),
        "aid": aid.model_dump(),
    }
    with open("/tmp/agentity-identity.json", "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"    Saved to /tmp/agentity-identity.json")

    print("\n=== All checks passed ===")


if __name__ == "__main__":
    main()
