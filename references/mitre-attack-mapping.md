---
title: SPECTER — MITRE ATT&CK Skill Mapping
---

# SPECTER — MITRE ATT&CK Skill Mapping

Maps each SPECTER security skill to the MITRE ATT&CK Enterprise tactics and key
technique IDs it covers. Use this table to build ATT&CK Navigator heatmaps or to
cite framework references in findings.

## Skill → ATT&CK Mapping

| Skill | Primary Tactic | Key Technique IDs |
|-------|---------------|-------------------|
| `active-directory-and-identity-audit` | Credential Access | T1558.003 Kerberoasting · T1550.002 Pass-the-Hash · T1649 AS-REP Roasting · T1482 Domain Trust Discovery |
| `api-security-review` | Initial Access | T1190 Exploit Public-Facing App · T1059.007 JavaScript · T1552.001 Credentials in Files |
| `bug-bounty-triage` | — | Scope & intake; not adversarial |
| `ci-cd-supply-chain-security` | Persistence | T1195 Supply Chain Compromise · T1552.001 Credentials in Files · T1072 Software Deployment Tools |
| `cloud-config-audit` | Privilege Escalation | T1078.004 Cloud Accounts · T1530 Data from Cloud Storage · T1537 Transfer to Cloud Account |
| `container-and-runtime-security` | Privilege Escalation | T1611 Escape to Host · T1613 Container Discovery · T1552.007 Container API |
| `dependency-and-secret-audit` | Credential Access | T1552.001 Credentials in Files · T1195.001 Compromise Software Deps · T1588.006 Vulnerabilities |
| `evidence-and-reporting` | — | Reporting; not adversarial |
| `exploit-validation` | Execution | T1190 Exploit Public-Facing App · T1059 Command & Scripting Interpreter · T1203 Client Execution |
| `indepth-recon-analysis` | Reconnaissance | T1592 Gather Victim Host Info · T1589 Gather Identity Info · T1596 Search Technical Databases |
| `llm-and-ai-security` | Initial Access | T1190 Exploit Public-Facing App · T1059 Prompt Injection via Scripting · T1204 User Execution |
| `mobile-security-assessment` | Defense Evasion | T1405 Exploit Firmware · T1407 Download Code at Runtime · T1426 System Information Discovery |
| `network-infrastructure-pentest` | Discovery | T1046 Network Service Discovery · T1595 Active Scanning · T1018 Remote System Discovery |
| `secure-code-review` | Execution | T1059 Command & Scripting Interpreter · T1190 Exploit Public-Facing App · T1134 Access Token Manipulation |
| `security-governance` | — | Authorization & scope; not adversarial |
| `specter-delta` | — | Audit & CI gate; not adversarial |
| `threat-modeling` | — | Threat identification & risk prioritization |
| `web-misconfig-review` | Initial Access | T1190 Exploit Public-Facing App · T1212 Exploitation for Cred Access · T1557 Adversary-in-the-Middle |

---

## ATT&CK Tactics Coverage Summary

| Tactic | Skills Covering It |
|--------|--------------------|
| Reconnaissance | `indepth-recon-analysis` |
| Initial Access | `api-security-review`, `exploit-validation`, `llm-and-ai-security`, `web-misconfig-review` |
| Execution | `exploit-validation`, `secure-code-review` |
| Persistence | `ci-cd-supply-chain-security` |
| Privilege Escalation | `cloud-config-audit`, `container-and-runtime-security` |
| Defense Evasion | `mobile-security-assessment` |
| Credential Access | `active-directory-and-identity-audit`, `dependency-and-secret-audit` |
| Discovery | `network-infrastructure-pentest` |

---

## Using ATT&CK IDs in Findings

Reference ATT&CK technique IDs in the `**Category**` field:

```markdown
| **Category** | CWE-89 / T1190 — Exploit Public-Facing Application |
```

For red team engagements, use this table to produce an ATT&CK Navigator layer
(`navigator.attackiq.com`) showing which techniques your assessment covers.

---

## Technique Severity Guidance

| Technique class | Typical SPECTER Severity |
|-----------------|--------------------------|
| Pre-auth RCE / SQLi (T1190) | S1 |
| Credential theft / Kerberoasting (T1558) | S1–S2 |
| Hardcoded secrets (T1552.001) | S1 |
| Supply chain compromise (T1195) | S1–S2 |
| Misconfiguration / weak headers | S3–S4 |
| Recon / information disclosure | S4–S5 |
