from fastapi import FastAPI
from fastapi.testclient import TestClient
from agentity_sdk import AgentKeyPair, RequestSigner
from agentity_middleware_python import AgentityMiddleware


def create_test_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(AgentityMiddleware)

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.get("/api/data")
    async def get_data():
        return {"data": "secret"}

    return app


app = create_test_app()
client = TestClient(app)


def test_health_passthrough():
    resp = client.get("/health")
    assert resp.status_code == 200


def test_missing_headers():
    resp = client.get("/api/data")
    assert resp.status_code == 401
    assert "Missing" in resp.text


def test_valid_signed_request():
    kp = AgentKeyPair()
    aid = kp.create_identity("did:agentity:human:test", ["api:read"], 1)
    signer = RequestSigner(kp, aid)
    headers = signer.sign_request("GET", "/api/data")

    resp = client.get("/api/data", headers=headers)
    assert resp.status_code == 200


def test_replay_detection():
    kp = AgentKeyPair()
    aid = kp.create_identity("did:agentity:human:test", ["api:read"], 1)
    signer = RequestSigner(kp, aid)
    headers = signer.sign_request("GET", "/api/data")

    resp1 = client.get("/api/data", headers=headers)
    assert resp1.status_code == 200

    resp2 = client.get("/api/data", headers=headers)
    assert resp2.status_code == 403


def test_expired_aid():
    kp = AgentKeyPair()
    aid = kp.create_identity("did:agentity:human:test", ["api:read"], ttl_days=-1)
    signer = RequestSigner(kp, aid)
    headers = signer.sign_request("GET", "/api/data")

    resp = client.get("/api/data", headers=headers)
    assert resp.status_code == 403
    assert "expired" in resp.text.lower()


def test_bad_token_format():
    headers = {
        "Agentity-Token": "bad.token",
        "Agentity-Nonce": "nonce-1",
        "Agentity-Timestamp": "2026-05-14T12:00:00Z",
    }
    resp = client.get("/api/data", headers=headers)
    assert resp.status_code in (400, 403)
