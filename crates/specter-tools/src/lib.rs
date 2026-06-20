use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct ToolSpec {
    pub name: String,
    pub command: String,
    pub requires_scope: bool,
    pub timeout_seconds: u64,
}
