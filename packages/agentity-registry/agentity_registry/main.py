import hashlib
import hmac
import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .models import RevokeRequest, RegisterRequest
from .stores import BaseStore, InMemoryStore
from .rate_limit import check_rate_limit

from typing import Optional


def _load_env():
    p = Path(__file__).resolve().parents[3] / ".env"
    if p.exists():
        with open(p) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

_load_env()

STORE_TYPE = os.getenv("AGENTITY_STORE", "memory")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://agentity:agentity@localhost:5432/agentity")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
AUTH_ENABLED = os.getenv("AGENTITY_AUTH_URL", "") != ""
AUDIT_SIGN_SECRET = os.getenv("AUDIT_SIGN_SECRET", "")
EVM_ENABLED = os.getenv("AGENTITY_EVM_RPC_URL", "") != "" and os.getenv("AGENTITY_EVM_CONTRACT", "") != ""

store: BaseStore = InMemoryStore()
evm_publisher: Optional = None


async def create_store() -> BaseStore:
    stype = STORE_TYPE.lower()
    if stype == "postgres":
        from .stores_postgres import PostgresStore
        s = PostgresStore(DATABASE_URL, REDIS_URL)
        await s.startup()
        return s
    return InMemoryStore()


def sign_audit_entry(did: str, event: str, timestamp: str) -> str:
    if not AUDIT_SIGN_SECRET:
        return ""
    payload = f"{did}:{event}:{timestamp}"
    return hmac.new(AUDIT_SIGN_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global store, evm_publisher
    store = await create_store()
    if EVM_ENABLED:
        try:
            from agentity_evm import EvmPublisher
            pub = EvmPublisher()
            if pub.connect():
                evm_publisher = pub
        except Exception:
            pass
    yield
    await store.shutdown()


def create_app() -> FastAPI:
    app = FastAPI(title="Agentity Registry", version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Optional: mount OIDC auth router
    if AUTH_ENABLED:
        try:
            from agentity_auth import router as auth_router
            app.include_router(auth_router)
        except ImportError:
            pass

    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        did = request.headers.get("X-Agent-DID") or ""
        if did:
            allowed, remaining = await check_rate_limit(did)
            if not allowed:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded", "retry_after": 60},
                    headers={"X-RateLimit-Remaining": "0"},
                )
            response = await call_next(request)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            return response
        return await call_next(request)

    @app.get("/health")
    async def health():
        return {"status": "ok", "store": STORE_TYPE, "auth": AUTH_ENABLED}

    @app.post("/register")
    async def register(req: RegisterRequest, request: Request):
        # OIDC verification (optional)
        if AUTH_ENABLED:
            session_token = request.headers.get("Agentity-Session")
            if session_token:
                try:
                    from httpx import AsyncClient
                    auth_url = os.getenv("AGENTITY_AUTH_URL", "http://localhost:8765")
                    async with AsyncClient() as client:
                        vr = await client.get(f"{auth_url}/auth/session/{session_token}")
                        if vr.status_code != 200:
                            raise HTTPException(403, detail="Invalid OIDC session")
                        owner = vr.json()
                        if owner.get("did") != req.owner_did:
                            raise HTTPException(403, detail="owner_did does not match authenticated user")
                except HTTPException:
                    raise
                except Exception:
                    raise HTTPException(503, detail="Auth service unavailable")

        result = await store.register(req)
        await store.broadcast("created", req.did)
        if evm_publisher:
            import hashlib as hp
            from base64 import urlsafe_b64decode
            try:
                aid = json.loads(req.aid_json)
                pk = aid.get("publicKey", {}).get("value", "")
                fp = hp.sha256(urlsafe_b64decode(pk + "==")).hexdigest()
                evm_publisher.register(req.did, fp, req.owner_did)
            except Exception:
                pass
        return result

    @app.get("/did/{did}")
    async def get_aid(did: str):
        return await store.get_aid(did)

    @app.get("/did/{did}/status")
    async def get_status(did: str):
        return await store.get_status(did)

    @app.get("/agents")
    async def list_agents():
        return await store.list_agents()

    @app.post("/revoke")
    async def revoke(req: RevokeRequest):
        result = await store.revoke(req)
        await store.broadcast("revocation", req.did)
        if evm_publisher:
            try:
                evm_publisher.revoke(req.did)
            except Exception:
                pass
        return result

    @app.get("/audit")
    async def get_all_audit():
        entries = await store.get_all_audit()
        if AUDIT_SIGN_SECRET:
            result = []
            for e in entries:
                ts = e.timestamp.isoformat() if hasattr(e.timestamp, 'isoformat') else str(e.timestamp)
                sig = sign_audit_entry(e.did, e.event, ts)
                result.append({**e.model_dump(), "signature": sig})
            return result
        return entries

    @app.get("/audit/{did}")
    async def get_audit(did: str):
        entries = await store.get_audit(did)
        if AUDIT_SIGN_SECRET:
            result = []
            for e in entries:
                ts = e.timestamp.isoformat() if hasattr(e.timestamp, 'isoformat') else str(e.timestamp)
                sig = sign_audit_entry(e.did, e.event, ts)
                result.append({**e.model_dump(), "signature": sig})
            return result
        return entries

    @app.get("/audit/{did}/verify")
    async def verify_audit(did: str, signature: str, event: str, timestamp: str):
        expected = sign_audit_entry(did, event, timestamp)
        if hmac.compare_digest(expected, signature):
            return {"valid": True}
        return {"valid": False}

    @app.websocket("/ws")
    async def websocket(ws: WebSocket):
        await store.ws_connect(ws)

    return app


app = create_app()
