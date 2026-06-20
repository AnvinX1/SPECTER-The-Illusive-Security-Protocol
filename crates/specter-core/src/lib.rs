use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct ProductLine {
    pub name: &'static str,
    pub description: &'static str,
}

impl ProductLine {
    pub fn all() -> Vec<Self> {
        vec![
            Self {
                name: "Specter Toolkit",
                description:
                    "Open-source security skills, references, adapters, and lightweight tooling",
            },
            Self {
                name: "Cerberus",
                description: "Araskova Labs agentic security framework built on a Rust runtime",
            },
        ]
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct Engagement {
    pub id: String,
    pub name: String,
    pub scope: Scope,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct Scope {
    pub included_targets: Vec<String>,
    pub excluded_targets: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct AgentTask {
    pub id: String,
    pub title: String,
    pub status: TaskStatus,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub enum TaskStatus {
    Pending,
    Approved,
    Running,
    Blocked,
    Complete,
}
