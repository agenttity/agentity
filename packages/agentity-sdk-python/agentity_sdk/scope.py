from enum import Enum
from typing import Optional
from pydantic import BaseModel


class ScopeRisk(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ScopeEntry(BaseModel):
    id: str
    description: str
    risk: ScopeRisk
    requires: list[str] = []


class ManifestSignature(BaseModel):
    type: str = "Ed25519Signature2020"
    created: str
    proofValue: str


class ProviderManifest(BaseModel):
    provider: str
    name: str
    description: Optional[str] = None
    specVersion: str = "0.1"
    baseUrl: Optional[str] = None
    scopes: list[ScopeEntry]
    signature: Optional[ManifestSignature] = None

    @staticmethod
    def scope_matches(needle: str, haystack: str) -> bool:
        if haystack in ("*:*:*", "*"):
            return True
        needle_parts = needle.split(":", 2)
        hay_parts = haystack.split(":", 2)
        if len(needle_parts) != len(hay_parts):
            return False
        for n, h in zip(needle_parts, hay_parts):
            if h == "*":
                continue
            if n != h:
                return False
        return True

    def verify_scope(self, scope: str) -> bool:
        return any(self.scope_matches(scope, s.id) for s in self.scopes)

    def validate_scopes(self, agent_scopes: list[str]) -> list[str]:
        invalid = [s for s in agent_scopes if not self.verify_scope(s)]
        return invalid
