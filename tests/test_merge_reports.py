"""Tests for merge_reports.py — report merging and severity sorting."""
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "toolkit" / "scripts"


def run_merge(report_paths, output, title=None):
    cmd = [sys.executable, str(SCRIPTS_DIR / "merge_reports.py")]
    for p in report_paths:
        cmd.append(str(p))
    cmd.extend(["-o", str(output)])
    if title:
        cmd.extend(["--title", title])
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


class TestMergeReports:
    def test_merge_single_report(self, tmp_path, sample_report_path):
        output = tmp_path / "merged.md"
        rc, _, err = run_merge([sample_report_path], output)
        assert rc == 0
        assert output.exists()

    def test_merged_output_contains_findings(self, tmp_path, sample_report_path):
        output = tmp_path / "merged.md"
        run_merge([sample_report_path], output)
        content = output.read_text()
        assert "SQL Injection" in content

    def test_merge_two_reports_combines_findings(self, tmp_path):
        r1 = tmp_path / "r1.md"
        r1.write_text("""### Finding: XSS in search
| **Severity** | S2 |
| **Affected Target** | /search |
""")
        r2 = tmp_path / "r2.md"
        r2.write_text("""### Finding: CSRF missing
| **Severity** | S3 |
| **Affected Target** | /submit |
""")
        output = tmp_path / "merged.md"
        rc, _, err = run_merge([r1, r2], output)
        assert rc == 0
        content = output.read_text()
        assert "XSS" in content
        assert "CSRF" in content

    def test_s1_appears_before_s3_in_merged(self, tmp_path):
        r1 = tmp_path / "r1.md"
        r1.write_text("""### Finding: Something Medium
| **Severity** | S3 |
| **Affected Target** | /api |
""")
        r2 = tmp_path / "r2.md"
        r2.write_text("""### Finding: Critical RCE
| **Severity** | S1 |
| **Affected Target** | /upload |
""")
        output = tmp_path / "merged.md"
        run_merge([r1, r2], output)
        content = output.read_text()
        s1_pos = content.find("Critical RCE")
        s3_pos = content.find("Something Medium")
        assert s1_pos < s3_pos, "S1 findings should appear before S3 in merged output"

    def test_custom_title(self, tmp_path, sample_report_path):
        output = tmp_path / "titled.md"
        run_merge([sample_report_path], output, title="Custom Title 2026")
        content = output.read_text()
        assert "Custom Title 2026" in content

    def test_missing_file_skipped_with_warning(self, tmp_path, sample_report_path):
        output = tmp_path / "partial.md"
        rc, _, err = run_merge([sample_report_path, tmp_path / "nonexistent.md"], output)
        assert rc == 0
        assert "Skipping" in err or "Warning" in err or "warning" in err
