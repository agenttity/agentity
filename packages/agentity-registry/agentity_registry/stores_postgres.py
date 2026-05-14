"""PostgreSQL + Redis store for Agentity Registry."""

import json
from datetime import datetime, timezone
from typing import Optional

import asyncpg
import redis.asyncio as aioredis
from fastapi import HTTPException, WebSocket, WebSocketDisconnect

from .models import AgentStatus, RevokeRequest, AuditEntry, RegisterRequest, AgentInfo
from .stores import BaseStore


class PostgresStore(BaseStore):
    def __init__(self, database_url: str, redis_url: str):
        self._db_url = database_url
        self._redis_url = redis_url
        self._pg: Optional[asyncpg.Pool] = None
        self._r: Optional[aioredis.Redis] = None
        self._pubsub: Optional[aioredis.Redis] = None
        self._websockets: list[WebSocket] = []
        self._ws_pubsub_task = None

    async def startup(self):
        self._pg = await asyncpg.create_pool(self._db_url, min_size=2, max_size=10)
        self._r = aioredis.from_url(self._redis_url, decode_responses=True)
        self._pubsub = aioredis.from_url(self._redis_url, decode_responses=True)
        await self._migrate()

    async def shutdown(self):
        if self._pg:
            await self._pg.close()
        if self._r:
            await self._r.aclose()
        if self._pubsub:
            await self._pubsub.aclose()

    async def _migrate(self):
        async with self._pg.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    did TEXT PRIMARY KEY,
                    aid_json TEXT NOT NULL,
                    public_key_b64 TEXT NOT NULL,
                    scopes TEXT[] DEFAULT '{}',
                    owner_did TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    parent_did TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    expires_at TIMESTAMPTZ NOT NULL
                );
                CREATE TABLE IF NOT EXISTS audit_log (
                    id BIGSERIAL PRIMARY KEY,
                    did TEXT NOT NULL,
                    event TEXT NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    actor TEXT,
                    reason TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_audit_did ON audit_log(did);
                CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
            """)
            await conn.execute("SELECT 1")

    async def register(self, req: RegisterRequest) -> AgentStatus:
        now = datetime.now(timezone.utc)
        expires = now.replace(year=now.year + 1)
        async with self._pg.acquire() as conn:
            await conn.execute(
                """INSERT INTO agents (did, aid_json, public_key_b64, scopes, owner_did, status, created_at, expires_at)
                   VALUES ($1, $2, $3, $4, $5, 'active', $6, $7)""",
                req.did, req.aid_json, req.public_key_b64, req.scopes, req.owner_did, now, expires,
            )
            await conn.execute(
                "INSERT INTO audit_log (did, event, timestamp) VALUES ($1, 'created', $2)",
                req.did, now,
            )
        return AgentStatus(did=req.did, status="active", updatedAt=now)

    async def get_status(self, did: str) -> AgentStatus:
        async with self._pg.acquire() as conn:
            row = await conn.fetchrow("SELECT status, expires_at FROM agents WHERE did=$1", did)
        if not row:
            raise HTTPException(status_code=404, detail="DID not found")
        status = row["status"]
        if status == "active" and datetime.now(timezone.utc) > row["expires_at"]:
            async with self._pg.acquire() as conn:
                await conn.execute("UPDATE agents SET status='expired' WHERE did=$1", did)
            status = "expired"
        return AgentStatus(did=did, status=status, updatedAt=row["expires_at"])

    async def get_aid(self, did: str) -> dict:
        async with self._pg.acquire() as conn:
            row = await conn.fetchrow("SELECT aid_json FROM agents WHERE did=$1", did)
        if not row:
            raise HTTPException(status_code=404, detail="DID not found")
        return json.loads(row["aid_json"])

    async def revoke(self, req: RevokeRequest) -> AgentStatus:
        async with self._pg.acquire() as conn:
            row = await conn.fetchrow("SELECT status FROM agents WHERE did=$1", req.did)
            if not row:
                raise HTTPException(status_code=404, detail="DID not found")
            if row["status"] != "active":
                raise HTTPException(status_code=400, detail="AID is not active")
            now = datetime.now(timezone.utc)
            await conn.execute("UPDATE agents SET status='revoked' WHERE did=$1", req.did)
            await conn.execute(
                "INSERT INTO audit_log (did, event, timestamp, actor, reason) VALUES ($1, 'revoked', $2, $3, $4)",
                req.did, now, req.reason, req.reason,
            )
            if req.cascade:
                await conn.execute(
                    "UPDATE agents SET status='revoked' WHERE parent_did=$1 AND status='active'",
                    req.did,
                )
        return AgentStatus(did=req.did, status="revoked", updatedAt=datetime.now(timezone.utc))

    async def get_audit(self, did: str) -> list[AuditEntry]:
        async with self._pg.acquire() as conn:
            rows = await conn.fetch(
                "SELECT did, event, timestamp, actor, reason FROM audit_log WHERE did=$1 ORDER BY timestamp",
                did,
            )
        return [AuditEntry(**dict(r)) for r in rows]

    async def list_agents(self) -> list[AgentInfo]:
        async with self._pg.acquire() as conn:
            rows = await conn.fetch(
                "SELECT did, status, owner_did, scopes, created_at, expires_at FROM agents ORDER BY created_at DESC",
            )
        return [
            AgentInfo(
                did=r["did"], status=r["status"], owner_did=r["owner_did"],
                scopes=list(r["scopes"]) if r["scopes"] else [],
                created_at=r["created_at"], expires_at=r["expires_at"],
            )
            for r in rows
        ]

    async def broadcast(self, event: str, did: str):
        msg = json.dumps({"type": event, "did": did, "timestamp": datetime.now(timezone.utc).isoformat()})
        if self._r:
            await self._r.publish("agentity:events", msg)
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
                data = await ws.receive_text()
                if data == "ping":
                    await ws.send_text("pong")
        except WebSocketDisconnect:
            self._websockets.remove(ws)
