use anyhow::{anyhow, Result};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::{env, fmt};

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
pub enum LlmProvider {
    Anthropic,
    OpenAi,
    OpenAiCompatible,
    Offline,
}

impl LlmProvider {
    pub fn parse(value: &str) -> Result<Self> {
        match value.to_ascii_lowercase().as_str() {
            "anthropic" | "claude" => Ok(Self::Anthropic),
            "openai" => Ok(Self::OpenAi),
            "openai-compatible" | "compatible" | "local" | "lmstudio" | "ollama" => {
                Ok(Self::OpenAiCompatible)
            }
            "offline" | "none" => Ok(Self::Offline),
            other => Err(anyhow!("unknown LLM provider: {other}")),
        }
    }
}

impl fmt::Display for LlmProvider {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Anthropic => write!(f, "anthropic"),
            Self::OpenAi => write!(f, "openai"),
            Self::OpenAiCompatible => write!(f, "openai-compatible"),
            Self::Offline => write!(f, "offline"),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct LlmConfig {
    pub provider: LlmProvider,
    pub model: String,
    pub base_url: String,
    pub api_key_env: Option<String>,
}

impl LlmConfig {
    pub fn from_env(provider_override: Option<&str>, model_override: Option<&str>) -> Result<Self> {
        let provider = match provider_override {
            Some(value) => LlmProvider::parse(value)?,
            None => LlmProvider::parse(
                &env::var("CERBERUS_LLM_PROVIDER").unwrap_or_else(|_| "offline".to_string()),
            )?,
        };

        let config = match provider {
            LlmProvider::Anthropic => Self {
                provider,
                model: model_override
                    .map(ToOwned::to_owned)
                    .or_else(|| env::var("ANTHROPIC_MODEL").ok())
                    .unwrap_or_else(|| "claude-sonnet-4-5".to_string()),
                base_url: env::var("ANTHROPIC_BASE_URL")
                    .unwrap_or_else(|_| "https://api.anthropic.com".to_string()),
                api_key_env: Some("ANTHROPIC_API_KEY".to_string()),
            },
            LlmProvider::OpenAi => Self {
                provider,
                model: model_override
                    .map(ToOwned::to_owned)
                    .or_else(|| env::var("OPENAI_MODEL").ok())
                    .unwrap_or_else(|| "gpt-5".to_string()),
                base_url: env::var("OPENAI_BASE_URL")
                    .unwrap_or_else(|_| "https://api.openai.com".to_string()),
                api_key_env: Some("OPENAI_API_KEY".to_string()),
            },
            LlmProvider::OpenAiCompatible => Self {
                provider,
                model: model_override
                    .map(ToOwned::to_owned)
                    .or_else(|| env::var("CERBERUS_LLM_MODEL").ok())
                    .unwrap_or_else(|| "local-model".to_string()),
                base_url: env::var("CERBERUS_LLM_BASE_URL")
                    .unwrap_or_else(|_| "http://127.0.0.1:1234".to_string()),
                api_key_env: env::var("CERBERUS_LLM_API_KEY_ENV")
                    .ok()
                    .or_else(|| Some("CERBERUS_LLM_API_KEY".to_string())),
            },
            LlmProvider::Offline => Self {
                provider,
                model: model_override
                    .map(ToOwned::to_owned)
                    .unwrap_or_else(|| "offline".to_string()),
                base_url: "local".to_string(),
                api_key_env: None,
            },
        };

        Ok(config)
    }

    pub fn api_key_present(&self) -> bool {
        self.api_key_env
            .as_ref()
            .and_then(|name| env::var(name).ok())
            .is_some_and(|value| !value.trim().is_empty())
    }

    pub fn status_lines(&self) -> Vec<String> {
        vec![
            format!("provider: {}", self.provider),
            format!("model: {}", self.model),
            format!("base_url: {}", self.base_url),
            format!(
                "api_key: {}",
                match &self.api_key_env {
                    Some(name) if self.api_key_present() => format!("{name} present"),
                    Some(name) => format!("{name} missing"),
                    None => "not required".to_string(),
                }
            ),
        ]
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct LlmResponse {
    pub text: String,
}

pub struct LlmClient {
    config: LlmConfig,
    http: reqwest::Client,
}

impl LlmClient {
    pub fn new(config: LlmConfig) -> Self {
        Self {
            config,
            http: reqwest::Client::new(),
        }
    }

    pub async fn generate(&self, prompt: &str) -> Result<LlmResponse> {
        match self.config.provider {
            LlmProvider::Anthropic => self.generate_anthropic(prompt).await,
            LlmProvider::OpenAi | LlmProvider::OpenAiCompatible => {
                self.generate_openai_responses(prompt).await
            }
            LlmProvider::Offline => Ok(LlmResponse {
                text: "Cerberus is offline. Set CERBERUS_LLM_PROVIDER plus provider credentials."
                    .to_string(),
            }),
        }
    }

    async fn generate_anthropic(&self, prompt: &str) -> Result<LlmResponse> {
        let key = self.required_key()?;
        let url = format!("{}/v1/messages", self.config.base_url.trim_end_matches('/'));
        let response: Value = self
            .http
            .post(url)
            .header("x-api-key", key)
            .header("anthropic-version", "2023-06-01")
            .json(&json!({
                "model": self.config.model,
                "max_tokens": 1024,
                "system": cerberus_system_prompt(),
                "messages": [
                    { "role": "user", "content": prompt }
                ]
            }))
            .send()
            .await?
            .error_for_status()?
            .json()
            .await?;

        let text = response
            .get("content")
            .and_then(Value::as_array)
            .and_then(|items| {
                items.iter().find_map(|item| {
                    (item.get("type")?.as_str()? == "text")
                        .then(|| item.get("text")?.as_str().map(ToOwned::to_owned))
                        .flatten()
                })
            })
            .unwrap_or_else(|| response.to_string());

        Ok(LlmResponse { text })
    }

    async fn generate_openai_responses(&self, prompt: &str) -> Result<LlmResponse> {
        let key = self.optional_key();
        let url = format!(
            "{}/v1/responses",
            self.config.base_url.trim_end_matches('/')
        );
        let mut request = self.http.post(url).json(&json!({
            "model": self.config.model,
            "instructions": cerberus_system_prompt(),
            "input": prompt
        }));

        if let Some(key) = key {
            request = request.bearer_auth(key);
        }

        let response: Value = request.send().await?.error_for_status()?.json().await?;

        let text = response
            .get("output_text")
            .and_then(Value::as_str)
            .map(ToOwned::to_owned)
            .or_else(|| {
                response
                    .get("output")
                    .and_then(Value::as_array)
                    .and_then(|items| extract_openai_output_text(items))
            })
            .unwrap_or_else(|| response.to_string());

        Ok(LlmResponse { text })
    }

    fn required_key(&self) -> Result<String> {
        self.optional_key()
            .ok_or_else(|| anyhow!("missing API key env var: {:?}", self.config.api_key_env))
    }

    fn optional_key(&self) -> Option<String> {
        self.config
            .api_key_env
            .as_ref()
            .and_then(|name| env::var(name).ok())
            .filter(|value| !value.trim().is_empty())
    }
}

fn extract_openai_output_text(items: &[Value]) -> Option<String> {
    let mut chunks = Vec::new();
    for item in items {
        if let Some(content) = item.get("content").and_then(Value::as_array) {
            for block in content {
                if let Some(text) = block.get("text").and_then(Value::as_str) {
                    chunks.push(text.to_string());
                }
            }
        }
    }
    (!chunks.is_empty()).then(|| chunks.join("\n"))
}

pub fn cerberus_system_prompt() -> &'static str {
    "You are Cerberus, Araskova Labs' governed security agent. You help analyze authorized projects, find vulnerabilities, propose fixes, and verify remediation. You must respect scope, avoid destructive action, preserve evidence, classify uncertainty, and route active or exploit validation actions through policy approval."
}
