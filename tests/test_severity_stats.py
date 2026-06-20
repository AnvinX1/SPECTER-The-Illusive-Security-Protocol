"""Tests for severity_stats.py — validates the fixed regex and argparse interface."""
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"


def run_severity_stats(report_path):
    """Run severity_stats.py and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "severity_stats.py"), str(report_path)],
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


class TestSeverityStatsRegex:
    """The fixed regex must match all finding ID formats."""

    def test_finds_d_prefix_findings(self, sample_report_path):
        rc, out, _ = run_severity_stats(sample_report_path)
        assert rc == 0
        assert "Total Findings:** 3" in out

    def test_counts_s1_finding(self, sample_report_path):
        rc, out, _ = run_severity_stats(sample_report_path)
        assert "| S1 | Critical | 1 |" in out

    def test_counts_s3_finding(self, sample_report_path):
        rc, out, _ = run_severity_stats(sample_report_path)
        assert "| S3 | Medium | 1 |" in out

    def test_counts_s5_finding(self, sample_report_path):
        rc, out, _ = run_severity_stats(sample_report_path)
        assert "| S5 | Informational | 1 |" in out

    def test_aggregate_score_shown(self, sample_report_path):
        rc, out, _ = run_severity_stats(sample_report_path)
        assert "Aggregate Risk Score" in out

    def test_empty_report_exits_cleanly(self, tmp_path):
        empty = tmp_path / "empty.md"
        empty.write_text("# Report with no findings\n")
        rc, out, _ = run_severity_stats(empty)
        assert rc == 0
        assert "No findings found" in out

    def test_argparse_help(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "severity_stats.py"), "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "report" in result.stdout.lower()

    def test_missing_file_exits_1(self, tmp_path):
        rc, _, err = run_severity_stats(tmp_path / "nonexistent.md")
        assert rc == 1
        assert "not found" in err.lower() or "error" in err.lower()
