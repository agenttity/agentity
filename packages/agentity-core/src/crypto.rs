use ed25519_dalek::{SigningKey, VerifyingKey, Signer, Verifier, Signature};
use rand::rngs::OsRng;
use sha2::{Sha256, Digest};
use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine};
use crate::error::AgentityError;

pub struct AgentKeyPair {
    pub signing_key: SigningKey,
    pub verifying_key: VerifyingKey,
}

impl AgentKeyPair {
    pub fn generate() -> Self {
        let signing_key = SigningKey::generate(&mut OsRng);
        let verifying_key = signing_key.verifying_key();
        Self { signing_key, verifying_key }
    }

    pub fn from_bytes(secret: &[u8]) -> Result<Self, AgentityError> {
        let secret_array: [u8; 32] = secret.try_into()
            .map_err(|_| AgentityError::Crypto("Invalid secret key length".into()))?;
        let signing_key = SigningKey::from_bytes(&secret_array);
        let verifying_key = signing_key.verifying_key();
        Ok(Self { signing_key, verifying_key })
    }

    pub fn public_key_bytes(&self) -> [u8; 32] {
        self.verifying_key.to_bytes()
    }

    pub fn public_key_b64(&self) -> String {
        URL_SAFE_NO_PAD.encode(self.verifying_key.as_bytes())
    }

    pub fn secret_key_b64(&self) -> String {
        URL_SAFE_NO_PAD.encode(self.signing_key.to_bytes())
    }

    pub fn fingerprint(&self) -> String {
        let hash = Sha256::digest(self.verifying_key.as_bytes());
        bs58::encode(hash).into_string()
    }

    pub fn sign(&self, payload: &[u8]) -> String {
        let sig: Signature = self.signing_key.sign(payload);
        URL_SAFE_NO_PAD.encode(sig.to_bytes())
    }

    pub fn verify(public_key_b64: &str, payload: &[u8], sig_b64: &str) -> bool {
        let pk_bytes = match URL_SAFE_NO_PAD.decode(public_key_b64) {
            Ok(b) => b,
            Err(_) => return false,
        };
        let sig_bytes = match URL_SAFE_NO_PAD.decode(sig_b64) {
            Ok(b) => b,
            Err(_) => return false,
        };
        let pk_array: [u8; 32] = match pk_bytes.as_slice().try_into() {
            Ok(arr) => arr,
            Err(_) => return false,
        };
        let vk = match VerifyingKey::from_bytes(&pk_array) {
            Ok(vk) => vk,
            Err(_) => return false,
        };
        let sig = match Signature::from_slice(&sig_bytes) {
            Ok(s) => s,
            Err(_) => return false,
        };
        vk.verify(payload, &sig).is_ok()
    }

    pub fn sign_request(
        &self,
        did: &str,
        nonce: &str,
        timestamp: &str,
        method: &str,
        path: &str,
        body_hash: Option<&str>,
    ) -> String {
        let payload = format!("{}:{}:{}:{}:{}:{}", did, nonce, timestamp, method, path, body_hash.unwrap_or(""));
        self.sign(payload.as_bytes())
    }

    #[allow(clippy::too_many_arguments)]
    pub fn verify_request(
        public_key_b64: &str,
        did: &str,
        nonce: &str,
        timestamp: &str,
        method: &str,
        path: &str,
        body_hash: Option<&str>,
        sig_b64: &str,
    ) -> bool {
        let payload = format!("{}:{}:{}:{}:{}:{}", did, nonce, timestamp, method, path, body_hash.unwrap_or(""));
        Self::verify(public_key_b64, payload.as_bytes(), sig_b64)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_keypair_generation() {
        let kp = AgentKeyPair::generate();
        assert_eq!(kp.public_key_bytes().len(), 32);
        assert!(!kp.fingerprint().is_empty());
    }

    #[test]
    fn test_sign_and_verify() {
        let kp = AgentKeyPair::generate();
        let msg = b"hello world";
        let sig = kp.sign(msg);
        assert!(AgentKeyPair::verify(&kp.public_key_b64(), msg, &sig));
    }

    #[test]
    fn test_verify_bad_signature() {
        let kp = AgentKeyPair::generate();
        let msg = b"hello world";
        assert!(!AgentKeyPair::verify(&kp.public_key_b64(), msg, "bad"));
    }

    #[test]
    fn test_sign_request_roundtrip() {
        let kp = AgentKeyPair::generate();
        let did = "did:agentity:agent:test123";
        let nonce = uuid::Uuid::new_v4().to_string();
        let timestamp = "2026-05-08T12:00:00Z";
        let sig = kp.sign_request(did, &nonce, timestamp, "GET", "/api/resource", None);
        assert!(AgentKeyPair::verify_request(
            &kp.public_key_b64(), did, &nonce, timestamp, "GET", "/api/resource", None, &sig
        ));
    }

    #[test]
    fn test_from_bytes_deterministic() {
        let secret = [0u8; 32];
        let kp1 = AgentKeyPair::from_bytes(&secret).unwrap();
        let kp2 = AgentKeyPair::from_bytes(&secret).unwrap();
        assert_eq!(kp1.public_key_b64(), kp2.public_key_b64());
        assert_eq!(kp1.fingerprint(), kp2.fingerprint());
    }
}
