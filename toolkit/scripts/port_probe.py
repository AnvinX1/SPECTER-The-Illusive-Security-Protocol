#!/usr/bin/env python3
"""
port_probe.py — Fast TCP port prober with banner grabbing.

Usage:
    python port_probe.py <host> [--ports top100] [--threads 50] [--timeout 1.0]
    python port_probe.py 10.0.0.1
    python port_probe.py example.com --ports top1000
    python port_probe.py 192.168.1.1 --ports 22,80,443,8080,3306
    python port_probe.py 10.0.0.1 --ports 1-1024 --threads 100

Port specs:
    top100    — 100 most commonly scanned ports (default)
    top1000   — ~1000 ports (1–1024 + well-known high ports)
    22,80,443 — comma-separated list
    1-1024    — range

Requires no external dependencies (stdlib only).
"""

import argparse
import concurrent.futures
import socket
import sys
from typing import Optional

# ── Well-known service names ───────────────────────────────────────────────────
PORT_SERVICES = {
    21: "FTP",           22: "SSH",            23: "Telnet",
    25: "SMTP",          53: "DNS",             67: "DHCP",
    69: "TFTP",          80: "HTTP",           110: "POP3",
    111: "RPC",          119: "NNTP",          123: "NTP",
    135: "MSRPC",       137: "NetBIOS-NS",     139: "NetBIOS-SMB",
    143: "IMAP",        161: "SNMP",           179: "BGP",
    389: "LDAP",        443: "HTTPS",          445: "SMB",
    465: "SMTPS",       514: "Syslog",         587: "SMTP-TLS",
    636: "LDAPS",       993: "IMAPS",          995: "POP3S",
    1433: "MSSQL",      1521: "Oracle",       2049: "NFS",
    2181: "ZooKeeper",  2375: "Docker(unauth)", 2376: "Docker-TLS",
    3000: "Dev-HTTP",   3306: "MySQL",         3389: "RDP",
    4444: "Metasploit", 5000: "Dev-HTTP",      5432: "PostgreSQL",
    5601: "Kibana",     5900: "VNC",           6379: "Redis(unauth)",
    6443: "K8s-API",    7001: "WebLogic",      8080: "HTTP-Alt",
    8443: "HTTPS-Alt",  8888: "Dev-HTTP",      9000: "PHP-FPM",
    9090: "Prometheus", 9200: "Elasticsearch(unauth)", 9300: "ES-Cluster",
    10250: "Kubelet-API", 27017: "MongoDB(unauth)",
}

# High-risk if externally accessible
HIGH_RISK = {
    23, 135, 137, 139, 445, 161, 2375, 3389, 4444,
    5900, 6379, 7001, 9200, 10250, 27017,
}

# Top 100 most commonly scanned ports
TOP_100 = sorted(set([
    21, 22, 23, 25, 53, 69, 80, 110, 111, 119, 123, 135, 137, 139, 143,
    161, 179, 389, 443, 445, 465, 514, 587, 636, 993, 995, 1433, 1521,
    2049, 2181, 2375, 2376, 3000, 3306, 3389, 4444, 5000, 5432, 5601,
    5900, 6379, 6443, 7001, 8000, 8008, 8080, 8443, 8888, 9000, 9090,
    9200, 9300, 10250, 27017,
]))

TOP_1000 = sorted(set(list(range(1, 1025)) + TOP_100))


def parse_ports(spec: str) -> list:
    spec = spec.strip().lower()
    if spec == "top100":
        return TOP_100
    if spec == "top1000":
        return TOP_1000
    ports = set()
    for part in spec.split(","):
        part = part.strip()
        if "-" in part and not part.startswith("-"):
            lo, hi = part.split("-", 1)
            ports.update(range(int(lo), int(hi) + 1))
        elif part.isdigit():
            ports.add(int(part))
    return sorted(ports)


def probe_port(host: str, port: int, timeout: float) -> Optional[dict]:
    """TCP connect to host:port. Returns result dict if open, None if closed/filtered."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        if sock.connect_ex((host, port)) != 0:
            sock.close()
            return None

        # Port is open — attempt banner grab
        banner = None
        try:
            sock.settimeout(2.0)
            # Send minimal HTTP probe for common web ports
            if port in (80, 8080, 8008, 8090, 8888, 3000, 5000, 4200, 9000):
                sock.sendall(b"HEAD / HTTP/1.0\r\nHost: " + host.encode() + b"\r\n\r\n")
            else:
                sock.sendall(b"\r\n")
            raw = sock.recv(256)
            banner = raw.decode("utf-8", errors="replace").strip()[:120]
        except Exception:
            pass
        finally:
            sock.close()

        return {"port": port, "banner": banner}
    except Exception:
        return None


def scan(host: str, ports: list, threads: int, timeout: float) -> list:
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as ex:
        futures = {ex.submit(probe_port, host, p, timeout): p for p in ports}
        for fut in concurrent.futures.as_completed(futures):
            r = fut.result()
            if r:
                results.append(r)
    return sorted(results, key=lambda x: x["port"])


def build_findings(open_ports: list, host: str) -> list:
    findings = []
    for p in open_ports:
        port = p["port"]
        service = PORT_SERVICES.get(port, "Unknown")
        severity = "S2" if port in HIGH_RISK else "S4"
        findings.append({
            "port": port,
            "service": service,
            "severity": severity,
            "banner": (p.get("banner") or "(no banner)")[:80],
            "high_risk": port in HIGH_RISK,
        })
    return findings


def print_results(findings: list, host: str, scanned: int) -> None:
    print(f"\n## Port Probe Results\n")
    print(f"**Target:** `{host}`  ")
    print(f"**Ports Scanned:** {scanned}  ")
    print(f"**Open Ports:** {len(findings)}\n")

    if not findings:
        print("No open TCP ports found in the scanned range.")
        return

    print("| Port | Service | Severity | Banner |")
    print("|------|---------|----------|--------|")
    for f in findings:
        risk_tag = " ⚠ HIGH RISK" if f["high_risk"] else ""
        banner_short = f["banner"][:60].replace("|", "\\|")
        print(f"| `{f['port']}` | {f['service']}{risk_tag} | {f['severity']} | `{banner_short}` |")

    risky = [f for f in findings if f["high_risk"]]
    if risky:
        print(f"\n### High-Risk Open Ports ({len(risky)})\n")
        for f in risky:
            print(f"- **Port {f['port']}** ({f['service']}): {f['banner'][:60]}")
        print(
            "\n> Investigate each high-risk port. Validate external exposure before reporting. "
            "Route confirmed findings through `bug-bounty-triage`."
        )
    else:
        print(
            "\n> No high-risk ports found in scanned range. "
            "Review open ports against expected service inventory."
        )


def main():
    parser = argparse.ArgumentParser(
        description="Fast TCP port prober with banner grabbing."
    )
    parser.add_argument("host", help="Target hostname or IP address")
    parser.add_argument(
        "--ports", default="top100",
        help="Ports: top100 (default), top1000, 22,80,443, or 1-1024",
    )
    parser.add_argument(
        "--threads", type=int, default=50,
        help="Parallel threads (default: 50)",
    )
    parser.add_argument(
        "--timeout", type=float, default=1.0,
        help="Per-port TCP timeout in seconds (default: 1.0)",
    )
    args = parser.parse_args()

    # Resolve host early
    try:
        ip = socket.gethostbyname(args.host)
        if ip != args.host:
            print(f"**Resolved:** `{args.host}` → `{ip}`")
    except socket.gaierror as exc:
        print(f"ERROR: Cannot resolve '{args.host}': {exc}", file=sys.stderr)
        sys.exit(1)

    ports = parse_ports(args.ports)
    print(f"Scanning {len(ports)} ports on {args.host}…", flush=True)

    open_ports = scan(args.host, ports, args.threads, args.timeout)
    findings = build_findings(open_ports, args.host)
    print_results(findings, args.host, len(ports))

    if any(f["high_risk"] for f in findings):
        sys.exit(1)


if __name__ == "__main__":
    main()
