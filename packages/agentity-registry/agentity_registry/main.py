import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from .models import RevokeRequest, RegisterRequest
from .stores import BaseStore, InMemoryStore

STORE_TYPE = os.getenv("AGENTITY_STORE", "memory")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://agentity:agentity@localhost:5432/agentity")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

store: BaseStore = InMemoryStore()


async def create_store() -> BaseStore:
    stype = STORE_TYPE.lower()
    if stype == "postgres":
        from .stores_postgres import PostgresStore
        s = PostgresStore(DATABASE_URL, REDIS_URL)
        await s.startup()
        return s
    return InMemoryStore()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global store
    store = await create_store()
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

    @app.get("/health")
    async def health():
        return {"status": "ok", "store": STORE_TYPE}

    @app.post("/register")
    async def register(req: RegisterRequest):
        return await store.register(req)

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
        return result

    @app.get("/audit/{did}")
    async def get_audit(did: str):
        return await store.get_audit(did)

    @app.websocket("/ws")
    async def websocket(ws: WebSocket):
        await store.ws_connect(ws)

    return app


app = create_app()
