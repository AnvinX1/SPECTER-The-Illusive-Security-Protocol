"""Tests for validate_finding.py — finding format validation."""
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"


def run_validate(input_path_or_dash, args=None):
    cmd = [sys.executable, str(SCRIPTS_DIR / "validate_finding.py")]
    if input_path_or_dash == "-":
        cmd.append("-")
    else:
        cmd.append(str(input_path_or_dash))
    if args:
        cmd.extend(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


class TestValidateFinding:
    def test_valid_finding_passes(self, tmp_path, minimal_finding_md):
        f = tmp_path / "finding.md"
        f.write_text(minimal_finding_md)
        rc, out, _ = run_validate(f)
        assert rc == 0
        assert "All checks passed" in out

    def test_missing_severity_fails(self, tmp_path):
        text = """### Finding: Missing Severity
| **Confidence** | C2 |
| **Status** | Confirmed |
| **Category** | CWE-89 |
| **Affected Target** | https://example.com |
| **Issue Summary** | Test |
| **Impact** | Test |
| **Remediation** | Test |
"""
        f = tmp_path / "bad.md"
        f.write_text(text)
        rc, out, _ = run_validate(f)
        assert rc == 1
        assert "severity" in out.lower()

    def test_invalid_severity_detected(self, tmp_path):
        text = """### Finding: Bad Severity
| **Severity** | X9 |
| **Confidence** | C1 |
| **Status** | Confirmed |
| **Category** | CWE-79 |
| **Affected Target** | https://example.com |
| **Issue Summary** | Test |
| **Impact** | Test |
| **Remediation** | Test |
"""
        f = tmp_path / "bad.md"
        f.write_text(text)
        rc, out, _ = run_validate(f)
        assert rc == 1
        assert "INVALID" in out or "invalid" in out.lower()

    def test_no_findings_exits_1(self, tmp_path):
        empty = tmp_path / "empty.md"
        empty.write_text("# No findings here\n")
        rc, _, err = run_validate(empty)
        assert rc == 1
        assert "no findings" in err.lower()

    def test_validate_all_flag(self, sample_report_path):
        rc, out, _ = run_validate(sample_report_path, ["--all"])
        assert rc == 0
        # Sample report has 3 findings
        assert out.count("Finding") >= 2

    def test_placeholder_warning_detected(self, tmp_path):
        text = """### Finding: Placeholder Test
| **Severity** | S2 |
| **Confidence** | C2 |
| **Status** | Confirmed |
| **Category** | CWE-79 |
| **Affected Target** | [INSERT TARGET HERE] |
| **Issue Summary** | Test |
| **Impact** | Test |
| **Remediation** | Test |
"""
        f = tmp_path / "placeholder.md"
        f.write_text(text)
        _, out, _ = run_validate(f)
        assert "placeholder" in out.lower() or "WARN" in out
