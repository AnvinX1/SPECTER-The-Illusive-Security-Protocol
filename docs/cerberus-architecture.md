# Cerberus Architecture

Cerberus is the commercial Araskova Labs upgrade path for Specter Toolkit.
Specter Toolkit remains the open-source skills, references, adapters, helper
scripts, and lightweight CLI. Cerberus turns that foundation into a Rust-native
agentic security framework with policy enforcement, memory, tool execution,
findings storage, and autonomous security workflows.

## Product Split

| Layer | Name | Role |
|-------|------|------|
| Open-source toolkit | Specter Toolkit | Security skills, references, adapter rules, lightweight scanners, report helpers |
| Agentic upgrade | Cerberus | Terminal-first Rust runtime for governed autonomous security operations |
| Company | Araskova Labs | Product owner and commercial security platform steward |

Specter Toolkit should stay easy to install, audit, fork, and use from IDE
agents. Cerberus should become the controlled runtime that can reason, plan,
execute, remember, validate, and report inside authorized engagements.

## Interface Strategy

Cerberus is terminal-only for the agent interface.

The primary operator surface should feel closer to Claude Code, Codex, Gemini
CLI, and opencode than to a traditional dashboard. The terminal is where the
agent plans, requests approval, runs tools, patches code, verifies fixes, and
streams evidence. No desktop or web UI should be required for Cerberus agent
operation.

| Surface | Role |
|---------|------|
| Terminal console | Primary agent loop, missions, approvals, tool output, fixes |
| Headless CLI | CI, scripts, automation, MCP/tool integrations |
| API/MCP | Integration layer for external agents and IDEs |

## Terminal Typography

Cerberus can ship Rephen as a brand asset, but a terminal application cannot
reliably force the operator's terminal emulator to use a bundled font. The TUI
must therefore use ASCII-safe, monospaced-friendly layout by default. Operators
may configure Rephen in their terminal profile if their terminal supports it,
but Cerberus should never depend on that font for readability.

## Positioning

**Specter Toolkit**

Open-source security skill framework for autonomous IDE agents.

**Cerberus**

Araskova's agentic security framework for governed autonomous defense, red
teaming, validation, and continuous security operations.

## Rust Workspace Target

```text
crates/
  specter-cli/        Public CLI compatibility and migration commands
  specter-core/       Agent runtime, plans, tasks, sessions, orchestration
  specter-policy/     Authorization, scope, tool risk, and guardrail engine
  specter-skills/     Skill manifest loading and routing
  specter-tools/      Native scanners and controlled external tool execution
  specter-findings/   Finding model, validation, deduplication, reporting
  specter-memory/     Local state, audit trail, and session store
  specter-llm/        Provider abstraction for local and remote models
  specter-api/        Local HTTP control plane
  specter-mcp/        MCP server/client integration
  cerberus-daemon/    Long-running Cerberus service
```

The first Rust milestone should live beside the current Node/Python package.
Once command parity is reached, the Node CLI can become a compatibility shim or
be retired in a major release.

## Agent Loop

```text
Observe request
  -> classify security intent
  -> load engagement scope
  -> enforce policy
  -> select skills
  -> build plan
  -> approve tool calls
  -> execute tools
  -> collect evidence
  -> normalize findings
  -> deduplicate and validate
  -> report
  -> persist audit trail
```

The LLM proposes actions. Cerberus decides whether those actions are allowed.
Tool execution must always pass through the Rust policy and scope engine.

## Security Control Model

Cerberus actions are classified by risk:

| Risk | Meaning |
|------|---------|
| passive | Reads local files or public metadata without touching targets |
| active-safe | Makes low-impact requests to in-scope targets |
| intrusive | Performs heavier scans, fuzzing, auth testing, or enumeration |
| exploit-validation | Attempts controlled proof-of-concept validation |
| forbidden | Destructive, out-of-scope, or unauthorized behavior |

Every tool call should record:

- tool name
- arguments
- target
- policy decision
- start and end time
- exit status
- redacted stdout/stderr
- linked evidence IDs

## MVP

The first Cerberus-capable Rust milestone:

```bash
specter-rs doctor
specter-rs list
specter-rs console
specter-rs llm status
specter-rs policy check
specter-rs scan web https://example.com
specter-rs scan dir ./src
specter-rs findings list
specter-rs report generate
```

MVP internals:

- Rust CLI shell
- shared domain model
- policy decision type
- finding type and validation helpers
- skill manifest type
- placeholder scanner commands
- compatibility docs for current Specter Toolkit users

## Migration Phases

1. Scaffold Rust workspace with stable crate boundaries.
2. Port finding parsing, validation, deduplication, and export.
3. Port passive scanners: secrets, HTTP headers, TLS checks.
4. Add local findings storage and report generation.
5. Add scope and authorization policy gates.
6. Add controlled external tool runner.
7. Add skill manifests and skill router.
8. Add LLM provider abstraction.
9. Add autonomous planner and execution loop.
10. Add MCP/API/daemon modes for Cerberus.

## Naming Rules

- Use **Specter Toolkit** for the open-source package and docs.
- Use **Cerberus** for the Rust-native agentic upgrade.
- Use **Cerberus Core** for the runtime internals.
- Use **Cerberus Protocol** for the governed autonomous workflow.
- Keep the public CLI name `specter` for existing users until a major release
  intentionally changes distribution.
