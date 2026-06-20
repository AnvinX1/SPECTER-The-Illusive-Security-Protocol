use clap::ValueEnum;
use serde::{Deserialize, Serialize};
use std::fmt;

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq, ValueEnum)]
pub enum RiskLevel {
    Passive,
    ActiveSafe,
    Intrusive,
    ExploitValidation,
    Forbidden,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub enum PolicyDecision {
    Allow { risk: RiskLevel },
    RequireApproval { risk: RiskLevel, reason: String },
    Deny { risk: RiskLevel, reason: String },
}

impl PolicyDecision {
    pub fn for_risk(risk: RiskLevel) -> Self {
        match risk {
            RiskLevel::Passive => Self::Allow { risk },
            RiskLevel::ActiveSafe => Self::RequireApproval {
                risk,
                reason: "active target interaction requires in-scope authorization".to_string(),
            },
            RiskLevel::Intrusive => Self::RequireApproval {
                risk,
                reason: "intrusive testing requires explicit rules of engagement".to_string(),
            },
            RiskLevel::ExploitValidation => Self::RequireApproval {
                risk,
                reason: "exploit validation requires explicit written authorization".to_string(),
            },
            RiskLevel::Forbidden => Self::Deny {
                risk,
                reason: "forbidden actions cannot be executed by Cerberus".to_string(),
            },
        }
    }
}

impl fmt::Display for PolicyDecision {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Allow { risk } => write!(f, "allow: {risk:?}"),
            Self::RequireApproval { risk, reason } => {
                write!(f, "require-approval: {risk:?}: {reason}")
            }
            Self::Deny { risk, reason } => write!(f, "deny: {risk:?}: {reason}"),
        }
    }
}
