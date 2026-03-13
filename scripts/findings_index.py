#!/usr/bin/env python3
"""
findings_index.py

Maintains .specter/findings/index.json — the persistent findings store.
Called by the AI (or hooks) after each delta or full audit to persist findings.

Usage:
  python3 findings_index.py add    '<json-finding>'
  python3 findings_index.py update <id> <status>
  python3 findings_index.py list   [--severity S1|S2|S3|S4|S5] [--status open|remediated]
  python3 findings_index.py stats
  python3 findings_index.py init

Finding JSON schema (for `add`):
  {
    "id":        "D-001",
    "title":     "Missing input validation on IPC handler",
    "severity":  "S2",
    "confidence":"C1",
    "status":    "Confirmed",
    "file":      "electron/ipc-handlers.ts",
    "line":      "246",
    "session":   "2026-03-13-session-001-delta",
    "created":   "2026-03-13T16:30:00Z"   (auto-filled if omitted)
  }

Valid status values: Confirmed | Suspected | Remediated | Accepted Risk | False Positive
"""

import json
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

INDEX = Path(__file__).parent.parent / "findings" / "index.json"

VALID_SEVERITIES = {"S1", "S2", "S3", "S4", "S5"}
VALID_STATUSES   = {"Confirmed", "Suspected", "Remediated", "Accepted Risk", "False Positive"}

# ── I/O ───────────────────────────────────────────────────────────────────────

def load() -> dict:
    if INDEX.exists():
        return json.loads(INDEX.read_text())
    return _empty_index()


def _empty_index() -> dict:
    return {
        "last_audit": None,
        "audit_type": None,
        "open":          [],
        "remediated":    [],
        "accepted_risk": [],
        "false_positives": [],
    }


def save(data: dict) -> None:
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    data["last_audit"] = datetime.now(timezone.utc).isoformat()
    INDEX.write_text(json.dumps(data, indent=2))


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_init(_args, _data=None) -> int:
    """Create an empty index file if one does not already exist."""
    if INDEX.exists():
        print(f"Index already exists at {INDEX}")
        return 0
    save(_empty_index())
    print(f"Initialized findings index at {INDEX}")
    return 0


def cmd_add(args, data: dict) -> int:
    """Add a new finding to the open list."""
    try:
        finding = json.loads(args.json)
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON — {exc}", file=sys.stderr)
        return 1

    # Validate required fields
    for field in ("id", "title", "severity"):
        if field not in finding:
            print(f"Error: missing required field '{field}'", file=sys.stderr)
            return 1

    if finding["severity"] not in VALID_SEVERITIES:
        print(f"Error: severity must be one of {VALID_SEVERITIES}", file=sys.stderr)
        return 1

    # Auto-fill created timestamp
    finding.setdefault("created", datetime.now(timezone.utc).isoformat())
    finding.setdefault("status", "Confirmed")

    # Check for duplicate ID
    all_entries = (
        data["open"] + data["remediated"] +
        data["accepted_risk"] + data["false_positives"]
    )
    if any(e["id"] == finding["id"] for e in all_entries):
        print(f"Error: finding ID '{finding['id']}' already exists", file=sys.stderr)
        return 1

    data["open"].append(finding)
    save(data)
    print(f"Added {finding['id']} [{finding['severity']}]: {finding['title']}")
    return 0


def cmd_update(args, data: dict) -> int:
    """Move a finding between lists by updating its status."""
    new_status = args.status

    status_to_list = {
        "Confirmed":     "open",
        "Suspected":     "open",
        "Remediated":    "remediated",
        "Accepted Risk": "accepted_risk",
        "False Positive":"false_positives",
    }

    if new_status not in VALID_STATUSES:
        print(f"Error: status must be one of {sorted(VALID_STATUSES)}", file=sys.stderr)
        return 1

    # Find the entry across all lists
    found = None
    src_list = None
    for list_name in ("open", "remediated", "accepted_risk", "false_positives"):
        for entry in data[list_name]:
            if entry["id"] == args.id:
                found = entry
                src_list = list_name
                break
        if found:
            break

    if not found:
        print(f"Error: finding ID '{args.id}' not found", file=sys.stderr)
        return 1

    dest_list = status_to_list[new_status]
    if src_list != dest_list:
        data[src_list].remove(found)
        found["status"] = new_status
        found["updated"] = datetime.now(timezone.utc).isoformat()
        data[dest_list].append(found)
    else:
        found["status"] = new_status
        found["updated"] = datetime.now(timezone.utc).isoformat()

    save(data)
    print(f"Updated {args.id} → {new_status}")
    return 0


def cmd_list(args, data: dict) -> int:
    """List findings, optionally filtered by severity or status."""
    entries = list(data["open"])
    if hasattr(args, "status") and args.status in ("remediated",):
        entries = list(data["remediated"])

    if hasattr(args, "severity") and args.severity:
        entries = [e for e in entries if e.get("severity") == args.severity]

    if not entries:
        print("No findings match the given filters.")
        return 0

    for e in entries:
        line = e.get("line", "")
        loc  = f"{e.get('file', '?')}:{line}" if line else e.get("file", "?")
        print(f"  [{e.get('severity','?')}] {e.get('id','?')}: {e.get('title','?')} — {loc}")

    return 0


def cmd_stats(_args, data: dict) -> int:
    """Print a summary count of findings by severity."""
    counts: dict[str, int] = {}
    for f in data["open"]:
        sev = f.get("severity", "?")
        counts[sev] = counts.get(sev, 0) + 1

    print(f"Open findings:      {len(data['open'])}")
    for sev in ["S1", "S2", "S3", "S4", "S5"]:
        if sev in counts:
            print(f"  {sev}: {counts[sev]}")

    print(f"Remediated:         {len(data['remediated'])}")
    print(f"Accepted risk:      {len(data['accepted_risk'])}")
    print(f"False positives:    {len(data['false_positives'])}")

    blocking = [f for f in data["open"] if f.get("severity") in ("S1", "S2")]
    if blocking:
        print(f"\nBLOCKING (S1/S2):   {len(blocking)}")
        for f in blocking:
            print(f"  [{f['severity']}] {f['id']}: {f['title']}")

    return 0


# ── Entry ────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Manage .specter/findings/index.json"
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("init", help="Initialize an empty findings index")
    subparsers.add_parser("stats", help="Print finding counts by severity")

    p_add = subparsers.add_parser("add", help="Add a new finding")
    p_add.add_argument("json", help="Finding as a JSON string")

    p_update = subparsers.add_parser("update", help="Update a finding status")
    p_update.add_argument("id", help="Finding ID (e.g. D-001)")
    p_update.add_argument("status", help="New status")

    p_list = subparsers.add_parser("list", help="List findings")
    p_list.add_argument("--severity", choices=sorted(VALID_SEVERITIES))
    p_list.add_argument("--status", choices=["open", "remediated"])

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    data = load()
    dispatch = {
        "init":   cmd_init,
        "add":    cmd_add,
        "update": cmd_update,
        "list":   cmd_list,
        "stats":  cmd_stats,
    }
    return dispatch[args.command](args, data)


if __name__ == "__main__":
    sys.exit(main())
