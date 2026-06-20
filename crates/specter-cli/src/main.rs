use anyhow::Result;
use clap::{Args, Parser, Subcommand};
use specter_core::ProductLine;
use specter_llm::{LlmClient, LlmConfig};
use specter_policy::{PolicyDecision, RiskLevel};

mod tui;

#[derive(Debug, Parser)]
#[command(name = "specter-rs")]
#[command(about = "Rust preview for Specter Toolkit and the Cerberus upgrade path")]
struct Cli {
    #[command(subcommand)]
    command: Command,
}

#[derive(Debug, Subcommand)]
enum Command {
    /// Launch the Cerberus terminal interface.
    Console(ConsoleArgs),
    /// Show repository and runtime health.
    Doctor,
    /// List available product layers and planned modules.
    List,
    /// Explain the Cerberus upgrade path.
    Cerberus,
    /// Policy inspection commands.
    Policy {
        #[command(subcommand)]
        command: PolicyCommand,
    },
    /// LLM connection commands.
    Llm {
        #[command(subcommand)]
        command: LlmCommand,
    },
}

#[derive(Debug, Args)]
struct ConsoleArgs {
    /// Provider: offline, anthropic, openai, or openai-compatible.
    #[arg(long)]
    provider: Option<String>,
    /// Model override for the selected provider.
    #[arg(long)]
    model: Option<String>,
}

#[derive(Debug, Subcommand)]
enum PolicyCommand {
    /// Run a placeholder policy decision for an action risk level.
    Check {
        #[arg(long, default_value = "passive")]
        risk: RiskLevel,
    },
}

#[derive(Debug, Subcommand)]
enum LlmCommand {
    /// Show active LLM provider configuration from environment.
    Status {
        /// Provider: offline, anthropic, openai, or openai-compatible.
        #[arg(long)]
        provider: Option<String>,
        /// Model override for the selected provider.
        #[arg(long)]
        model: Option<String>,
    },
    /// Send a prompt to the configured provider.
    Ask {
        /// Prompt text.
        prompt: String,
        /// Provider: anthropic, openai, or openai-compatible.
        #[arg(long)]
        provider: Option<String>,
        /// Model override for the selected provider.
        #[arg(long)]
        model: Option<String>,
    },
}

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Command::Console(args) => {
            let config = LlmConfig::from_env(args.provider.as_deref(), args.model.as_deref())?;
            tui::run(config)?;
        }
        Command::Doctor => {
            println!("Specter Toolkit: present");
            println!("Cerberus Rust preview: initialized");
            println!("Status: scaffold ready");
        }
        Command::List => {
            for line in ProductLine::all() {
                println!("{} - {}", line.name, line.description);
            }
        }
        Command::Cerberus => {
            println!("Cerberus is Araskova Labs' Rust-native agentic upgrade for Specter Toolkit.");
            println!("Specter Toolkit remains the open-source skills and lightweight security tooling layer.");
            println!("Cerberus adds policy, memory, tool control, findings storage, and autonomous execution.");
        }
        Command::Policy { command } => match command {
            PolicyCommand::Check { risk } => {
                let decision = PolicyDecision::for_risk(risk);
                println!("{decision}");
            }
        },
        Command::Llm { command } => match command {
            LlmCommand::Status { provider, model } => {
                let config = LlmConfig::from_env(provider.as_deref(), model.as_deref())?;
                for line in config.status_lines() {
                    println!("{line}");
                }
            }
            LlmCommand::Ask {
                prompt,
                provider,
                model,
            } => {
                let config = LlmConfig::from_env(provider.as_deref(), model.as_deref())?;
                let client = LlmClient::new(config);
                let response = client.generate(&prompt).await?;
                println!("{}", response.text);
            }
        },
    }

    Ok(())
}
