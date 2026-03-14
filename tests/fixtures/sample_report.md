# SPECTER test fixture — sample security report
# Contains 3 findings in different severity levels and both ID formats

# Assessment Summary

**Target:** `test.example.com`
**Scope:** Web application + API
**Date:** 2026-03-14

---

## Findings

### D-001: SQL Injection in User Login Endpoint
| **Title** | SQL Injection in User Login Endpoint |
| **Severity** | S1 |
| **Confidence** | C1 |
| **Status** | Confirmed |
| **Category** | CWE-89: SQL Injection |
| **Affected Target** | `https://test.example.com/api/login` |
| **Issue Summary** | The `username` parameter is directly concatenated into a SQL query without parameterization, allowing full database read/modify access. |
| **Impact** | Full database compromise, authentication bypass, potential RCE via xp_cmdshell (MSSQL). |
| **Evidence** | `POST /api/login HTTP/1.1` with `username=admin'--&password=x` returns HTTP 200 with admin session cookie. |
| **Remediation** | Use parameterized queries or prepared statements. Never interpolate user input into SQL. |
| **Validation Notes** | Confirmed via `sqlmap -u https://test.example.com/api/login --data="username=*&password=x" --level=3` |

---

### F-001: Missing Content-Security-Policy Header
| **Title** | Missing Content-Security-Policy Header |
| **Severity** | S3 |
| **Confidence** | C2 |
| **Status** | Confirmed |
| **Category** | OWASP A05:2021 Security Misconfiguration |
| **Affected Target** | `https://test.example.com/` |
| **Issue Summary** | No Content-Security-Policy header returned on any endpoint. All inline scripts executable without restriction. |
| **Impact** | Increased XSS risk. Any reflected or stored XSS finding is elevated by absence of CSP as a mitigating control. |
| **Evidence** | `curl -sI https://test.example.com/ | grep -i content-security` — no output |
| **Remediation** | Add `Content-Security-Policy: default-src 'self'; script-src 'self';` header via web server or application middleware. |
| **Validation Notes** | Verify CSP presence and evaluate policy strictness after deployment. |

---

### Finding: Informational — TLS 1.1 Still Accepted
| **Title** | Informational — TLS 1.1 Still Accepted |
| **Severity** | S5 |
| **Confidence** | C3 |
| **Status** | Suspected |
| **Category** | CWE-326: Inadequate Encryption Strength |
| **Affected Target** | `test.example.com:443` |
| **Issue Summary** | Server accepts TLS 1.1 connections even though TLS 1.2+ is negotiated by default. TLS 1.1 is deprecated per RFC 8996. |
| **Impact** | Low risk in isolation. Potential regulatory concern for PCI-DSS environments. |
| **Evidence** | `openssl s_client -connect test.example.com:443 -tls1_1 -quiet` — handshake completes |
| **Remediation** | Disable TLS 1.0 and 1.1 in server config. Nginx: `ssl_protocols TLSv1.2 TLSv1.3;` |
| **Validation Notes** | Re-test after config change. |
