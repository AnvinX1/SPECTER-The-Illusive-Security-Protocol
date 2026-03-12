#!/usr/bin/env python3
"""
cmd_runner.py — Run allowlisted security tools safely (no shell injection).

Usage:
    python cmd_runner.py [--list]
    python cmd_runner.py [--timeout N] <tool> [tool-args...]

    python cmd_runner.py nmap -sV -p 80,443 example.com
    python cmd_runner.py nikto -h https://example.com
    python cmd_runner.py testssl example.com
    python cmd_runner.py nuclei -u https://example.com -t http/vulnerabilities/
    python cmd_runner.py --list

Security design:
  - Only tools in the allowlist can be executed (no arbitrary binaries)
  - subprocess is called with shell=False — shell metacharacters in args are inert
  - Argument strings are scanned for shell chaining characters as an extra layer
  - The tool binary is resolved via shutil.which() — no PATH manipulation tricks
"""

import argparse
import shlex
import shutil
import subprocess
import sys

# ── Allowlisted tool definitions ──────────────────────────────────────────────
ALLOWED_TOOLS = {
    # Network scanning
    "nmap":         "Network mapper — port scanning, service/OS detection, NSE scripts",
    "masscan":      "High-speed TCP port scanner",
    # Web scanning
    "nikto":        "Web server scanner — misconfigs, outdated software, headers",
    "whatweb":      "Web fingerprinter — CMS, framework, server detection",
    "nuclei":       "Template-based vulnerability scanner (ProjectDiscovery)",
    "wapiti":       "Web app vulnerability scanner",
    # TLS/crypto
    "testssl.sh":   "TLS/SSL scanner — cipher suites, protocols, certificate checking",
    "testssl":      "TLS/SSL scanner (alias for testssl.sh)",
    "openssl":      "Crypto toolkit — TLS/cert inspection, encryption operations",
    # Directory/content discovery
    "gobuster":     "Directory, DNS, and vhost bruteforcer",
    "ffuf":         "Web fuzzer — directories, parameters, vhosts",
    "feroxbuster":  "Recursive content discovery tool",
    "dirb":         "Web content scanner with wordlists",
    # Recon / OSINT
    "amass":        "Attack surface mapping and subdomain enumeration",
    "subfinder":    "Passive subdomain discovery",
    "httpx":        "HTTP probe — alive check, title, tech fingerprint",
    "dnsx":         "DNS resolver and brute forcer",
    "dig":          "DNS lookup utility",
    "host":         "DNS lookup utility",
    "nslookup":     "DNS lookup utility",
    "whois":        "Domain/IP registration lookup",
    # Manual probing
    "curl":         "HTTP client — manual request crafting",
    "nc":           "Netcat — TCP/UDP connection and banner grabbing",
    "netcat":       "Netcat (alias)",
    "ping":         "ICMP reachability check",
    "traceroute":   "Network path tracing",
    "tracepath":    "Network path tracing (Linux alternative)",
    # Injection / exploitation (authorized engagements only)
    "sqlmap":       "Automated SQL injection detection and exploitation",
    # Runtime
    "python3":      "Python 3 — run SPECTER helper scripts",
    "python":       "Python — run SPECTER helper scripts",
    "grep":         "Pattern search — evidence gathering from output files",
}

# Argument substrings that indicate shell injection / command chaining attempts
_FORBIDDEN = (";", "&&", "||", "`", "$(", "\n", "\r", ">>", ">&")


def _check_args(tool_args: list) -> None:
    """Raise SystemExit if any arg contains a shell injection pattern."""
    for arg in tool_args:
        for pattern in _FORBIDDEN:
            if pattern in arg:
                print(
                    f"ERROR: Forbidden character sequence {pattern!r} in argument: {arg!r}\n"
                    "Remove shell metacharacters — cmd_runner.py does not use a shell.",
                    file=sys.stderr,
                )
                sys.exit(2)


def list_tools() -> None:
    print("\n## SPECTER Allowlisted Security Tools\n")
    print("| Tool | Description | Installed |")
    print("|------|-------------|-----------|")
    for tool, desc in sorted(ALLOWED_TOOLS.items()):
        mark = "✓" if shutil.which(tool) else "✗ not found"
        print(f"| `{tool}` | {desc} | {mark} |")
    print(
        "\nInstall missing tools via your package manager or from their official sources.\n"
        "Run a tool: `python cmd_runner.py <tool> [args...]`"
    )


def run_tool(tool: str, tool_args: list, timeout: int) -> int:
    """Resolve, validate, and execute an allowlisted tool. Returns exit code."""
    if tool not in ALLOWED_TOOLS:
        print(
            f"ERROR: '{tool}' is not in the SPECTER tool allowlist.\n"
            "Run `python cmd_runner.py --list` to see available tools.",
            file=sys.stderr,
        )
        sys.exit(2)

    binary = shutil.which(tool)
    if binary is None:
        print(
            f"ERROR: '{tool}' not found in PATH.\n"
            "Install it first, or check your PATH.",
            file=sys.stderr,
        )
        sys.exit(3)

    _check_args(tool_args)

    cmd = [binary] + tool_args
    print(f"\n[specter] Running: {' '.join(shlex.quote(c) for c in cmd)}\n", flush=True)

    try:
        result = subprocess.run(
            cmd,
            shell=False,          # NEVER True — prevents shell injection
            timeout=timeout or None,
        )
        print(f"\n[specter] Exit code: {result.returncode}", flush=True)
        return result.returncode
    except subprocess.TimeoutExpired:
        print(
            f"\n[specter] Timeout: tool exceeded {timeout}s. "
            "Partial output may be above.",
            file=sys.stderr,
        )
        return 124
    except KeyboardInterrupt:
        print("\n[specter] Interrupted.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"\n[specter] ERROR: {exc}", file=sys.stderr)
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Run allowlisted security tools safely (no shell injection).",
        usage="cmd_runner.py [--list] [--timeout N] <tool> [tool-args...]",
    )
    parser.add_argument("--list", action="store_true", help="List allowlisted tools")
    parser.add_argument(
        "--timeout", type=int, default=0,
        help="Kill tool after N seconds (0 = no timeout, default: 0)",
    )
    parser.add_argument("tool", nargs="?", help="Tool to run")
    parser.add_argument(
        "tool_args", nargs=argparse.REMAINDER,
        help="Arguments to pass directly to the tool",
    )
    args = parser.parse_args()

    if args.list:
        list_tools()
        return

    if not args.tool:
        parser.print_help()
        sys.exit(1)

    sys.exit(run_tool(args.tool, args.tool_args, args.timeout))


if __name__ == "__main__":
    main()
