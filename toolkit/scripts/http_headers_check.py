#!/usr/bin/env python3
"""
http_headers_check.py — Check HTTP security headers on a live target URL.

Usage:
    python http_headers_check.py <url> [--no-follow]
    python http_headers_check.py https://example.com
    python http_headers_check.py http://staging.example.com --no-follow

Probes the target with a real HTTP request, evaluates security response headers,
and outputs SPECTER-format findings for missing or misconfigured headers.

Requires no external dependencies (stdlib only).
"""

import argparse
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

# ── Header checks ─────────────────────────────────────────────────────────────
# Each entry: header name, severity, description, remediation, optional validator
HEADER_CHECKS = [
    {
        "header": "Strict-Transport-Security",
        "severity": "S2",
        "description": "HSTS not set — browser may connect over HTTP",
        "remediation": "Strict-Transport-Security: max-age=31536000; includeSubDomains; preload",
        "https_only": True,
        "validate": lambda v: bool(re.search(r"max-age\s*=\s*(\d+)", v, re.I))
            and int(re.search(r"max-age\s*=\s*(\d+)", v, re.I).group(1)) >= 31536000,
        "validate_msg": "max-age must be >= 31536000 (1 year)",
    },
    {
        "header": "Content-Security-Policy",
        "severity": "S2",
        "description": "CSP not set — XSS and injection risk",
        "remediation": "Define a Content-Security-Policy. Minimum: default-src 'self'",
        "https_only": False,
        "validate": lambda v: "unsafe-inline" not in v and "unsafe-eval" not in v,
        "validate_msg": "CSP must not contain 'unsafe-inline' or 'unsafe-eval'",
    },
    {
        "header": "X-Frame-Options",
        "severity": "S3",
        "description": "X-Frame-Options not set — clickjacking risk",
        "remediation": "X-Frame-Options: DENY  (or use CSP: frame-ancestors 'none')",
        "https_only": False,
        "validate": lambda v: v.strip().upper() in ("DENY", "SAMEORIGIN")
            or v.strip().upper().startswith("ALLOW-FROM"),
        "validate_msg": "Value must be DENY or SAMEORIGIN",
    },
    {
        "header": "X-Content-Type-Options",
        "severity": "S3",
        "description": "X-Content-Type-Options not set — MIME sniffing enabled",
        "remediation": "X-Content-Type-Options: nosniff",
        "https_only": False,
        "validate": lambda v: v.strip().lower() == "nosniff",
        "validate_msg": "Value must be 'nosniff'",
    },
    {
        "header": "Referrer-Policy",
        "severity": "S4",
        "description": "Referrer-Policy not set — full URL may leak via Referer header",
        "remediation": "Referrer-Policy: strict-origin-when-cross-origin",
        "https_only": False,
        "validate": lambda v: v.strip().lower() in (
            "no-referrer", "no-referrer-when-downgrade", "origin",
            "origin-when-cross-origin", "same-origin", "strict-origin",
            "strict-origin-when-cross-origin", "unsafe-url",
        ),
        "validate_msg": "Must be a valid Referrer-Policy value",
    },
    {
        "header": "Permissions-Policy",
        "severity": "S4",
        "description": "Permissions-Policy not set — browser features unrestricted",
        "remediation": "Permissions-Policy: camera=(), microphone=(), geolocation=()",
        "https_only": False,
        "validate": None,
        "validate_msg": None,
    },
]

# Headers that leak server technology when present
LEAKY_HEADERS = [
    "Server", "X-Powered-By", "X-AspNet-Version",
    "X-AspNetMvc-Version", "X-Generator",
]


class NoFollowRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Redirect handler that suppresses all redirects."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # Returning None prevents redirect following


def fetch_headers(url: str, follow_redirects: bool = True) -> tuple:
    """Return (headers_lower_dict, status_code, final_url). Exits on connection error."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE  # we're checking headers, not cert trust here
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "SPECTER-Security-Scanner/1.0"},
    )
    try:
        if follow_redirects:
            response_cm = urllib.request.urlopen(req, context=ctx, timeout=15)
        else:
            opener = urllib.request.build_opener(NoFollowRedirectHandler())
            response_cm = opener.open(req, timeout=15)
        with response_cm as resp:
            headers = {k.lower(): v for k, v in resp.getheaders()}
            return headers, resp.status, resp.url
    except urllib.error.HTTPError as e:
        headers = {k.lower(): v for k, v in e.headers.items()}
        return headers, e.code, url
    except Exception as exc:
        print(f"ERROR: Could not connect to {url}: {exc}", file=sys.stderr)
        sys.exit(1)


def run_checks(url: str, follow_redirects: bool = True) -> list:
    parsed = urllib.parse.urlparse(url)
    is_https = parsed.scheme == "https"

    headers, status, final_url = fetch_headers(url, follow_redirects=follow_redirects)
    findings = []

    print(f"\n## HTTP Security Header Check\n")
    print(f"**Target:** `{final_url}`  ")
    print(f"**Status:** `{status}`  ")
    print(f"**Scheme:** `{'HTTPS' if is_https else 'HTTP'}`\n")

    # Security header checks
    for chk in HEADER_CHECKS:
        if chk["https_only"] and not is_https:
            continue
        hdr_lower = chk["header"].lower()
        val = headers.get(hdr_lower)

        if val is None:
            findings.append({
                "header": chk["header"],
                "severity": chk["severity"],
                "issue": "MISSING",
                "detail": chk["description"],
                "remediation": chk["remediation"],
            })
        elif chk["validate"] is not None:
            try:
                ok = chk["validate"](val)
            except Exception:
                ok = False
            if not ok:
                findings.append({
                    "header": chk["header"],
                    "severity": chk["severity"],
                    "issue": "MISCONFIGURED",
                    "detail": f"Value {val!r} — {chk['validate_msg']}",
                    "remediation": chk["remediation"],
                })

    # Leaky banner headers
    for lhdr in LEAKY_HEADERS:
        val = headers.get(lhdr.lower())
        if val:
            findings.append({
                "header": lhdr,
                "severity": "S4",
                "issue": "INFO LEAK",
                "detail": f"{lhdr}: {val!r} reveals server technology",
                "remediation": f"Remove or suppress the {lhdr} response header in server config.",
            })

    return findings


def print_findings(findings: list) -> None:
    if not findings:
        print("✓ All checked security headers are present and correctly configured.\n")
        return

    print(f"**Issues Found:** {len(findings)}\n")
    print("| # | Severity | Header | Issue | Detail |")
    print("|---|----------|--------|-------|--------|")
    for i, f in enumerate(findings, 1):
        detail = f["detail"][:80].replace("|", "\\|")
        print(f"| {i} | {f['severity']} | `{f['header']}` | {f['issue']} | {detail} |")

    print("\n### Remediations\n")
    for f in findings:
        print(f"- **{f['header']}** ({f['issue']}): `{f['remediation']}`")

    print(
        "\n> Validate findings against `references/web-common-risks.md`. "
        "Route confirmed issues through `bug-bounty-triage`."
    )


def main():
    parser = argparse.ArgumentParser(
        description="Check HTTP security headers on a live target URL."
    )
    parser.add_argument("url", help="Target URL (e.g., https://example.com)")
    parser.add_argument(
        "--no-follow",
        action="store_true",
        help="Do not follow HTTP redirects (check headers of first response)",
    )
    args = parser.parse_args()

    url = args.url
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    findings = run_checks(url, follow_redirects=not args.no_follow)
    print_findings(findings)

    if any(f["severity"] in ("S1", "S2") for f in findings):
        sys.exit(1)


if __name__ == "__main__":
    main()
