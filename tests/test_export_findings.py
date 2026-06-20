"""Tests for export_findings.py — JSON and CSV export."""
import csv
import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"


def run_export(report_path, fmt="json", severity=None, output=None):
    cmd = [
        sys.executable,
        str(SCRIPTS_DIR / "export_findings.py"),
        str(report_path),
        "--format",
        fmt,
    ]
    if severity:
        cmd.extend(["--severity", severity])
    if output:
        cmd.extend(["-o", str(output)])
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


class TestExportFindingsJSON:
    def test_json_output_valid(self, sample_report_path):
        rc, out, _ = run_export(sample_report_path, "json")
        assert rc == 0
        data = json.loads(out)
        assert isinstance(data, list)
        assert len(data) == 3

    def test_json_contains_severity(self, sample_report_path):
        rc, out, _ = run_export(sample_report_path, "json")
        data = json.loads(out)
        severities = [f.get("severity") for f in data]
        assert "S1" in severities
        assert "S3" in severities

    def test_severity_filter_s1_only(self, sample_report_path):
        rc, out, _ = run_export(sample_report_path, "json", severity="S1")
        data = json.loads(out)
        assert len(data) == 1
        assert data[0]["severity"] == "S1"

    def test_severity_filter_no_match_exits_0(self, sample_report_path):
        rc, _, err = run_export(sample_report_path, "json", severity="S2")
        assert rc == 0


class TestExportFindingsCSV:
    def test_csv_output_parseable(self, sample_report_path):
        rc, out, _ = run_export(sample_report_path, "csv")
        assert rc == 0
        reader = csv.DictReader(io.StringIO(out))
        rows = list(reader)
        assert len(rows) == 3

    def test_csv_has_expected_columns(self, sample_report_path):
        rc, out, _ = run_export(sample_report_path, "csv")
        reader = csv.DictReader(io.StringIO(out))
        fieldnames = reader.fieldnames or []
        assert "title" in fieldnames
        assert "severity" in fieldnames

    def test_output_to_file(self, tmp_path, sample_report_path):
        output_file = tmp_path / "export.json"
        rc, _, _ = run_export(sample_report_path, "json", output=output_file)
        assert rc == 0
        assert output_file.exists()
        data = json.loads(output_file.read_text())
        assert len(data) == 3
