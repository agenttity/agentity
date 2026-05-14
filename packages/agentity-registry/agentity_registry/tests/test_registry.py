from fastapi.testclient import TestClient
from agentity_registry import create_app
import json

app = create_app()
client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_register_and_status():
    reg = {
        "did": "did:agentity:agent:test123",
        "aid_json": json.dumps({"did": "did:agentity:agent:test123", "version": "1"}),
        "public_key_b64": "testkey",
        "scopes": ["test:read"],
        "owner_did": "did:agentity:human:owner",
        "ttl_days": 30,
    }
    resp = client.post("/register", json=reg)
    assert resp.status_code == 200

    resp = client.get("/did/did:agentity:agent:test123/status")
    assert resp.status_code == 200
    assert resp.json()["status"] == "active"


def test_revoke():
    reg = {
        "did": "did:agentity:agent:revoke-test",
        "aid_json": json.dumps({"did": "did:agentity:agent:revoke-test"}),
        "public_key_b64": "key",
        "scopes": [],
        "owner_did": "did:agentity:human:owner",
        "ttl_days": 30,
    }
    client.post("/register", json=reg)
    resp = client.post("/revoke", json={"did": "did:agentity:agent:revoke-test", "reason": "test", "cascade": False})
    assert resp.status_code == 200
    assert resp.json()["status"] == "revoked"


def test_audit():
    reg = {
        "did": "did:agentity:agent:audit-test",
        "aid_json": json.dumps({"did": "did:agentity:agent:audit-test"}),
        "public_key_b64": "key",
        "scopes": [],
        "owner_did": "did:agentity:human:owner",
        "ttl_days": 30,
    }
    client.post("/register", json=reg)
    resp = client.get("/audit/did:agentity:agent:audit-test")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
    assert resp.json()[0]["event"] == "created"


def test_unknown_did():
    resp = client.get("/did/unknown/status")
    assert resp.status_code == 404
