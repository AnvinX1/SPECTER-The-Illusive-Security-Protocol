# Cerberus Terminal Interface

Cerberus is a terminal-only security agent surface.

The command center is:

```bash
cargo run -p specter-cli -- console
```

Provider-aware launch:

```bash
cargo run -p specter-cli -- console --provider anthropic
cargo run -p specter-cli -- console --provider openai
cargo run -p specter-cli -- console --provider openai-compatible --model local-model
```

## LLM Environment

Anthropic / Claude:

```powershell
$env:CERBERUS_LLM_PROVIDER="anthropic"
$env:ANTHROPIC_API_KEY="..."
$env:ANTHROPIC_MODEL="claude-sonnet-4-5"
```

OpenAI:

```powershell
$env:CERBERUS_LLM_PROVIDER="openai"
$env:OPENAI_API_KEY="..."
$env:OPENAI_MODEL="gpt-5"
```

Local OpenAI-compatible server:

```powershell
$env:CERBERUS_LLM_PROVIDER="openai-compatible"
$env:CERBERUS_LLM_BASE_URL="http://127.0.0.1:1234"
$env:CERBERUS_LLM_MODEL="local-model"
```

Check configuration:

```bash
cargo run -p specter-cli -- llm status
```

Send a direct prompt:

```bash
cargo run -p specter-cli -- llm ask "Create a safe first-pass audit plan."
```

## Font Policy

The Rephen font remains an Araskova brand asset, but terminal apps cannot
reliably force bundled fonts. Cerberus should render cleanly in any good
monospace terminal. If an operator's terminal emulator supports custom fonts,
they can configure Rephen manually, but the TUI must not require it.
