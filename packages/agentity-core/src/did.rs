use crate::crypto::AgentKeyPair;

#[derive(Debug, Clone)]
pub struct AgentDid(pub String);

impl AgentDid {
    pub fn from_keypair(kp: &AgentKeyPair) -> Self {
        Self(format!("did:agentity:agent:{}", kp.fingerprint()))
    }

    pub fn from_parts(did_type: &str, fingerprint: &str) -> Self {
        Self(format!("did:agentity:{}:{}", did_type, fingerprint))
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }

    pub fn fingerprint(&self) -> Option<&str> {
        self.0.rsplit(':').next()
    }

    pub fn entity_type(&self) -> Option<&str> {
        let parts: Vec<&str> = self.0.split(':').collect();
        if parts.len() >= 3 {
            Some(parts[2])
        } else {
            None
        }
    }
}

impl std::fmt::Display for AgentDid {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        write!(f, "{}", self.0)
    }
}

impl PartialEq for AgentDid {
    fn eq(&self, other: &Self) -> bool {
        self.0 == other.0
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::crypto::AgentKeyPair;

    #[test]
    fn test_did_format() {
        let kp = AgentKeyPair::generate();
        let did = AgentDid::from_keypair(&kp);
        assert!(did.as_str().starts_with("did:agentity:agent:"));
        assert_eq!(did.entity_type(), Some("agent"));
    }

    #[test]
    fn test_did_fingerprint() {
        let kp = AgentKeyPair::generate();
        let did = AgentDid::from_keypair(&kp);
        assert_eq!(did.fingerprint(), Some(kp.fingerprint().as_str()));
    }

    #[test]
    fn test_did_from_parts() {
        let did = AgentDid::from_parts("human", "abc123");
        assert_eq!(did.as_str(), "did:agentity:human:abc123");
        assert_eq!(did.entity_type(), Some("human"));
    }
}
