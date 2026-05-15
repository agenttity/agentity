"""FastAPI router for Agentity OIDC authentication."""

import json
import os
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from httpx import AsyncClient

from .models import OwnerInfo, VerifiedSession
from .providers import get_provider

router = APIRouter(prefix="/auth", tags=["auth"])

# In-memory session store (use Redis in production)
_sessions: dict[str, dict] = {}
_verified_owners: dict[str, OwnerInfo] = {}
SESSION_TTL = timedelta(hours=1)


def _generate_session_token() -> str:
    return secrets.token_urlsafe(32)


@router.get("/login/{provider}")
async def login(provider: str, redirect_uri: Optional[str] = None):
    try:
        cfg = get_provider(provider)
    except ValueError as e:
        raise HTTPException(404, detail=str(e))
    if not cfg.client_id:
        raise HTTPException(503, detail=f"OAuth2 not configured for {provider}")

    state = secrets.token_urlsafe(16)
    redirect = redirect_uri or cfg.redirect_uri.format(provider=provider)

    _sessions[state] = {"provider": provider, "redirect_uri": redirect, "created_at": datetime.now(timezone.utc)}

    if provider == "github":
        authorize_url = (
            f"{cfg.authorize_url}?client_id={cfg.client_id}"
            f"&redirect_uri={redirect}&state={state}&scope={cfg.scope}"
        )
    else:
        authorize_url = (
            f"{cfg.authorize_url}?client_id={cfg.client_id}"
            f"&redirect_uri={redirect}&response_type=code"
            f"&state={state}&scope={cfg.scope.replace(' ', '+')}"
        )
    return RedirectResponse(url=authorize_url)


@router.get("/callback/{provider}")
async def callback(provider: str, code: str, state: str, request: Request):
    session = _sessions.pop(state, None)
    if not session:
        raise HTTPException(400, detail="Invalid or expired state")

    cfg = get_provider(provider)
    redirect_uri = session["redirect_uri"]

    async with AsyncClient() as client:
        token_resp = await client.post(
            cfg.token_url,
            data={
                "client_id": cfg.client_id,
                "client_secret": cfg.client_secret,
                "code": code,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
            headers={"Accept": "application/json"},
        )
        if token_resp.status_code != 200:
            raise HTTPException(401, detail="Failed to exchange authorization code")

        token_data = token_resp.json()
        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(401, detail="No access_token in response")

        userinfo_resp = await client.get(
            cfg.userinfo_url,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if userinfo_resp.status_code != 200:
            raise HTTPException(401, detail="Failed to fetch user info")

        userinfo = userinfo_resp.json()

    sub = userinfo.get("sub") or str(userinfo.get("id"))
    email = userinfo.get("email") or ""
    name = userinfo.get("name") or userinfo.get("login") or email
    email_verified = userinfo.get("email_verified", False)

    owner_did = f"did:agentity:human:{provider}:{sub}"
    owner = OwnerInfo(
        did=owner_did,
        provider=provider,
        provider_sub=sub,
        email=email,
        name=name,
        verified=bool(email_verified),
    )

    session_token = _generate_session_token()
    _verified_owners[session_token] = owner

    html = f"""<!DOCTYPE html>
<html><body style="font-family:system-ui;padding:2rem;text-align:center">
<h2>✓ Authentifié</h2>
<p>DID : <code>{owner.did}</code></p>
<p>Email : {email} {('✅' if email_verified else '⚠️ non vérifié')}</p>
<p style="font-size:0.85rem;color:#666">Tu peux fermer cette fenêtre.</p>
</body></html>"""
    return HTMLResponse(html)


@router.get("/session/{session_token}")
async def get_session(session_token: str):
    owner = _verified_owners.get(session_token)
    if not owner:
        raise HTTPException(404, detail="Session not found or expired")
    return owner


@router.get("/me")
async def me(request: Request):
    token = request.headers.get("Agentity-Session")
    if not token:
        raise HTTPException(401, detail="Missing Agentity-Session header")
    owner = _verified_owners.get(token)
    if not owner:
        raise HTTPException(404, detail="Session not found or expired")
    return owner


@router.post("/register-verified")
async def register_verified(request: Request):
    session_token = request.headers.get("Agentity-Session")
    if not session_token:
        raise HTTPException(401, detail="Missing Agentity-Session header")
    owner = _verified_owners.get(session_token)
    if not owner:
        raise HTTPException(404, detail="Session not found or expired")

    body = await request.json()
    agent_did = body.get("did")
    owner_did = body.get("owner_did")

    if owner_did != owner.did:
        raise HTTPException(403, detail=f"owner_did mismatch: got {owner_did}, expected {owner.did}")

    return {"status": "verified", "did": agent_did, "owner": owner.model_dump()}
