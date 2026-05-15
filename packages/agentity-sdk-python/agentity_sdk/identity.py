import hashlib
import base64
import json
from datetime import datetime, timedelta, timezone
from typing import Optional
from pydantic import BaseModel, field_serializer

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, PrivateFormat, NoEncryption
from cryptography.exceptions import InvalidSignature

from .errors import AgentityError


class AidStatus:
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class OwnerRef(BaseModel):
    did: str
    type: str = "human"


class ModelInfo(BaseModel):
    provider: str
    name: str
    version: str


class Proof(BaseModel):
    type: str = "Ed25519Signature2020"
    created: datetime
    proofValue: str

    @field_serializer("created")
    def serialize_dt(self, dt: datetime) -> str:
        return dt.isoformat().replace("+00:00", "Z")


class AgentIdentity(BaseModel):
    did: str
    version: str = "1"
    specVersion: str = "0.1"
    created: datetime
    expires: datetime
    owner: OwnerRef
    parent: Optional[str] = None
    previousAid: Optional[str] = None
    delegationDepth: int = 0
    model: Optional[ModelInfo] = None
    scope: list[str]
    publicKey: dict
    status: str = AidStatus.ACTIVE
    proof: Optional[Proof] = None

    @field_serializer("created", "expires")
    def serialize_dt(self, dt: datetime) -> str:
        return dt.isoformat().replace("+00:00", "Z")

    @staticmethod
    def _json_default(obj):
        if isinstance(obj, datetime):
            return obj.isoformat().replace("+00:00", "Z")
        if isinstance(obj, Proof):
            return {
                "type": obj.type,
                "created": obj.created.isoformat().replace("+00:00", "Z"),
                "proofValue": obj.proofValue,
            }
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    @field_serializer("proof")
    def serialize_proof(self, p: Optional[Proof]) -> Optional[dict]:
        if p is None:
            return None
        return {
            "type": p.type,
            "created": p.created.isoformat().replace("+00:00", "Z"),
            "proofValue": p.proofValue,
        }

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires

    def verify_signature(self) -> bool:
        if not self.proof:
            return False
        payload = self._signing_payload()
        try:
            key_bytes = base64.urlsafe_b64decode(self.publicKey["value"] + "==")
            pub_key = Ed25519PublicKey.from_public_bytes(key_bytes)
            sig_bytes = base64.urlsafe_b64decode(self.proof.proofValue + "==")
            pub_key.verify(sig_bytes, payload)
            return True
        except (InvalidSignature, Exception):
            return False

    def _signing_payload(self) -> bytes:
        data = (
            f"{self.did}:{self.version}:"
            f"{self.created.isoformat().replace('+00:00', 'Z')}:"
            f"{self.expires.isoformat().replace('+00:00', 'Z')}:"
            f"{','.join(sorted(self.scope))}:{self.owner.did}"
        )
        return data.encode()

    def encode_token(self, kp: "AgentKeyPair", nonce: str, timestamp: str,
                     method: str, path: str, body_hash: Optional[str] = None) -> str:
        aid_json = json.dumps(self.model_dump(), separators=(",", ":"), default=self._json_default)
        aid_b64 = base64.urlsafe_b64encode(aid_json.encode()).decode().rstrip("=")
        sig = kp.sign_request(self.did, nonce, timestamp, method, path, body_hash)
        return f"{aid_b64}.{sig}"

    @staticmethod
    def decode_token(token: str) -> tuple["AgentIdentity", str]:
        parts = token.split(".", 1)
        if len(parts) != 2:
            raise AgentityError("Invalid token format")
        pad = 4 - len(parts[0]) % 4
        if pad != 4:
            parts[0] += "=" * pad
        aid_json = base64.urlsafe_b64decode(parts[0])
        aid = AgentIdentity(**json.loads(aid_json))
        return aid, parts[1]


class AgentKeyPair:
    def __init__(self, private_key: Optional[Ed25519PrivateKey] = None):
        self._private_key = private_key or Ed25519PrivateKey.generate()
        self._public_key = self._private_key.public_key()

    @classmethod
    def from_bytes(cls, secret: bytes) -> "AgentKeyPair":
        if len(secret) != 32:
            raise AgentityError("Invalid secret key length")
        priv_key = Ed25519PrivateKey.from_private_bytes(secret)
        return cls(priv_key)

    def public_key_bytes(self) -> bytes:
        return self._public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)

    def public_key_b64(self) -> str:
        return base64.urlsafe_b64encode(self.public_key_bytes()).decode().rstrip("=")

    def secret_key_b64(self) -> str:
        raw = self._private_key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
        return base64.urlsafe_b64encode(raw).decode().rstrip("=")

    def fingerprint(self) -> str:
        h = hashlib.sha256(self.public_key_bytes()).digest()
        alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        n = int.from_bytes(h, "big")
        if n == 0:
            return alphabet[0]
        result = []
        while n > 0:
            n, rem = divmod(n, 58)
            result.append(alphabet[rem])
        return "".join(reversed(result))

    def sign(self, payload: bytes) -> str:
        sig = self._private_key.sign(payload)
        return base64.urlsafe_b64encode(sig).decode().rstrip("=")

    def sign_request(self, did: str, nonce: str, timestamp: str,
                     method: str, path: str, body_hash: Optional[str] = None) -> str:
        payload = f"{did}:{nonce}:{timestamp}:{method}:{path}:{body_hash or ''}"
        return self.sign(payload.encode())

    @staticmethod
    def verify(public_key_b64: str, payload: bytes, sig_b64: str) -> bool:
        try:
            pad = 4 - len(public_key_b64) % 4
            key_bytes = base64.urlsafe_b64decode(public_key_b64 + ("=" * pad if pad != 4 else ""))
            pub_key = Ed25519PublicKey.from_public_bytes(key_bytes)
            pad = 4 - len(sig_b64) % 4
            sig_bytes = base64.urlsafe_b64decode(sig_b64 + ("=" * pad if pad != 4 else ""))
            pub_key.verify(sig_bytes, payload)
            return True
        except (InvalidSignature, Exception):
            return False

    @staticmethod
    def verify_request(public_key_b64: str, did: str, nonce: str, timestamp: str,
                       method: str, path: str, body_hash: Optional[str], sig_b64: str) -> bool:
        payload = f"{did}:{nonce}:{timestamp}:{method}:{path}:{body_hash or ''}"
        return AgentKeyPair.verify(public_key_b64, payload.encode(), sig_b64)

    def rotate(self, previous_aid: "AgentIdentity", ttl_days: int = 90) -> "AgentIdentity":
        """Generate a new keypair and create a new AID with version+1 referencing the old one."""
        new_kp = AgentKeyPair()
        new_did = AgentDid.from_keypair(new_kp)
        now = datetime.now(timezone.utc)
        expires = now + timedelta(days=ttl_days)
        old_version = int(previous_aid.version)
        new_aid = AgentIdentity(
            did=new_did.as_str(),
            version=str(old_version + 1),
            specVersion=previous_aid.specVersion,
            created=now,
            expires=expires,
            owner=previous_aid.owner,
            parent=previous_aid.parent,
            delegationDepth=previous_aid.delegationDepth,
            model=previous_aid.model,
            scope=previous_aid.scope.copy(),
            publicKey={"type": "Ed25519VerificationKey2020", "value": new_kp.public_key_b64()},
            previousAid=previous_aid.did,
        )
        payload = new_aid._signing_payload()
        proof_value = new_kp.sign(payload)
        new_aid.proof = Proof(created=now, proofValue=proof_value)
        return new_aid

    def create_identity(self, owner_did: str, scopes: list[str],
                        ttl_days: int = 30, parent: Optional[str] = None,
                        delegation_depth: int = 0,
                        model: Optional[ModelInfo] = None) -> AgentIdentity:
        did = AgentDid.from_keypair(self)
        now = datetime.now(timezone.utc)
        expires = now + timedelta(days=ttl_days)

        aid = AgentIdentity(
            did=did.as_str(),
            created=now,
            expires=expires,
            owner=OwnerRef(did=owner_did),
            parent=parent,
            delegationDepth=delegation_depth,
            model=model,
            scope=scopes,
            publicKey={"type": "Ed25519VerificationKey2020", "value": self.public_key_b64()},
        )
        payload = aid._signing_payload()
        proof_value = self.sign(payload)
        aid.proof = Proof(created=now, proofValue=proof_value)
        return aid


class AgentDid:
    def __init__(self, did: str):
        self.did = did

    @classmethod
    def from_keypair(cls, kp: AgentKeyPair) -> "AgentDid":
        return cls(f"did:agentity:agent:{kp.fingerprint()}")

    @classmethod
    def from_parts(cls, did_type: str, fingerprint: str) -> "AgentDid":
        return cls(f"did:agentity:{did_type}:{fingerprint}")

    def as_str(self) -> str:
        return self.did

    def __str__(self) -> str:
        return self.did
