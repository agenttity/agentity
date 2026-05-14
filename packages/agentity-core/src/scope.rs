use crate::{AgentKeyPair, AgentityError};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase")]
pub enum ScopeRisk {
    Low,
    Medium,
    High,
    Critical,
}

impl std::fmt::Display for ScopeRisk {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            ScopeRisk::Low => write!(f, "low"),
            ScopeRisk::Medium => write!(f, "medium"),
            ScopeRisk::High => write!(f, "high"),
            ScopeRisk::Critical => write!(f, "critical"),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ScopeEntry {
    pub id: String,
    pub description: String,
    pub risk: ScopeRisk,
    #[serde(default)]
    pub requires: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ProviderManifest {
    pub provider: String,
    pub name: String,
    pub description: Option<String>,
    pub spec_version: String,
    pub base_url: Option<String>,
    pub scopes: Vec<ScopeEntry>,
    pub signature: Option<ManifestSignature>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ManifestSignature {
    #[serde(rename = "type")]
    pub sig_type: String,
    pub created: String,
    pub proof_value: String,
}

impl ProviderManifest {
    pub fn new(provider: &str, name: &str) -> Self {
        Self {
            provider: provider.to_string(),
            name: name.to_string(),
            description: None,
            spec_version: "0.1".into(),
            base_url: None,
            scopes: vec![],
            signature: None,
        }
    }

    pub fn add_scope(
        &mut self,
        id: &str,
        description: &str,
        risk: ScopeRisk,
        requires: Vec<String>,
    ) {
        self.scopes.push(ScopeEntry {
            id: id.to_string(),
            description: description.to_string(),
            risk,
            requires,
        });
    }

    pub fn sign(&mut self, kp: &AgentKeyPair) -> Result<(), AgentityError> {
        let payload = serde_json::to_vec(&self.scopes)?;
        let proof_value = kp.sign(&payload);
        self.signature = Some(ManifestSignature {
            sig_type: "Ed25519Signature2020".into(),
            created: chrono::Utc::now().to_rfc3339(),
            proof_value,
        });
        Ok(())
    }

    pub fn verify_scope(scope: &str, allowed_scopes: &[String]) -> bool {
        let parts: Vec<&str> = scope.splitn(3, ':').collect();
        if parts.len() != 3 {
            return false;
        }
        for allowed in allowed_scopes {
            if scope_matches(scope, allowed) {
                return true;
            }
        }
        false
    }

    pub fn has_scope(agent_scopes: &[String], required_scope: &str) -> bool {
        agent_scopes
            .iter()
            .any(|s| scope_matches(required_scope, s))
    }

    pub fn validate_scopes(
        agent_scopes: &[String],
        manifest_scopes: &[ScopeEntry],
    ) -> Result<(), AgentityError> {
        let manifest_ids: Vec<String> = manifest_scopes.iter().map(|s| s.id.clone()).collect();
        for scope in agent_scopes {
            if !Self::verify_scope(scope, &manifest_ids) {
                return Err(AgentityError::InvalidScope(scope.clone()));
            }
        }
        Ok(())
    }
}

fn scope_matches(needle: &str, haystack: &str) -> bool {
    if haystack == "*:*:*" || haystack == "*" {
        return true;
    }
    let needle_parts: Vec<&str> = needle.splitn(3, ':').collect();
    let hay_parts: Vec<&str> = haystack.splitn(3, ':').collect();

    for (n, h) in needle_parts.iter().zip(hay_parts.iter()) {
        if *h == "*" {
            continue;
        }
        if n != h {
            return false;
        }
    }
    // If haystack has fewer parts but all matched, it's a prefix match
    needle_parts.len() == hay_parts.len()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_scope_matching_exact() {
        assert!(scope_matches(
            "stripe:payments:read",
            "stripe:payments:read"
        ));
        assert!(!scope_matches(
            "stripe:payments:read",
            "stripe:payments:write"
        ));
    }

    #[test]
    fn test_scope_matching_wildcard() {
        assert!(scope_matches("stripe:payments:read", "stripe:payments:*"));
        assert!(scope_matches("stripe:payments:write", "stripe:payments:*"));
        assert!(scope_matches("stripe:payments:read", "stripe:*:*"));
        assert!(scope_matches("stripe:payments:read", "*:*:*"));
    }

    #[test]
    fn test_verify_scope() {
        let allowed = vec![
            "stripe:payments:read".to_string(),
            "calendar:*:*".to_string(),
        ];
        assert!(ProviderManifest::verify_scope(
            "stripe:payments:read",
            &allowed
        ));
        assert!(ProviderManifest::verify_scope(
            "calendar:events:write",
            &allowed
        ));
        assert!(!ProviderManifest::verify_scope(
            "stripe:payments:write",
            &allowed
        ));
    }

    #[test]
    fn test_manifest_validation() {
        let mut manifest = ProviderManifest::new("did:agentity:provider:test", "Test API");
        manifest.add_scope("test:data:read", "Read data", ScopeRisk::Low, vec![]);
        manifest.add_scope(
            "test:data:write",
            "Write data",
            ScopeRisk::High,
            vec!["test:data:read".into()],
        );

        let valid_scopes = vec!["test:data:read".to_string()];
        assert!(ProviderManifest::validate_scopes(&valid_scopes, &manifest.scopes).is_ok());

        let invalid_scopes = vec!["test:other:action".to_string()];
        assert!(ProviderManifest::validate_scopes(&invalid_scopes, &manifest.scopes).is_err());
    }
}
