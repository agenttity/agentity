from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from datetime import datetime, timezone
from typing import Optional
from contextlib import asynccontextmanager

from .models import AgentStatus, RevokeRequest, AuditEntry, RegisterRequest


class InMemoryStore:
    """Simple in-memory store (replace with Redis/PostgreSQL in production)."""

    def __init__(self):
        self._agents: dict[str, dict] = {}
        self._audit: list[AuditEntry] = []
        self._websockets: list[WebSocket] = []

    def register(self, req: RegisterRequest) -> AgentStatus:
        now = datetime.now(timezone.utc)
        self._agents[req.did] = {
            "did": req.did,
            "aid_json": req.aid_json,
            "public_key_b64": req.public_key_b64,
            "scopes": req.scopes,
            "owner_did": req.owner_did,
            "status": "active",
            "created_at": now,
            "expires_at": now.replace(year=now.year + 1),
            "children": [],
        }
        entry = AuditEntry(did=req.did, event="created", timestamp=now)
        self._audit.append(entry)
        return AgentStatus(did=req.did, status="active", updatedAt=now)

    def get_status(self, did: str) -> AgentStatus:
        agent = self._agents.get(did)
        if not agent:
            raise HTTPException(status_code=404, detail="DID not found")
        now = datetime.now(timezone.utc)
        if agent["status"] == "active" and now > agent["expires_at"]:
            agent["status"] = "expired"
        return AgentStatus(did=did, status=agent["status"], updatedAt=agent.get("expires_at", now))

    def get_aid(self, did: str) -> dict:
        agent = self._agents.get(did)
        if not agent:
            raise HTTPException(status_code=404, detail="DID not found")
        import json
        return json.loads(agent["aid_json"])

    def revoke(self, req: RevokeRequest) -> AgentStatus:
        agent = self._agents.get(req.did)
        if not agent:
            raise HTTPException(status_code=404, detail="DID not found")
        if agent["status"] != "active":
            raise HTTPException(status_code=400, detail="AID is not active")
        agent["status"] = "revoked"
        now = datetime.now(timezone.utc)
        entry = AuditEntry(did=req.did, event="revoked", timestamp=now, actor=req.reason, reason=req.reason)
        self._audit.append(entry)

        if req.cascade:
            self._revoke_children(req.did, req.reason, now)
        return AgentStatus(did=req.did, status="revoked", updatedAt=now)

    def _revoke_children(self, parent_did: str, reason: str, now: datetime):
        for did, agent in self._agents.items():
            if agent.get("parent_did") == parent_did and agent["status"] == "active":
                agent["status"] = "revoked"
                entry = AuditEntry(did=did, event="revoked", timestamp=now, actor=f"cascade:{parent_did}", reason=reason)
                self._audit.append(entry)

    def get_audit(self, did: str) -> list[AuditEntry]:
        return [e for e in self._audit if e.did == did]

    async def broadcast(self, event: str, did: str):
        import json
        msg = json.dumps({"type": event, "did": did, "timestamp": datetime.now(timezone.utc).isoformat()})
        for ws in self._websockets[:]:
            try:
                await ws.send_text(msg)
            except Exception:
                self._websockets.remove(ws)

    async def ws_connect(self, ws: WebSocket):
        await ws.accept()
        self._websockets.append(ws)
        try:
            while True:
                await ws.receive_text()
        except WebSocketDisconnect:
            self._websockets.remove(ws)


store = InMemoryStore()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Agentity Registry", version="0.1.0", lifespan=lifespan)

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.post("/register")
    async def register(req: RegisterRequest):
        return store.register(req)

    @app.get("/did/{did}")
    async def get_aid(did: str):
        return store.get_aid(did)

    @app.get("/did/{did}/status")
    async def get_status(did: str):
        return store.get_status(did)

    @app.post("/revoke")
    async def revoke(req: RevokeRequest):
        result = store.revoke(req)
        await store.broadcast("revocation", req.did)
        return result

    @app.get("/audit/{did}")
    async def get_audit(did: str):
        return store.get_audit(did)

    @app.websocket("/ws")
    async def websocket(ws: WebSocket):
        await store.ws_connect(ws)

    return app


app = create_app()
