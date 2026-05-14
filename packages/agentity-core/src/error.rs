use thiserror::Error;

#[derive(Error, Debug)]
pub enum AgentityError {
    #[error("Invalid signature")]
    InvalidSignature,
    #[error("AID expired")]
    Expired,
    #[error("AID revoked")]
    Revoked,
    #[error("Invalid scope: {0}")]
    InvalidScope(String),
    #[error("Scope exceeds parent permissions")]
    ScopeEscalation,
    #[error("Serialization error: {0}")]
    Serialization(#[from] serde_json::Error),
    #[error("Delegation depth exceeded (max 10)")]
    DelegationDepthExceeded,
    #[error("Invalid nonce: {0}")]
    InvalidNonce(String),
    #[error("Cryptographic error: {0}")]
    Crypto(String),
    #[error("Timestamp out of tolerance")]
    TimestampOutOfTolerance,
}
