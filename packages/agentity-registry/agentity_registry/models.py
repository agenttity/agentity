from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AgentStatus(BaseModel):
    did: str
    status: str
    updatedAt: datetime


class AgentInfo(BaseModel):
    did: str
    status: str
    owner_did: str
    scopes: list[str] = []
    created_at: datetime
    expires_at: Optional[datetime] = None


class RevokeRequest(BaseModel):
    did: str
    reason: str
    cascade: bool = True


class AuditEntry(BaseModel):
    did: str
    event: str
    timestamp: datetime
    actor: Optional[str] = None
    reason: Optional[str] = None


class RegisterRequest(BaseModel):
    did: str
    aid_json: str
    public_key_b64: str
    scopes: list[str] = []
    owner_did: str
    ttl_days: int = 30
