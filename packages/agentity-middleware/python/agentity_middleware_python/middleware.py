import hashlib
from typing import Optional, Set
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from agentity_sdk import AgentKeyPair, AgentIdentity


class AgentityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, registry_url: Optional[str] = None, tolerance_seconds: int = 300):
        super().__init__(app)
        self._registry_url = registry_url
        self._tolerance = tolerance_seconds
        self._used_nonces: Set[str] = set()

    async def dispatch(self, request: Request, call_next):
        if request.url.path in ("/health", "/docs", "/openapi.json"):
            return await call_next(request)

        token = request.headers.get("Agentity-Token")
        nonce = request.headers.get("Agentity-Nonce")
        timestamp = request.headers.get("Agentity-Timestamp")

        if not all([token, nonce, timestamp]):
            return JSONResponse(status_code=401, content={"detail": "Missing Agentity headers"})

        if nonce in self._used_nonces:
            return JSONResponse(status_code=403, content={"detail": "Nonce replayed"})

        from datetime import datetime, timezone
        try:
            ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            if abs((now - ts).total_seconds()) > self._tolerance:
                return JSONResponse(status_code=403, content={"detail": "Timestamp out of tolerance"})
        except ValueError:
            return JSONResponse(status_code=400, content={"detail": "Invalid timestamp format"})

        try:
            aid, sig = AgentIdentity.decode_token(token)
        except Exception:
            return JSONResponse(status_code=400, content={"detail": "Invalid token format"})

        if aid.is_expired():
            return JSONResponse(status_code=403, content={"detail": "AID expired"})

        body = await request.body()
        body_hash = hashlib.sha256(body).hexdigest() if body else None
        valid = AgentKeyPair.verify_request(
            aid.publicKey["value"], aid.did, nonce, timestamp,
            request.method, str(request.url.path), body_hash, sig,
        )
        if not valid:
            return JSONResponse(status_code=403, content={"detail": "Invalid signature"})

        if self._registry_url:
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{self._registry_url}/did/{aid.did}/status")
                if resp.status_code != 200:
                    return JSONResponse(status_code=403, content={"detail": "AID not found in registry"})
                status = resp.json().get("status")
                if status != "active":
                    return JSONResponse(status_code=403, content={"detail": f"AID status is {status}"})

        self._used_nonces.add(nonce)
        request.state.agent_did = aid.did
        request.state.agent_scopes = aid.scope
        return await call_next(request)
