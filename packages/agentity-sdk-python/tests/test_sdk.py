import pytest
from agentity_sdk import AgentKeyPair, AgentDid, AgentIdentity, RequestSigner, RequestVerifier


def test_keypair_generation():
    kp = AgentKeyPair()
    assert len(kp.public_key_bytes()) == 32
    assert kp.fingerprint()


def test_sign_and_verify():
    kp = AgentKeyPair()
    msg = b"hello world"
    sig = kp.sign(msg)
    assert AgentKeyPair.verify(kp.public_key_b64(), msg, sig)


def test_verify_bad_signature():
    kp = AgentKeyPair()
    assert not AgentKeyPair.verify(kp.public_key_b64(), b"msg", "bad")


def test_did_format():
    kp = AgentKeyPair()
    did = AgentDid.from_keypair(kp)
    assert did.as_str().startswith("did:agentity:agent:")


def test_create_identity():
    kp = AgentKeyPair()
    aid = kp.create_identity("did:agentity:human:alice", ["test:read"], 30)
    assert aid.verify_signature()
    assert not aid.is_expired()
    assert aid.status == "active"


def test_token_roundtrip():
    kp = AgentKeyPair()
    aid = kp.create_identity("did:agentity:human:bob", ["data:read"], 30)
    token = aid.encode_token(kp, "nonce-1", "2026-05-08T12:00:00Z", "GET", "/api/data")
    decoded, sig = AgentIdentity.decode_token(token)
    assert decoded.did == aid.did


def test_sign_request_roundtrip():
    kp = AgentKeyPair()
    aid = kp.create_identity("did:agentity:human:carol", ["api:read"], 1)
    signer = RequestSigner(kp, aid)
    headers = signer.sign_request("GET", "/api/test")
    assert "Agentity-Token" in headers
    assert "Agentity-Nonce" in headers
    assert "Agentity-Timestamp" in headers


def test_verifier():
    kp = AgentKeyPair()
    aid = kp.create_identity("did:agentity:human:dave", ["svc:read"], 1)
    signer = RequestSigner(kp, aid)
    headers = signer.sign_request("GET", "/api/resource")
    verifier = RequestVerifier()
    used = set()
    result = verifier.verify_request(headers, "GET", "/api/resource", used_nonces=used)
    assert result.did == aid.did


def test_replay_detection():
    kp = AgentKeyPair()
    aid = kp.create_identity("did:agentity:human:eve", ["svc:read"], 1)
    signer = RequestSigner(kp, aid)
    headers = signer.sign_request("GET", "/api/data")
    verifier = RequestVerifier()
    used = set()
    verifier.verify_request(headers, "GET", "/api/data", used_nonces=used)
    with pytest.raises(PermissionError, match="replay"):
        verifier.verify_request(headers, "GET", "/api/data", used_nonces=used)


def test_key_rotation():
    kp = AgentKeyPair()
    aid = kp.create_identity("did:agentity:human:adam", ["svc:read"], 30)
    assert aid.version == "1"

    new_aid = kp.rotate(aid, ttl_days=90)
    assert new_aid.version == "2"
    assert new_aid.previousAid == aid.did
    assert new_aid.owner.did == aid.owner.did
    assert new_aid.scope == aid.scope
    assert new_aid.verify_signature()
    assert not new_aid.is_expired()
