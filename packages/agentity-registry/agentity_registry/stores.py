"""Storage backends for Agentity Registry."""

import json
import os
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, WebSocket, WebSocketDisconnect

from .models import AgentStatus, RevokeRequest, AuditEntry, RegisterRequest, AgentInfo


class BaseStore(ABC):
    @abstractmethod
    async def register(self, req: RegisterRequest) -> AgentStatus:
        ...

    @abstractmethod
    async def get_status(self, did: str) -> AgentStatus:
        ...

    @abstractmethod
    async def get_aid(self, did: str) -> dict:
        ...

    @abstractmethod
    async def revoke(self, req: RevokeRequest) -> AgentStatus:
        ...

    @abstractmethod
    async def get_audit(self, did: str) -> list[AuditEntry]:
        ...

    @abstractmethod
    async def list_agents(self) -> list[AgentInfo]:
        ...

    @abstractmethod
    async def broadcast(self, event: str, did: str):
        ...

    @abstractmethod
    async def ws_connect(self, ws: WebSocket):
        ...

    @abstractmethod
    async def startup(self):
        ...

    @abstractmethod
    async def shutdown(self):
        ...


class InMemoryStore(BaseStore):
    def __init__(self):
        self._agents: dict[str, dict] = {}
        self._audit: list[AuditEntry] = []
        self._websockets: list[WebSocket] = []

    async def startup(self):
        pass

    async def shutdown(self):
        pass

    async def register(self, req: RegisterRequest) -> AgentStatus:
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
        }
        entry = AuditEntry(did=req.did, event="created", timestamp=now)
        self._audit.append(entry)
        return AgentStatus(did=req.did, status="active", updatedAt=now)

    async def get_status(self, did: str) -> AgentStatus:
        agent = self._agents.get(did)
        if not agent:
            raise HTTPException(status_code=404, detail="DID not found")
        now = datetime.now(timezone.utc)
        if agent["status"] == "active" and now > agent["expires_at"]:
            agent["status"] = "expired"
        return AgentStatus(did=did, status=agent["status"], updatedAt=agent.get("expires_at", now))

    async def get_aid(self, did: str) -> dict:
        agent = self._agents.get(did)
        if not agent:
            raise HTTPException(status_code=404, detail="DID not found")
        return json.loads(agent["aid_json"])

    async def revoke(self, req: RevokeRequest) -> AgentStatus:
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

    async def get_audit(self, did: str) -> list[AuditEntry]:
        return [e for e in self._audit if e.did == did]

    async def list_agents(self) -> list[AgentInfo]:
        result = []
        now = datetime.now(timezone.utc)
        for d, agent in self._agents.items():
            result.append(AgentInfo(
                did=d,
                status=agent["status"],
                owner_did=agent["owner_did"],
                scopes=agent["scopes"],
                created_at=agent["created_at"],
                expires_at=agent.get("expires_at"),
            ))
        return result

    async def broadcast(self, event: str, did: str):
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
