<div align="center">

<br>

<pre>
 ███████╗██████╗ ███████╗ ██████╗████████╗███████╗██████╗
 ██╔════╝██╔══██╗██╔════╝██╔════╝╚══██╔══╝██╔════╝██╔══██╗
 ███████╗██████╔╝█████╗  ██║        ██║   █████╗  ██████╔╝
 ╚════██║██╔═══╝ ██╔══╝  ██║        ██║   ██╔══╝  ██╔══██╗
 ███████║██║     ███████╗╚██████╗   ██║   ███████╗██║  ██║
 ╚══════╝╚═╝     ╚══════╝ ╚═════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
</pre>

**S**ecurity **P**rotocol for **E**xploitation, **C**omprehensive **T**esting, **E**valuation & **R**eporting

<em>Modular security skill system for autonomous IDE agents.</em>

<br>

[![npm](https://img.shields.io/npm/v/specter-kit?color=00e5ff&style=flat-square&label=specter-kit)](https://www.npmjs.com/package/specter-kit)
[![license](https://img.shields.io/badge/license-MIT-00e5ff?style=flat-square)](LICENSE)
![zero-deps](https://img.shields.io/badge/dependencies-0-00e5ff?style=flat-square)

</div>

---

SPECTER is a zero-dependency skill framework that transforms any LLM-powered coding agent into a governed security operator. One command installs 18 security skills, 22 enforceable guardrails, and a structured assessment workflow into any project — with support for 8 agent platforms (5 auto-detected, 1 custom).

<br>

## Installation

```bash
npx specter-kit init
```

Or install globally:

```bash
npm install -g specter-kit
specter init
```

<details>
<summary>Other methods</summary>

```bash
# pnpm
pnpm add -g specter-kit && specter init

# Manual clone
git clone https://github.com/AnvinX1/SPECTER-The-Illusive-Security-Protocol.git
bash SPECTER-The-Illusive-Security-Protocol/setup.sh init
```

</details>

<br>

## Supported Platforms

| Platform | Auto-Detected |
|----------|:------------:|
| GitHub Copilot | ✓ |
| Cursor | ✓ |
| Windsurf | ✓ |
| Claude Code | — |
| Zed Editor | ✓ |
| Continue.dev | ✓ |
| Cline (VS Code) | ✓ |
| Generic (AGENTS.md) | ✓ |
| **Custom** (any agent) | — |

```bash
specter init --agent all              # target all platforms
specter init --agent zed              # Zed Editor
specter init --agent cline            # Cline (VS Code)
specter init --agent custom --src ./my-adapter.md --dest ./.myagent/specter.md
specter list --agents                 # show all supported platforms
```

<br>

## Skills

| Domain | Skills | Covers |
|--------|:------:|--------|
| **Governance & Triage** | 2 | Authorization enforcement, scope control, 22 guardrails, finding intake & dedup |
| **Reconnaissance & Threat Modeling** | 2 | Attack surface mapping, STRIDE/PASTA, AI threat actor profiling, risk prioritization |
| **Code & Application** | 3 | Source review, API security (OWASP Top 10), server misconfiguration |
| **Infrastructure & Cloud** | 3 | Cloud IAM/CIS, container escape & K8s, network segmentation |
| **Supply Chain & Identity** | 3 | Dependency CVEs, secret detection, AI hallucinated packages, CI/CD pipelines, AD/Kerberos |
| **Exploit, Mobile & AI** | 3 | PoC validation, OWASP Mobile Top 10, LLM/AI red teaming, OWASP LLM Top 10 2025 |
| **Reporting & Audit** | 2 | Evidence compilation, redaction, statistics, continuous post-task delta audit |

<br>

## Workflow

```
governance ──► recon ──► threat model
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
         code & app    infra & cloud      AI / LLM
                             supply chain
              │               │               │
              └───────────────┼───────────────┘
                              ▼
                    triage ──► exploit validation
                              │
                              ▼
                          reporting
```

Every engagement starts with `security-governance` — scope authorization and 22 cascading guardrails are enforced before any assessment work begins.

<br>

## Included

| Type | Count | Description |
|------|:-----:|-------------|
| Security Skills | 18 | Structured SKILL.md workflows with standard finding formats |
| Reference Docs | 14 | Checklists, attack patterns, MITRE ATT&CK mapping, attack chains, severity matrix, CIS benchmarks |
| Helper Scripts | 15 | Finding normalization, dedup, export, redaction, validation, scanning, shared utilities |
| Guardrails | 22 | Scope enforcement, evidence standards, regulatory escalation |

<br>

## Commands

```bash
specter init       # initialize in current project
specter scan web https://target.com   # TLS + HTTP headers scan
specter scan host target.com          # TLS + port probe
specter scan dir ./src                # secret scan
specter scan all https://target.com . # all checks + optional --output report.md
specter list       # view installed skills
specter doctor     # verify installation health
specter update     # update to latest skills
specter banner     # replay the terminal animation
```

<br>

## Guardrails

All assessments operate under 22 mandatory rules enforced by the governance skill:

**Scope & Authorization** — Written authorization required. Strict scope boundaries. Out-of-scope discovery protocol.

**Engagement Rules** — Full exploit capability within scope. Credential testing against authorized targets only. Lateral movement requires explicit approval. Destructive action limits enforced.

**Evidence & Classification** — Suspected ≠ Confirmed. Evidence required for all findings. Conservative severity classification. Standard finding format (S1–S5 severity, C1–C4 confidence).

**Compliance & Escalation** — PII access limits. Zero-day disclosure protocol. Regulatory escalation triggers for GDPR, PCI-DSS, HIPAA, SOX. Evidence retention policy enforced.

<br>

---

<div align="center">

<br>

<strong>SPECTER</strong> · by Anvin · Illusive Operations

MIT License

<br>

</div>
