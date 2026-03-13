# SPECTER — The Illusive Security Protocol

> **S**ecurity **P**rotocol for **E**xploitation, **C**omprehensive **T**esting, **E**valuation & **R**eporting
> by Anvin · Illusive Operations

Full skill reference and workflow guide. This document is the source of truth for all SPECTER operations.

---

## Path Convention

All paths in this document and in SKILL.md files are **relative to the `.specter/` directory**. When a skill references `references/severity-matrix.md`, look for `.specter/references/severity-matrix.md`.

---

## Governance — MANDATORY

**Before ANY security task**, invoke `skills/security-governance/SKILL.md` and confirm:

1. Authorization exists (bug bounty URL, pentest SOW, or explicit user confirmation)
2. Scope is defined (what's in, what's out)
3. Rules of engagement are set (rate limits, forbidden actions, data handling)

**Never skip governance.** No assessment, scan, or exploit proceeds without it.

---

## Skill Index

### Governance & Triage
| Skill | Path | When |
|-------|------|------|
| security-governance | `skills/security-governance/SKILL.md` | Always first — authorization + scope |
| bug-bounty-triage | `skills/bug-bounty-triage/SKILL.md` | New finding needs intake, dedup, routing |

### Reconnaissance & Design
| Skill | Path | When |
|-------|------|------|
| indepth-recon-analysis | `skills/indepth-recon-analysis/SKILL.md` | Map attack surface, fingerprint tech |
| threat-modeling | `skills/threat-modeling/SKILL.md` | System design review, STRIDE/PASTA |

### Code & Application
| Skill | Path | When |
|-------|------|------|
| secure-code-review | `skills/secure-code-review/SKILL.md` | Source code in scope |
| api-security-review | `skills/api-security-review/SKILL.md` | REST/GraphQL/WebSocket APIs |
| web-misconfig-review | `skills/web-misconfig-review/SKILL.md` | Server/app config audit |

### Infrastructure & Cloud
| Skill | Path | When |
|-------|------|------|
| cloud-config-audit | `skills/cloud-config-audit/SKILL.md` | AWS/Azure/GCP/IaC config |
| container-and-runtime-security | `skills/container-and-runtime-security/SKILL.md` | Docker/K8s environment |
| network-infrastructure-pentest | `skills/network-infrastructure-pentest/SKILL.md` | Network segmentation, firewalls |

### Supply Chain & Identity
| Skill | Path | When |
|-------|------|------|
| dependency-and-secret-audit | `skills/dependency-and-secret-audit/SKILL.md` | Dependencies, secrets, configs |
| ci-cd-supply-chain-security | `skills/ci-cd-supply-chain-security/SKILL.md` | Pipeline config, artifact integrity |
| active-directory-and-identity-audit | `skills/active-directory-and-identity-audit/SKILL.md` | AD, Kerberos, Azure AD |

### Specialized
| Skill | Path | When |
|-------|------|------|
| exploit-validation | `skills/exploit-validation/SKILL.md` | Suspected finding needs PoC |
| mobile-security-assessment | `skills/mobile-security-assessment/SKILL.md` | iOS/Android app in scope |
| llm-and-ai-security | `skills/llm-and-ai-security/SKILL.md` | LLM chatbot, AI agent, GenAI feature, AI red teaming |

### Reporting
| Skill | Path | When |
|-------|------|------|
| evidence-and-reporting | `skills/evidence-and-reporting/SKILL.md` | Assessment complete, generate report |

### Delta Audit (Continuous)
| Skill | Path | When |
|-------|------|------|
| specter-delta | `skills/specter-delta/SKILL.md` | After every coding task that touches security-relevant files |

---

## Workflow

```
Governance → Recon → [Threat Model] → Parallel Assessment → Triage → Validation → Report
```

1. **security-governance** — Set scope and authorization
2. **indepth-recon-analysis** — Map the target (includes AI/LLM feature fingerprinting)
3. **threat-modeling** — (optional) Analyze design-level risks, including AI/ML threat actors
4. **Assessment skills** — Run appropriate skills in parallel based on target type:
   - Traditional web/API/code targets → existing skill set
   - AI/LLM features detected → also invoke `llm-and-ai-security`
   - AI red teaming engagement → `llm-and-ai-security` as primary skill
5. **bug-bounty-triage** — Process all findings through triage (routing matrix decides next skill)
6. **exploit-validation** — Validate suspected findings with PoC (includes AI/LLM PoC development)
7. **evidence-and-reporting** — Compile final report
8. **Post-Remediation Re-Validation** *(after client applies fixes)*:
   - Re-test each finding marked as `Remediated`
   - Update finding status: `Confirmed` → `Remediated (Verified)` or `Re-Opened`
   - Generate a delta report via `evidence-and-reporting` (delta report type)
   - Close findings that pass re-validation; escalate any regressions immediately

---

## Finding Format

Every finding MUST use this structure:

```markdown
### [FINDING-ID]: [Title]

| Field | Value |
|-------|-------|
| **Severity** | S1-S5 (per references/severity-matrix.md) |
| **Confidence** | C1 Confirmed / C2 Firm / C3 Probable / C4 Speculative |
| **Status** | Suspected / Confirmed / Remediated / False Positive / Accepted Risk |
| **Category** | CWE-XXX / OWASP category |
| **Affected Target** | endpoint, file, component |

#### Issue Summary
#### Impact
#### Evidence
#### Remediation
#### Validation Notes
```

---

## Guardrails (22 Rules)

All skills enforce these — see `skills/security-governance/SKILL.md` for full details:

**Core:** Authorization required · Scope enforcement · Suspected ≠ Confirmed · Evidence required · Conservative classification · Data protection · Destructive action limits

**Extended:** Out-of-scope discovery protocol · Third-party testing limits · Zero-day disclosure · PII access limits · Active defense interaction · Incident response triggers · Regulatory escalation (GDPR/PCI/HIPAA) · Risk acceptance process · Scope expansion matrix · Evidence retention policy

---

## References

| Document | Purpose |
|----------|---------|
| `references/severity-matrix.md` | S1-S5 severity, C1-C4 confidence, triage SLAs |
| `references/authz-and-authn-checklist.md` | AuthN/AuthZ review checklist |
| `references/secrets-and-config-checklist.md` | Secret detection, config hygiene |
| `references/web-common-risks.md` | OWASP Top 10 + common vulns |
| `references/report-template.md` | Finding and report format |
| `references/owasp-api-top-10-checklist.md` | API1-API10 test procedures |
| `references/graphql-security-checklist.md` | GraphQL attack surface |
| `references/jwt-and-oauth-attacks.md` | JWT + OAuth attack patterns |
| `references/ssrf-exploitation-guide.md` | SSRF payloads and bypasses |
| `references/cloud-cis-benchmarks-summary.md` | AWS/Azure/GCP CIS checks |
| `references/tool-recommendations.md` | Categorized tool reference |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/normalize_finding.py` | Raw data → standard finding |
| `scripts/severity_stats.py` | Report → statistics |
| `scripts/secret_grep.py` | Scan directory for secrets |
| `scripts/deduplicate_findings.py` | Merge duplicate findings |
| `scripts/export_findings.py` | Findings → JSON/CSV |
| `scripts/merge_reports.py` | Combine multiple reports |
| `scripts/validate_finding.py` | Format compliance check |
| `scripts/redact_evidence.py` | PII/secret redaction |
| `scripts/http_headers_check.py` | **Active** — probe HTTP security headers on a live URL |
| `scripts/tls_check.py` | **Active** — check TLS version, cipher, certificate expiry |
| `scripts/port_probe.py` | **Active** — fast TCP port prober with service banners |
| `scripts/cmd_runner.py` | **Active** — run allowlisted security tools (nmap, nikto…) safely |
| `scripts/post_task_audit.py` | **Hook** — run after every task (Stop hook); writes `.audit-pending` |
| `scripts/findings_index.py` | **Findings** — manage `.specter/findings/index.json` (add/update/list/stats) |

### Running Active Checks

Active scripts can be invoked directly or via the `specter run` CLI command:

```bash
specter run http-headers https://example.com
specter run tls example.com --port 8443
specter run ports 10.0.0.1 --ports top1000
specter run secrets ./src
specter run tool nmap -sV -p 80,443 example.com
specter run tool --list           # show all allowlisted tools
```

Or directly:

```bash
python3 .specter/scripts/http_headers_check.py https://example.com
python3 .specter/scripts/tls_check.py example.com --port 443
python3 .specter/scripts/port_probe.py 10.0.0.1 --ports 22,80,443,3306
python3 .specter/scripts/cmd_runner.py nmap -sV -T4 example.com
```

---

## Session Protocol

### On Every New Conversation (Security or Not)

Before doing anything else, run these two checks silently:

1. **Open findings check**
   ```
   cat .specter/findings/index.json
   ```
   If there are open S1 or S2 findings from a previous session:
   → Surface them to the user immediately with a one-line summary.
   → Example: "2 open S2 findings from last session (ipc-handlers.ts). Fix before new work?"

2. **Pending audit check**
   ```
   cat .specter/.audit-pending
   ```
   If the file exists:
   → Run `specter-delta` on the listed files before starting new work.
   → Brief the user: "Running post-task security check on N changed files…"

### On Every Task Completion

After any task that modifies security-relevant files:
→ Run `specter-delta` (see `specter.instructions.md` for full gate procedure)
→ Log findings to `.specter/findings/`
→ Only say "Done" when the severity gate passes

### Configuring the Stop Hook (Claude Code)

To automate the audit trigger without relying on AI self-enforcement, add to the project's `.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .specter/scripts/post_task_audit.py"
          }
        ]
      }
    ]
  }
}
```

The `post_task_audit.py` script will then write `.specter/.audit-pending` automatically after every agent response.
