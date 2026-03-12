#!/usr/bin/env python3
"""
tls_check.py — Check TLS/SSL configuration for a live host.

Usage:
    python tls_check.py <hostname> [--port 443]
    python tls_check.py example.com
    python tls_check.py api.example.com --port 8443

Checks: negotiated TLS version, deprecated protocol support (TLS 1.0/1.1),
certificate expiry, hostname match in SANs, weak signature algorithm,
and weak cipher suite negotiation.

Requires no external dependencies (stdlib only).
"""

import argparse
import datetime
import socket
import ssl
import sys


def _probe_max_version(hostname: str, port: int, max_ver) -> bool:
    """Test whether the server accepts a connection capped at max_ver."""
    if max_ver is None:
        return False
    try:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ctx.maximum_version = max_ver
        ctx.minimum_version = max_ver
        with socket.create_connection((hostname, port), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=hostname):
                return True
    except Exception:
        return False


def get_conn_info(hostname: str, port: int) -> dict:
    """Return TLS connection details: cert, cipher, version, error."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                cipher_name, tls_ver, _ = ssock.cipher()
                return {
                    "cert": ssock.getpeercert(),
                    "cipher": cipher_name,
                    "tls_version": tls_ver,
                    "error": None,
                }
    except ssl.SSLCertVerificationError as exc:
        # Grab cert data anyway for expiry/hostname checks
        ctx2 = ssl.create_default_context()
        ctx2.check_hostname = False
        ctx2.verify_mode = ssl.CERT_NONE
        try:
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with ctx2.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cipher_name, tls_ver, _ = ssock.cipher()
                    return {
                        "cert": ssock.getpeercert(),
                        "cipher": cipher_name,
                        "tls_version": tls_ver,
                        "error": f"Certificate verification failed: {exc}",
                    }
        except Exception as exc2:
            return {"cert": None, "cipher": None, "tls_version": None, "error": str(exc2)}
    except Exception as exc:
        return {"cert": None, "cipher": None, "tls_version": None, "error": str(exc)}


def run_checks(hostname: str, port: int) -> list:
    findings = []

    print(f"\n## TLS/SSL Security Check\n")
    print(f"**Target:** `{hostname}:{port}`\n")

    info = get_conn_info(hostname, port)

    if info["error"] and info["cert"] is None:
        print(f"ERROR: Cannot connect — {info['error']}", file=sys.stderr)
        sys.exit(1)

    if info["error"]:
        findings.append({
            "check": "Certificate Verification Failure",
            "severity": "S1",
            "detail": info["error"],
            "remediation": (
                "Fix the certificate chain. Ensure the certificate is issued by a trusted CA "
                "and that the hostname matches the presented certificate."
            ),
        })

    tls_ver = info["tls_version"] or ""
    cipher = info["cipher"] or ""

    print(f"**Negotiated TLS:** `{tls_ver}`  ")
    print(f"**Cipher Suite:** `{cipher}`\n")

    # Weak negotiated version
    if tls_ver in ("TLSv1", "TLSv1.0", "TLSv1.1"):
        findings.append({
            "check": f"Weak TLS Version Negotiated ({tls_ver})",
            "severity": "S2",
            "detail": f"Server negotiated {tls_ver} which is deprecated (RFC 8996).",
            "remediation": "Disable TLS 1.0 and TLS 1.1. Require TLS 1.2+.",
        })

    # Test if old versions are independently accepted
    for proto_name, max_ver in [
        ("TLSv1.0", ssl.TLSVersion.TLSv1 if hasattr(ssl.TLSVersion, "TLSv1") else None),
        ("TLSv1.1", ssl.TLSVersion.TLSv1_1 if hasattr(ssl.TLSVersion, "TLSv1_1") else None),
    ]:
        if max_ver and _probe_max_version(hostname, port, max_ver):
            findings.append({
                "check": f"Deprecated Protocol Accepted ({proto_name})",
                "severity": "S2",
                "detail": f"Server accepts {proto_name} connections even when not negotiated by default.",
                "remediation": (
                    f"Disable {proto_name} in server config. "
                    "Nginx: ssl_protocols TLSv1.2 TLSv1.3;  "
                    "Apache: SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1"
                ),
            })

    # Certificate checks
    cert = info["cert"]
    if cert:
        # Expiry
        not_after = cert.get("notAfter")
        if not_after:
            try:
                expiry = datetime.datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                days_left = (expiry - datetime.datetime.utcnow()).days
                print(f"**Certificate Expiry:** `{not_after}` ({days_left} days remaining)  ")
                if days_left < 0:
                    findings.append({
                        "check": "Expired Certificate",
                        "severity": "S1",
                        "detail": f"Certificate expired {abs(days_left)} days ago ({not_after}).",
                        "remediation": "Renew the certificate immediately.",
                    })
                elif days_left < 14:
                    findings.append({
                        "check": "Certificate Expiring Within 14 Days",
                        "severity": "S2",
                        "detail": f"Certificate expires in {days_left} days ({not_after}).",
                        "remediation": "Renew certificate before expiry to avoid service disruption.",
                    })
                elif days_left < 30:
                    findings.append({
                        "check": "Certificate Expiring Within 30 Days",
                        "severity": "S3",
                        "detail": f"Certificate expires in {days_left} days ({not_after}).",
                        "remediation": "Schedule certificate renewal.",
                    })
            except ValueError:
                pass

        # Hostname / SAN match
        sans = [v for t, v in cert.get("subjectAltName", []) if t == "DNS"]
        if sans:
            print(f"**SANs:** {', '.join(f'`{s}`' for s in sans[:6])}"
                  f"{'…' if len(sans) > 6 else ''}  ")
            matched = any(
                hostname == san
                or (
                    san.startswith("*.") and "." in hostname
                    and hostname.endswith("." + san[2:])
                )
                for san in sans
            )
            if not matched:
                findings.append({
                    "check": "Hostname Mismatch",
                    "severity": "S1",
                    "detail": f"'{hostname}' does not match SANs: {sans}",
                    "remediation": (
                        "Obtain a certificate that includes the target hostname, "
                        "or correct the DNS/hostname."
                    ),
                })

        # Weak signature algorithm
        sig_alg = cert.get("signatureAlgorithm", "")
        if sig_alg and ("sha1" in sig_alg.lower() or "md5" in sig_alg.lower()):
            findings.append({
                "check": "Weak Certificate Signature Algorithm",
                "severity": "S2",
                "detail": f"Signature algorithm: {sig_alg}",
                "remediation": "Replace certificate with one signed using SHA-256 or SHA-384.",
            })

    # Weak cipher
    weak_kws = ["RC4", "DES", "3DES", "NULL", "EXPORT", "ANON", "MD5"]
    if cipher and any(kw.lower() in cipher.lower() for kw in weak_kws):
        findings.append({
            "check": "Weak Cipher Suite",
            "severity": "S2",
            "detail": f"Negotiated cipher: {cipher}",
            "remediation": (
                "Prefer ECDHE+AES256-GCM-SHA384 or ECDHE+CHACHA20-POLY1305. "
                "Disable RC4, DES, 3DES, NULL, EXPORT, and anonymous ciphers."
            ),
        })

    return findings


def print_findings(findings: list) -> None:
    if not findings:
        print("\n✓ No TLS/SSL issues detected.\n")
        return

    print(f"\n**Issues Found:** {len(findings)}\n")
    print("| # | Severity | Check | Detail |")
    print("|---|----------|-------|--------|")
    for i, f in enumerate(findings, 1):
        detail = f["detail"][:80].replace("|", "\\|")
        print(f"| {i} | {f['severity']} | {f['check']} | {detail} |")

    print("\n### Remediations\n")
    for f in findings:
        print(f"- **{f['check']}**: {f['remediation']}")

    print(
        "\n> Route confirmed TLS findings through `bug-bounty-triage`. "
        "See `references/web-common-risks.md`."
    )


def main():
    parser = argparse.ArgumentParser(
        description="Check TLS/SSL configuration for a live host."
    )
    parser.add_argument("hostname", help="Target hostname (e.g., example.com)")
    parser.add_argument("--port", type=int, default=443, help="Port to check (default: 443)")
    args = parser.parse_args()

    findings = run_checks(args.hostname, args.port)
    print_findings(findings)

    if any(f["severity"] in ("S1", "S2") for f in findings):
        sys.exit(1)


if __name__ == "__main__":
    main()
