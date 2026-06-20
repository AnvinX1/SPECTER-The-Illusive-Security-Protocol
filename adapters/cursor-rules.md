# SPECTER Security Protocol

This project uses SPECTER (The Illusive Security Protocol) — a modular security skills system installed at `.specter/`.

## Rules

For any security-related task (assessment, pentest, code review, vulnerability analysis, bug bounty, AI/LLM security, threat modeling):

1. Read `.specter/skills/security-governance/SKILL.md` first. Confirm authorization and scope before any work.
2. Consult `.specter/specter.md` for the full skill index. Select the matching skill and follow its workflow.
3. Output all findings using the standard format from `.specter/references/report-template.md`.
4. Apply severity ratings per `.specter/references/severity-matrix.md` (S1-S5 severity, C1-C4 confidence).
5. Route findings through `.specter/skills/bug-bounty-triage/SKILL.md` for dedup and prioritization.
6. Never test outside authorized scope. Never output unredacted PII or credentials.

## Skills (18)

Governance: security-governance, bug-bounty-triage
Recon: indepth-recon-analysis, threat-modeling
Application: secure-code-review, api-security-review, web-misconfig-review
Infrastructure: cloud-config-audit, container-and-runtime-security, network-infrastructure-pentest
Supply Chain: dependency-and-secret-audit, ci-cd-supply-chain-security, active-directory-and-identity-audit
Specialized: exploit-validation, mobile-security-assessment, llm-and-ai-security
Reporting & Audit: evidence-and-reporting, specter-delta

All at `.specter/skills/<name>/SKILL.md`. Read the SKILL.md before starting.
