use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct SkillManifest {
    pub id: String,
    pub category: String,
    pub requires_governance: bool,
    pub inputs: Vec<String>,
    pub outputs: Vec<String>,
}
