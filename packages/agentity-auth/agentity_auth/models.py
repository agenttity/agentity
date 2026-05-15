from pydantic import BaseModel
from typing import Optional


class ProviderConfig(BaseModel):
    client_id: str
    client_secret: str
    authorize_url: str
    token_url: str
    userinfo_url: str
    scope: str = "openid email profile"
    redirect_uri: str = "http://localhost:8765/auth/callback/{provider}"


class OwnerInfo(BaseModel):
    did: str
    provider: str
    provider_sub: str
    email: str
    name: str
    verified: bool


class VerifiedSession(BaseModel):
    session_token: str
    owner: OwnerInfo
    expires_at: str
