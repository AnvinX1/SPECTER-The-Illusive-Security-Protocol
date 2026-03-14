# SPECTER — The Illusive Security Protocol

This project has SPECTER security skills installed at `.specter/`.

## For All Security Work

Before ANY security assessment, pentest, code review, or vulnerability analysis:

1. Read `.specter/skills/security-governance/SKILL.md` — confirm authorization and scope
2. Read `.specter/specter.md` — full skill index, select the right skill for the task
3. Follow the selected skill's workflow exactly
4. Output findings using `.specter/references/report-template.md` format
5. Apply severity per `.specter/references/severity-matrix.md`
6. Route findings through `.specter/skills/bug-bounty-triage/SKILL.md`

## Rules

- Never test outside authorized scope
- Separate Suspected from Confirmed findings
- Redact PII and credentials
- Evidence required for every finding
- Follow the 22 guardrails in security-governance

## 18 Skills Available

| Category | Skills |
|----------|--------|
| Governance | security-governance, bug-bounty-triage |
| Recon | indepth-recon-analysis, threat-modeling |
| Application | secure-code-review, api-security-review, web-misconfig-review |
| Infrastructure | cloud-config-audit, container-and-runtime-security, network-infrastructure-pentest |
| Supply Chain | dependency-and-secret-audit, ci-cd-supply-chain-security, active-directory-and-identity-audit |
| Specialized | exploit-validation, mobile-security-assessment, llm-and-ai-security |
| Reporting & Audit | evidence-and-reporting, specter-delta |

All skill files are at `.specter/skills/<name>/SKILL.md`. Read the SKILL.md before starting work.

## Post-Task Security Gate

After completing any coding or security task, run a fast delta audit:

1. Check for `.specter/.audit-pending` (written by the Stop hook if configured)
2. If present (or after any file modifications), invoke `.specter/skills/specter-delta/SKILL.md`
3. **S1 Critical** — STOP. Fix immediately. Task is not complete.
4. **S2 High** — Fix before closing, or get explicit user acceptance in writing.
5. **S3–S5** — Log to `.specter/findings/` and surface as a warning. Task may close.
6. Persist any findings via `python3 .specter/scripts/findings_index.py add '<json>'`
7. Delete `.specter/.audit-pending` when done

At the start of every new conversation, check `.specter/findings/index.json` for open S1/S2 findings and surface them before beginning new work.
