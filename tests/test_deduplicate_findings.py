"""Tests for deduplicate_findings.py — finding deduplication logic."""
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"


def run_dedup(report_path, threshold=None, output=None):
    cmd = [sys.executable, str(SCRIPTS_DIR / "deduplicate_findings.py"), str(report_path)]
    if threshold is not None:
        cmd.extend(["--threshold", str(threshold)])
    if output:
        cmd.extend(["-o", str(output)])
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


class TestDeduplicateFindings:
    def test_unique_findings_preserved(self, sample_report_path):
        rc, out, _ = run_dedup(sample_report_path)
        assert rc == 0
        assert "Deduplication Summary" in out

    def test_identical_findings_deduplicated(self, tmp_path):
        report = tmp_path / "dupes.md"
        report.write_text("""### Finding: SQL Injection
| **Severity** | S1 |
| **Confidence** | C1 |
| **Affected Target** | /api/login |

### Finding: SQL Injection
| **Severity** | S1 |
| **Confidence** | C1 |
| **Affected Target** | /api/login |
""")
        rc, out, _ = run_dedup(report, threshold=0.9)
        assert rc == 0
        assert "2 findings → 1 unique" in out

    def test_distinct_findings_not_merged(self, tmp_path):
        report = tmp_path / "distinct.md"
        report.write_text("""### Finding: SQL Injection
| **Severity** | S1 |
| **Affected Target** | /api/login |

### Finding: Cross-Site Scripting
| **Severity** | S2 |
| **Affected Target** | /comments |
""")
        rc, out, _ = run_dedup(report, threshold=0.9)
        assert rc == 0
        assert "2 findings → 2 unique" in out

    def test_output_file_written(self, tmp_path, sample_report_path):
        out_file = tmp_path / "deduped.md"
        rc, _, _ = run_dedup(sample_report_path, output=out_file)
        assert rc == 0
        assert out_file.exists()

    def test_empty_report_exits_0(self, tmp_path):
        empty = tmp_path / "empty.md"
        empty.write_text("# Report\n\nNo findings.\n")
        rc, _, err = run_dedup(empty)
        assert rc == 0
