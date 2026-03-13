---
applyTo: "**"
---

# SPECTER Security Protocol Active

This project has **SPECTER** (The Illusive Security Protocol) installed at `.specter/`.

## When to Use SPECTER

Activate SPECTER skills when the user requests any of:
- Security assessment, audit, review, or pentest
- Vulnerability analysis or bug bounty work
- Code review for security issues
- Dependency or secret scanning
- Cloud, container, or infrastructure security review
- Threat modeling or attack surface mapping
- Exploit development or validation
- Security report generation
- LLM/AI security or safety assessment, AI red teaming, prompt injection, jailbreak testing

## Mandatory Rules

1. **Governance first** — Before ANY security work, read and apply `.specter/skills/security-governance/SKILL.md`. Confirm authorization and scope.
2. **Standard format** — All findings use the format defined in `.specter/references/report-template.md` with severity from `.specter/references/severity-matrix.md`.
3. **Read the skill** — When a task matches a skill, read the full SKILL.md before proceeding. Follow its workflow exactly.
4. **Never skip triage** — Route findings through `.specter/skills/bug-bounty-triage/SKILL.md` for dedup and prioritization.
5. **Redact PII** — Never output unredacted PII, credentials, or secrets in findings.

## Quick Reference

Full skill index, workflow, and governance details: `.specter/specter.md`

18 skills available across: governance, recon, code review, API security, web config, cloud, containers, network, supply chain, identity, mobile, threat modeling, LLM/AI security, exploit validation, reporting, and delta audit.

---

## Post-Task Security Gate (MANDATORY — Non-Negotiable)

After **every coding task** that creates or modifies files under:
`electron/`, `lib/`, `components/`, `tesserin-mcp/`, `tesserin-cli/`, `tesserin-daemon/`, or any directory explicitly listed as in-scope for this project.

You MUST do the following **before marking the task complete**:

### Step 1 — Check for pending audit
Read `.specter/.audit-pending`.
If it exists, a hook has already identified changed files — use that list.
If it does not exist, run: `git diff --name-only HEAD`

### Step 2 — Run specter-delta
Invoke `.specter/skills/specter-delta/SKILL.md` on the changed files.

### Step 3 — Severity gate
| Finding Level | Action |
|--------------|--------|
| S1 Critical | STOP. Fix immediately. Task is not done. |
| S2 High | Fix before closing task, OR get explicit user acceptance. |
| S3 Medium | Log to findings store. Surface as warning. Task may close. |
| S4 / S5 | Log to findings store. Task may close. |

### Step 4 — Persist findings
Write results to `.specter/findings/<ISO-date>-delta.md`.
Update `.specter/findings/index.json` via `scripts/findings_index.py`.
Delete `.specter/.audit-pending`.

### Step 5 — Session start check
At the **start of every new conversation**, check:
1. Does `.specter/findings/index.json` have open S1 or S2 findings?
   → If yes: surface them immediately before beginning any new work.
2. Does `.specter/.audit-pending` exist?
   → If yes: run specter-delta before any new work begins.
