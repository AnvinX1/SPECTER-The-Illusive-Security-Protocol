# Rust Migration Plan

This plan keeps Specter Toolkit working while Cerberus is built in Rust.

## Phase 0: Compatibility Baseline

- Keep `bin/specter.js` as the npm CLI.
- Keep Python scripts and tests as the current behavioral reference.
- Add Rust crates without changing install behavior.
- Add parity tests as Rust functionality replaces Python scripts.

## Phase 1: CLI Foundation

Deliver a Rust CLI that can run side-by-side with the current package:

```bash
cargo run -p specter-cli -- doctor
cargo run -p specter-cli -- list
cargo run -p specter-cli -- cerberus
cargo run -p specter-cli -- console
cargo run -p specter-cli -- llm status
```

Initial responsibilities:

- identify repository health
- print product split
- expose placeholder command groups
- launch the first Cerberus terminal console
- detect and call configured LLM providers
- return stable exit codes

## Phase 2: Findings Core

Port the finding utilities first because every workflow depends on them.

Python source of truth:

- `scripts/specter_utils.py`
- `scripts/validate_finding.py`
- `scripts/normalize_finding.py`
- `scripts/deduplicate_findings.py`
- `scripts/export_findings.py`
- `scripts/severity_stats.py`
- `scripts/merge_reports.py`

Rust target crate:

- `crates/specter-findings`

## Phase 3: Native Scanners

Port passive and low-risk active checks:

- secret scan
- HTTP security headers
- TLS/certificate inspection
- TCP port probe with conservative defaults

Rust target crate:

- `crates/specter-tools`

## Phase 4: Policy Engine

Build the Cerberus control layer:

- authorization state
- scope matching
- tool risk classification
- approval decisions
- policy audit logs

Rust target crate:

- `crates/specter-policy`

## Phase 5: Agent Runtime

Build the agentic framework:

- task planning
- skill routing
- tool execution queue
- evidence collection
- findings generation
- session state
- policy-enforced LLM suggestions

Rust target crates:

- `crates/specter-core`
- `crates/specter-skills`
- `crates/specter-memory`
- `crates/specter-llm`

## Phase 6: Cerberus Services

Add commercial runtime surfaces:

- local daemon
- HTTP API
- MCP server
- CI policy gate
- terminal agent console

Rust target crates:

- `crates/cerberus-daemon`
- `crates/specter-api`
- `crates/specter-mcp`
- `crates/specter-llm`

## Release Strategy

Use three tracks:

| Track | Audience | Contents |
|-------|----------|----------|
| Specter Toolkit | Open source | Skills, docs, adapters, lightweight scanners |
| Specter Rust Preview | Developers | Rust CLI parity and native scanners |
| Cerberus | Araskova Labs | Agent runtime, daemon, policy engine, memory, commercial integrations |

Do not remove the Node/Python path until the Rust CLI has command parity for
the documented public commands.
