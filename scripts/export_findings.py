#!/usr/bin/env python3
"""Export findings from a markdown report to JSON or CSV.

Parses structured findings from a markdown security report and
exports them in machine-readable format for integration with
ticketing systems, dashboards, or other tooling.

Usage:
    python export_findings.py report.md --format json
    python export_findings.py report.md --format csv -o findings.csv
    python export_findings.py report.md --format json --severity S1,S2
"""

import argparse
import csv
import io
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from specter_utils import parse_findings  # noqa: E402
STANDARD_FIELDS = [
    "title",
    "severity",
    "confidence",
    "status",
    "category",
    "affected target",
    "issue summary",
    "impact",
    "evidence",
    "remediation",
    "validation notes",
]


def _flatten(findings: list[dict]) -> list[dict]:
    """Flatten specter_utils findings (with nested fields) to flat export dicts."""
    flat = []
    for f in findings:
        record = {"id": f.get("id", ""), "title": f.get("title", "")}
        record.update(f.get("fields", {}))
        flat.append(record)
    return flat


def filter_by_severity(findings: list[dict], severities: set[str]) -> list[dict]:
    """Filter findings to only include specified severity levels."""
    if not severities:
        return findings
    return [
        f for f in findings
        if any(f.get("severity", "").upper().startswith(s) for s in severities)
    ]


def export_json(findings: list[dict]) -> str:
    """Export findings as JSON."""
    return json.dumps(findings, indent=2, ensure_ascii=False)


def export_csv(findings: list[dict]) -> str:
    """Export findings as CSV."""
    if not findings:
        return ""

    # Collect all unique keys across findings, ordered by STANDARD_FIELDS first
    all_keys = []
    for field in STANDARD_FIELDS:
        if any(field in f for f in findings):
            all_keys.append(field)
    for f in findings:
        for key in f:
            if key not in all_keys:
                all_keys.append(key)

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=all_keys, extrasaction="ignore")
    writer.writeheader()
    for finding in findings:
        writer.writerow(finding)

    return output.getvalue()


def main():
    parser = argparse.ArgumentParser(description="Export markdown findings to JSON or CSV.")
    parser.add_argument("report", help="Path to markdown report file")
    parser.add_argument(
        "--format", "-f",
        choices=["json", "csv"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    parser.add_argument(
        "--severity",
        help="Comma-separated severity filter (e.g., S1,S2)",
    )
    args = parser.parse_args()

    report_path = Path(args.report)
    if not report_path.is_file():
        print(f"Error: File not found: {args.report}", file=sys.stderr)
        sys.exit(1)

    text = report_path.read_text(encoding="utf-8")
    findings = _flatten(parse_findings(text))

    if not findings:
        print("No findings found in report.", file=sys.stderr)
        sys.exit(0)

    severities = set()
    if args.severity:
        severities = {s.strip().upper() for s in args.severity.split(",")}
        findings = filter_by_severity(findings, severities)

    if args.format == "json":
        result = export_json(findings)
    else:
        result = export_csv(findings)

    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
        print(
            f"Exported {len(findings)} findings to {args.output} ({args.format})",
            file=sys.stderr,
        )
    else:
        print(result)


if __name__ == "__main__":
    main()
