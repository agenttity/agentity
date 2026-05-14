use crate::{AgentDid, AgentKeyPair, AgentityError};
use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase")]
pub enum AidStatus {
    Active,
    Revoked,
    Expired,
}

impl std::fmt::Display for AidStatus {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            AidStatus::Active => write!(f, "active"),
            AidStatus::Revoked => write!(f, "revoked"),
            AidStatus::Expired => write!(f, "expired"),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OwnerRef {
    pub did: String,
    #[serde(rename = "type")]
    pub owner_type: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ModelInfo {
    pub provider: String,
    pub name: String,
    pub version: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PublicKeyInfo {
    #[serde(rename = "type")]
    pub key_type: String,
    pub value: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Proof {
    #[serde(rename = "type")]
    pub proof_type: String,
    pub created: DateTime<Utc>,
    pub proof_value: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AgentIdentityDocument {
    pub did: String,
    pub version: String,
    pub spec_version: String,
    pub created: DateTime<Utc>,
    pub expires: DateTime<Utc>,
    pub owner: OwnerRef,
    pub parent: Option<String>,
    pub delegation_depth: u8,
    pub model: Option<ModelInfo>,
    pub scope: Vec<String>,
    pub public_key: PublicKeyInfo,
    pub status: AidStatus,
    pub proof: Option<Proof>,
}

impl AgentIdentityDocument {
    pub fn new(
        kp: &AgentKeyPair,
        owner_did: &str,
        scope: Vec<String>,
        ttl_days: i64,
        parent: Option<String>,
        delegation_depth: u8,
        model: Option<ModelInfo>,
    ) -> Result<Self, AgentityError> {
        if delegation_depth > 10 {
            return Err(AgentityError::DelegationDepthExceeded);
        }
        let did = AgentDid::from_keypair(kp);
        let now = Utc::now();
        let expires = now + chrono::Duration::days(ttl_days);

        let mut aid = Self {
            did: did.to_string(),
            version: "1".into(),
            spec_version: "0.1".into(),
            created: now,
            expires,
            owner: OwnerRef {
                did: owner_did.to_string(),
                owner_type: "human".into(),
            },
            parent,
            delegation_depth,
            model,
            scope,
            public_key: PublicKeyInfo {
                key_type: "Ed25519VerificationKey2020".into(),
                value: kp.public_key_b64(),
            },
            status: AidStatus::Active,
            proof: None,
        };

        let payload = aid.signing_payload()?;
        let proof_value = kp.sign(&payload);
        aid.proof = Some(Proof {
            proof_type: "Ed25519Signature2020".into(),
            created: now,
            proof_value,
        });
        Ok(aid)
    }

    fn signing_payload(&self) -> Result<Vec<u8>, AgentityError> {
        #[derive(Serialize)]
        struct AidWithoutProof<'a> {
            did: &'a str,
            version: &'a str,
            created: &'a DateTime<Utc>,
            expires: &'a DateTime<Utc>,
            scope: &'a Vec<String>,
            owner_did: &'a str,
        }
        let payload = AidWithoutProof {
            did: &self.did,
            version: &self.version,
            created: &self.created,
            expires: &self.expires,
            scope: &self.scope,
            owner_did: &self.owner.did,
        };
        Ok(serde_json::to_vec(&payload)?)
    }

    pub fn is_expired(&self) -> bool {
        Utc::now() > self.expires
    }

    pub fn verify_signature(&self) -> bool {
        if let Some(proof) = &self.proof {
            if let Ok(payload) = self.signing_payload() {
                return AgentKeyPair::verify(&self.public_key.value, &payload, &proof.proof_value);
            }
        }
        false
    }

    pub fn encode_token(
        &self,
        kp: &AgentKeyPair,
        nonce: &str,
        timestamp: &str,
        method: &str,
        path: &str,
        body_hash: Option<&str>,
    ) -> String {
        let aid_json = serde_json::to_string(self).unwrap_or_default();
        let aid_b64 = URL_SAFE_NO_PAD.encode(aid_json);
        let sig = kp.sign_request(&self.did, nonce, timestamp, method, path, body_hash);
        format!("{}.{}", aid_b64, sig)
    }

    pub fn decode_token(token: &str) -> Option<(Self, String)> {
        let parts: Vec<&str> = token.splitn(2, '.').collect();
        if parts.len() != 2 {
            return None;
        }
        let aid_json = URL_SAFE_NO_PAD.decode(parts[0]).ok()?;
        let aid: Self = serde_json::from_slice(&aid_json).ok()?;
        Some((aid, parts[1].to_string()))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::AgentKeyPair;

    #[test]
    fn test_aid_creation_and_verification() {
        let kp = AgentKeyPair::generate();
        let aid = AgentIdentityDocument::new(
            &kp,
            "did:agentity:human:owner123",
            vec!["stripe:payments:read".into()],
            30,
            None,
            0,
            None,
        )
        .unwrap();
        assert!(aid.verify_signature());
        assert!(!aid.is_expired());
        assert_eq!(aid.status, AidStatus::Active);
    }

    #[test]
    fn test_delegation_depth_limit() {
        let kp = AgentKeyPair::generate();
        let result =
            AgentIdentityDocument::new(&kp, "did:agentity:human:owner", vec![], 30, None, 11, None);
        assert!(result.is_err());
    }

    #[test]
    fn test_aid_with_model() {
        let kp = AgentKeyPair::generate();
        let model = ModelInfo {
            provider: "anthropic".into(),
            name: "claude-sonnet-4-6".into(),
            version: "20251001".into(),
        };
        let aid = AgentIdentityDocument::new(
            &kp,
            "did:agentity:human:owner",
            vec!["calendar:events:write".into()],
            30,
            None,
            0,
            Some(model),
        )
        .unwrap();
        assert!(aid.verify_signature());
        assert_eq!(aid.model.as_ref().unwrap().provider, "anthropic");
    }

    #[test]
    fn test_aid_with_parent() {
        let kp = AgentKeyPair::generate();
        let aid = AgentIdentityDocument::new(
            &kp,
            "did:agentity:human:owner",
            vec!["stripe:payments:read".into()],
            30,
            Some("did:agentity:agent:parent123".into()),
            1,
            None,
        )
        .unwrap();
        assert_eq!(aid.parent, Some("did:agentity:agent:parent123".into()));
        assert_eq!(aid.delegation_depth, 1);
    }

    #[test]
    fn test_encode_decode_token() {
        let kp = AgentKeyPair::generate();
        let aid = AgentIdentityDocument::new(
            &kp,
            "did:agentity:human:alice",
            vec!["test:read".into()],
            30,
            None,
            0,
            None,
        )
        .unwrap();
        let token = aid.encode_token(
            &kp,
            "nonce-123",
            "2026-05-08T12:00:00Z",
            "GET",
            "/api/data",
            None,
        );
        let (decoded_aid, sig) = AgentIdentityDocument::decode_token(&token).unwrap();
        assert_eq!(decoded_aid.did, aid.did);
        assert_eq!(decoded_aid.scope, aid.scope);
        assert!(!sig.is_empty());
    }
}
