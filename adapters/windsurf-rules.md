# SPECTER Security Protocol

This project uses SPECTER (The Illusive Security Protocol) — a modular security skills system at `.specter/`.

## Security Work Protocol

For any security assessment, pentest, code review, vulnerability analysis, or bug bounty work:

1. **Governance**: Read `.specter/skills/security-governance/SKILL.md` first. Confirm authorization and scope.
2. **Skill selection**: Read `.specter/specter.md` for the full skill index. Match the task to the right skill.
3. **Finding format**: Use `.specter/references/report-template.md` format. Severity per `.specter/references/severity-matrix.md`.
4. **Triage**: Route all findings through `.specter/skills/bug-bounty-triage/SKILL.md`.

## Key Rules

- Authorization required before any testing
- Suspected ≠ Confirmed — separate clearly
- Redact PII and credentials in all output
- Follow skill workflows exactly as defined

18 skills installed covering: governance, recon, threat modeling, code review, API security, AI/LLM security, web config, cloud, containers, network, supply chain, CI/CD, identity/AD, exploit validation, mobile, reporting, and continuous delta audit.

Full details: `.specter/specter.md`
