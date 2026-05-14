import hashlib
import uuid
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass

from .identity import AgentIdentity, AgentKeyPair


@dataclass
class AgentityToken:
    aid: AgentIdentity
    signature: str
    nonce: str
    timestamp: str


class RequestSigner:
    def __init__(self, keypair: AgentKeyPair, identity: AgentIdentity):
        self._kp = keypair
        self._aid = identity

    def sign_request(self, method: str, path: str, body: Optional[bytes] = None) -> dict[str, str]:
        nonce = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        body_hash = hashlib.sha256(body or b"").hexdigest() if body else None
        token = self._aid.encode_token(self._kp, nonce, timestamp, method, path, body_hash)
        return {
            "Agentity-Token": token,
            "Agentity-Nonce": nonce,
            "Agentity-Timestamp": timestamp,
        }

    def sign_headers(self, url: str, method: str = "GET", body: Optional[bytes] = None) -> dict[str, str]:
        from urllib.parse import urlparse
        path = urlparse(url).path
        return self.sign_request(method, path, body)


class RequestVerifier:
    @staticmethod
    def verify_request(
        headers: dict[str, str],
        method: str,
        path: str,
        body: Optional[bytes] = None,
        tolerance_seconds: int = 300,
        used_nonces: Optional[set[str]] = None,
    ) -> AgentIdentity:
        token_str = headers.get("Agentity-Token")
        nonce = headers.get("Agentity-Nonce")
        timestamp = headers.get("Agentity-Timestamp")

        if not all([token_str, nonce, timestamp]):
            raise PermissionError("Missing Agentity headers")

        if used_nonces is not None and nonce in used_nonces:
            raise PermissionError("Nonce already used (replay attack)")

        ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        if abs((now - ts).total_seconds()) > tolerance_seconds:
            raise PermissionError("Timestamp out of tolerance")

        aid, sig = AgentIdentity.decode_token(token_str)

        if aid.is_expired():
            raise PermissionError("AID expired")

        if aid.status != AidStatus.ACTIVE:
            raise PermissionError(f"AID status is {aid.status}")

        body_hash = hashlib.sha256(body or b"").hexdigest() if body else None
        valid = AgentKeyPair.verify_request(
            aid.publicKey["value"], aid.did, nonce, timestamp, method, path, body_hash, sig,
        )
        if not valid:
            raise PermissionError("Invalid signature")

        if used_nonces is not None:
            used_nonces.add(nonce)

        return aid


class AidStatus:
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"
