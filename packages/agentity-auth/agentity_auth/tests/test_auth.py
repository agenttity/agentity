from fastapi import FastAPI
from fastapi.testclient import TestClient
from agentity_auth import router


app = FastAPI()
app.include_router(router)
client = TestClient(app)


def test_login_unknown_provider():
    resp = client.get("/auth/login/unknown")
    assert resp.status_code == 404


def test_login_unconfigured_provider():
    resp = client.get("/auth/login/google")
    assert resp.status_code == 503
    assert "not configured" in resp.text


def test_session_not_found():
    resp = client.get("/auth/session/invalid")
    assert resp.status_code == 404


def test_me_missing_header():
    resp = client.get("/auth/me")
    assert resp.status_code == 401


def test_register_verified_missing_header():
    resp = client.post("/auth/register-verified", json={"did": "test", "owner_did": "test"})
    assert resp.status_code == 401
