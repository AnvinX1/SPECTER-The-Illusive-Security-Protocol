#!/usr/bin/env python3
"""
specter_utils.py — Shared utilities for SPECTER Python scripts.

Provides:
  - FINDING_HEADER_RE / FIELD_RE  : canonical parsing regex
  - parse_findings()              : unified finding extractor
  - Severity / confidence / status constants and validation helpers
  - resolve_index_path()          : CWD-walking .specter locator

Importing scripts should use:
    from specter_utils import parse_findings, VALID_SEVERITIES, resolve_index_path
"""

import re
import sys
from pathlib import Path

# ── Canonical parsing regex ────────────────────────────────────────────────────
#
# Matches all finding header variants used across the skill set:
#   ### Finding: Title               (legacy / simple format)
#   ### Finding - Title
#   ### D-001: Title                 (specter-delta delta findings)
#   ### F-001: Title                 (normalize_finding output)
#   ### [D-001]: Title               (bracket-wrapped ID)
#
# Group 1: the finding ID (e.g. "D-001", "F-001") or the word "Finding"
# Group 2: the finding title text

FINDING_HEADER_RE = re.compile(
    r"^###\s+"
    r"\[?([A-Z][A-Z0-9]*-\d+[A-Z0-9]*|Finding)\]?\s*"
    r"[:\-]\s*(.+)",
    re.IGNORECASE,
)

FIELD_RE = re.compile(r"^\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|")

# ── Severity / confidence / status constants ───────────────────────────────────

VALID_SEVERITIES = {"S1", "S2", "S3", "S4", "S5"}
VALID_CONFIDENCES = {"C1", "C2", "C3", "C4"}
VALID_STATUSES = {
    "Confirmed",
    "Suspected",
    "Remediated",
    "Accepted Risk",
    "False Positive",
}

SEVERITY_ORDER = {"S1": 0, "S2": 1, "S3": 2, "S4": 3, "S5": 4}

SEVERITY_LABELS = {
    "S1": "Critical",
    "S2": "High",
    "S3": "Medium",
    "S4": "Low",
    "S5": "Informational",
}

CONFIDENCE_LABELS = {
    "C1": "Confirmed",
    "C2": "High Confidence",
    "C3": "Moderate",
    "C4": "Tentative",
}

SEVERITY_WEIGHTS = {"S1": 10, "S2": 7, "S3": 4, "S4": 1, "S5": 0}

# ── Path resolution ────────────────────────────────────────────────────────────


def resolve_index_path() -> Path:
    """Find .specter/findings/index.json by walking up from the current directory.

    Walks the directory tree upward from CWD, looking for the first ancestor that
    contains a .specter/ subdirectory. Falls back to the __file__-relative path
    when no .specter/ directory is found (development / testing use case).
    """
    cwd = Path.cwd()
    for candidate in [cwd, *cwd.parents]:
        specter_dir = candidate / ".specter"
        if specter_dir.is_dir():
            return specter_dir / "findings" / "index.json"
    # Fallback: used when running tests or from inside the package source tree
    return Path(__file__).parent.parent / "findings" / "index.json"


# ── Core parser ────────────────────────────────────────────────────────────────


def parse_findings(text: str, source: str | None = None) -> list[dict]:
    """Extract structured findings from a SPECTER markdown report.

    Iterates lines looking for finding header markers, accumulates per-finding
    text, and extracts | **Field** | Value | table rows into a ``fields`` dict.

    Args:
        text:   Full markdown document text.
        source: Optional source label (e.g. filename) attached to each finding.

    Returns:
        List of finding dicts, each containing:
          id      (str)  Finding ID (e.g. "D-001") or "Finding" if no ID present.
          title   (str)  Finding title from the ### header.
          fields  (dict) Lowercase-keyed table fields extracted from the finding block.
          raw     (str)  Complete raw text of the finding block, including the header.
          source  (str | None)  The ``source`` argument passed in, or None.
    """
    findings: list[dict] = []
    current: dict | None = None
    current_lines: list[str] = []

    def _flush() -> None:
        if current is None:
            return
        current["raw"] = "\n".join(current_lines)
        findings.append(current)

    for line in text.splitlines():
        m = FINDING_HEADER_RE.match(line)
        if m:
            _flush()
            current = {
                "id": m.group(1).strip(),
                "title": m.group(2).strip(),
                "fields": {},
                "source": source,
            }
            current_lines = [line]
        elif current is not None:
            current_lines.append(line)
            fm = FIELD_RE.match(line)
            if fm:
                key = fm.group(1).strip().lower()
                val = fm.group(2).strip()
                current["fields"][key] = val

    _flush()
    return findings


# ── Validation helpers ────────────────────────────────────────────────────────


def severity_is_valid(value: str) -> bool:
    """Return True if value starts with a valid severity code (S1-S5)."""
    return value.strip()[:2].upper() in VALID_SEVERITIES


def confidence_is_valid(value: str) -> bool:
    """Return True if value starts with a valid confidence code (C1-C4)."""
    return value.strip()[:2].upper() in VALID_CONFIDENCES


def status_is_valid(value: str) -> bool:
    """Return True if value exactly matches a valid status string."""
    return value.strip() in VALID_STATUSES


# ── Severity sort key ─────────────────────────────────────────────────────────


def severity_sort_key(finding: dict) -> int:
    """Return an integer sort key from a finding's severity field (lower = higher priority).

    Reads ``finding["fields"].get("severity", "S5")``.
    """
    sev = finding.get("fields", {}).get("severity") or ""
    for prefix, order in SEVERITY_ORDER.items():
        if sev.upper().startswith(prefix):
            return order
    return len(SEVERITY_ORDER)


# ── Entry point guard ────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("specter_utils.py — shared utilities module, not a standalone script.", file=sys.stderr)
    sys.exit(0)
