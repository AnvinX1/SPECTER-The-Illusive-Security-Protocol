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

<h3>The Illusive Security Protocol</h3>

<p><em>Turn any AI coding agent into a structured security operator.</em></p>

<br>

[![npm](https://img.shields.io/npm/v/specter-kit?color=00e5ff&style=flat-square&label=specter-kit)](https://npmjs.com/package/specter-kit)
[![license](https://img.shields.io/badge/license-MIT-00e5ff?style=flat-square)](LICENSE)
![skills](https://img.shields.io/badge/skills-16-00e5ff?style=flat-square)
![refs](https://img.shields.io/badge/references-11-00e5ff?style=flat-square)
![scripts](https://img.shields.io/badge/scripts-8-00e5ff?style=flat-square)
![deps](https://img.shields.io/badge/dependencies-0-00e5ff?style=flat-square)

<br>

<strong>by Anvin · Illusive Operations</strong>

<br>

</div>

---

SPECTER is a zero-dependency, drop-in security skill system that turns any LLM-powered IDE agent into a governed security operator. Install it into any project and your agent gains **16 specialized security skills**, **22 enforceable guardrails**, structured finding formats, and a complete offensive security workflow — automatically.

**Works with:** GitHub Copilot · Cursor · Windsurf · Claude Code · Any markdown-aware agent

---

## ⚡ Quick Start

```bash
npm install -g specter-kit     # install globally
cd your-project                # enter any project
specter init                   # activate SPECTER
```

Done. Your agent now operates under SPECTER governance.

---

## 🖥️ What You'll See

### After Install

An animated terminal banner greets you with a scan + glitch reveal effect:

```
  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 100%

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ███████╗██████╗ ███████╗ ██████╗████████╗███████╗██████╗
   ██╔════╝██╔══██╗██╔════╝██╔════╝╚══██╔══╝██╔════╝██╔══██╗
   ███████╗██████╔╝█████╗  ██║        ██║   █████╗  ██████╔╝
   ╚════██║██╔═══╝ ██╔══╝  ██║        ██║   ██╔══╝  ██╔══██╗
   ███████║██║     ███████╗╚██████╗   ██║   ███████╗██║  ██║
   ╚══════╝╚═╝     ╚══════╝ ╚═════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    The Illusive Security Protocol  v1.0.0
    by Anvin · Illusive Operations

    ◆ 16 security skills   ◆ 11 reference docs   ◆ 8 helper scripts

    Run specter init to activate in your project.
```

> The banner animates with a scanning progress bar and glitch-decode effect on interactive terminals. Silent in CI.

### After `specter init`

```
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ███████╗██████╗ ███████╗ ██████╗████████╗███████╗██████╗
   ██╔════╝██╔══██╗██╔════╝██╔════╝╚══██╔══╝██╔════╝██╔══██╗
   ███████╗██████╔╝█████╗  ██║        ██║   █████╗  ██████╔╝
   ╚════██║██╔═══╝ ██╔══╝  ██║        ██║   ██╔══╝  ██╔══██╗
   ███████║██║     ███████╗╚██████╗   ██║   ███████╗██║  ██║
   ╚══════╝╚═╝     ╚══════╝ ╚═════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Initializing SPECTER...

  ✓ Installed 16 security skills
  ✓ Installed 11 reference documents
  ✓ Installed 8 helper scripts
  ✓ Created master instructions

  ✓ Created .github/copilot-instructions.md (GitHub Copilot)
  ✓ Created AGENTS.md (Generic Agents)
  ✓ Created .specterrc

  SPECTER is operational.
  Security governance is now enforced for all agents.
```

> `specter init` also plays the glitch animation before initializing. Use `specter banner` to replay it anytime.

---

## 🏗️ What Gets Installed

```
your-project/
├── .specter/                              ← SPECTER core
│   ├── specter.md                         ← Master skill index
│   ├── specter.instructions.md            ← Auto-loaded by agents
│   ├── skills/                            ← 16 security skills
│   │   ├── security-governance/SKILL.md
│   │   ├── secure-code-review/SKILL.md
│   │   ├── api-security-review/SKILL.md
│   │   └── ... (13 more)
│   ├── references/                        ← 11 reference docs
│   └── scripts/                           ← 8 helper scripts
├── .github/copilot-instructions.md        ← Agent adapter (auto-detected)
├── AGENTS.md                              ← Generic agent adapter
├── .specterrc                             ← Local config
└── ... (your project files)
```

**How it works:** The agent reads the adapter config → loads SPECTER instructions → follows skill workflows automatically. No setup needed beyond `specter init`.

---

## 🤖 Supported Agents

| Agent | Adapter Location | Auto-Detected |
|-------|-----------------|:-------------:|
| **GitHub Copilot** | `.github/copilot-instructions.md` | ✓ |
| **Cursor** | `.cursor/rules/specter.md` | ✓ |
| **Windsurf** | `.windsurfrules` | ✓ |
| **Claude Code** | `CLAUDE.md` | — |
| **Any Agent** | `AGENTS.md` | ✓ |

```bash
specter init                          # auto-detect agent platform
specter init --agent copilot          # specific platform
specter init --agent all              # all platforms
specter init --agent copilot,cursor   # multiple platforms
specter init --force                  # overwrite existing configs
```

---

## 🛡️ Skills (16)

| Category | Skill | Purpose |
|----------|-------|---------|
| **Governance** | `security-governance` | Authorization, scope, 22 cascading guardrails |
| | `bug-bounty-triage` | Intake, dedup, severity, routing matrix |
| **Recon & Design** | `indepth-recon-analysis` | Attack surface mapping, tech fingerprinting |
| | `threat-modeling` | STRIDE, PASTA, attack trees, risk prioritization |
| **Code & Application** | `secure-code-review` | Source code vulnerability hunting |
| | `api-security-review` | OWASP API Top 10, GraphQL, WebSocket |
| | `web-misconfig-review` | Headers, TLS, CORS, server config audit |
| **Infrastructure** | `cloud-config-audit` | IAM, storage, network, CIS benchmarks |
| | `container-and-runtime-security` | Container escape, K8s runtime, service mesh |
| | `network-infrastructure-pentest` | Segmentation, firewall, protocol testing |
| **Supply Chain** | `dependency-and-secret-audit` | CVE lookup, secret detection, license risk |
| | `ci-cd-supply-chain-security` | Pipeline config, SLSA, artifact integrity |
| | `active-directory-and-identity-audit` | Kerberos, AD CS, BloodHound, Azure AD |
| **Specialized** | `exploit-validation` | PoC development, exploitation, confirmation |
| | `mobile-security-assessment` | OWASP Mobile Top 10, Frida, Objection |
| **Reporting** | `evidence-and-reporting` | Report compilation, redaction, statistics |

---

## 📋 Workflow

```
 security-governance  ← ALWAYS FIRST: scope + authorization (22 guardrails)
         │
 indepth-recon-analysis → threat-modeling
         │
 ┌───────┴─────────────────────────────────────────────┐
 │                 Parallel Assessment                  │
 │                                                      │
 │  secure-code-review      cloud-config-audit          │
 │  api-security-review     container-runtime-security  │
 │  web-misconfig-review    network-infra-pentest       │
 │  dependency-secret-audit ci-cd-supply-chain          │
 │  mobile-assessment       ad-identity-audit           │
 └───────┬─────────────────────────────────────────────┘
         │
 bug-bounty-triage → exploit-validation
         │
 evidence-and-reporting  ← Final report
```

---

## 🔧 Commands

| Command | Purpose |
|---------|---------|
| `specter init` | Initialize SPECTER in current project |
| `specter list` | View all skills with categories |
| `specter doctor` | Health check — verify installation |
| `specter update` | Update skills to latest version |
| `specter banner` | Replay the animated terminal banner |
| `specter help` | Show all commands and options |

---

## 📚 References (11)

| Reference | Scope |
|-----------|-------|
| `severity-matrix.md` | S1–S5 severity, C1–C4 confidence, triage SLAs |
| `authz-and-authn-checklist.md` | AuthN/AuthZ, sessions, MFA, OAuth |
| `secrets-and-config-checklist.md` | Secret detection, config hygiene |
| `web-common-risks.md` | OWASP Top 10, XSS, CSRF, business logic |
| `report-template.md` | Finding format, report sections |
| `owasp-api-top-10-checklist.md` | API1–API10 test procedures |
| `graphql-security-checklist.md` | Introspection, DoS, batching |
| `jwt-and-oauth-attacks.md` | JWT + OAuth attack patterns |
| `ssrf-exploitation-guide.md` | Payloads, cloud metadata, bypasses |
| `cloud-cis-benchmarks-summary.md` | AWS/Azure/GCP CIS top checks |
| `tool-recommendations.md` | Categorized tool reference |

---

## 🔩 Scripts (8)

| Script | Purpose |
|--------|---------|
| `normalize_finding.py` | Raw data → standard finding format |
| `severity_stats.py` | Report → severity statistics |
| `secret_grep.py` | Scan for hardcoded secrets |
| `deduplicate_findings.py` | Merge duplicate findings |
| `export_findings.py` | Findings → JSON/CSV export |
| `merge_reports.py` | Combine multiple reports |
| `validate_finding.py` | Format compliance check |
| `redact_evidence.py` | Redact PII/secrets from reports |

---

## 🔒 Guardrails (22 Rules)

Enforced automatically via `security-governance` — the first skill invoked in every engagement:

**Core (1–12):** Authorization required · Scope enforcement · Full exploit capability (in scope) · Persistence/lateral (authorized only) · Credential testing (authorized targets) · Social engineering (explicit scope) · Stealth operations (in scope) · Suspected ≠ Confirmed · Evidence required · Conservative classification · Data protection · Destructive action limits

**Extended (13–22):** Out-of-scope discovery protocol · Third-party service limits · Zero-day disclosure · PII access limits · Active defense/honeypot handling · Incident response trigger · Regulatory escalation (GDPR/PCI/HIPAA/SOX) · Risk acceptance process · Scope expansion matrix · Evidence retention policy

---

## 📦 All Installation Methods

<details>
<summary><strong>npm (recommended)</strong></summary>

```bash
npm install -g specter-kit
cd your-project
specter init
```
</details>

<details>
<summary><strong>npx (no global install)</strong></summary>

```bash
cd your-project
npx specter-kit init
```
</details>

<details>
<summary><strong>pnpm</strong></summary>

```bash
pnpm add -g specter-kit
cd your-project
specter init
```
</details>

<details>
<summary><strong>Standalone (no Node.js required)</strong></summary>

```bash
git clone https://github.com/anvin/specter-kit.git
cd your-project
bash ../specter-kit/setup.sh init
```
</details>

---

## Finding Format

Every finding follows a standardized template:

```markdown
### [FINDING-ID]: Title

| Field | Value |
|-------|-------|
| Severity   | S1–S5 |
| Confidence | C1–C4 |
| Status     | Suspected / Confirmed |
| Category   | CWE-XXX |
| Target     | [affected component] |

#### Issue Summary
#### Impact
#### Evidence
#### Remediation
#### Validation Notes
```

---

<div align="center">

<br>

```
 ███████╗██████╗ ███████╗ ██████╗████████╗███████╗██████╗
 ██╔════╝██╔══██╗██╔════╝██╔════╝╚══██╔══╝██╔════╝██╔══██╗
 ███████╗██████╔╝█████╗  ██║        ██║   █████╗  ██████╔╝
 ╚════██║██╔═══╝ ██╔══╝  ██║        ██║   ██╔══╝  ██╔══██╗
 ███████║██║     ███████╗╚██████╗   ██║   ███████╗██║  ██║
 ╚══════╝╚═╝     ╚══════╝ ╚═════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
```

**S**ecurity **P**rotocol for **E**xploitation, **C**omprehensive **T**esting, **E**valuation & **R**eporting

*by Anvin · Illusive Operations*

MIT License

</div>
