from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AgentStatus(BaseModel):
    did: str
    status: str  # active | revoked | expired
    updatedAt: datetime


class RevokeRequest(BaseModel):
    did: str
    reason: str
    cascade: bool = True


class AuditEntry(BaseModel):
    did: str
    event: str  # created | revoked | rotated
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
