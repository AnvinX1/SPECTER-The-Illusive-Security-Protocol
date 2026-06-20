"""Tests for normalize_finding.py — finding normalization to markdown format."""
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "toolkit" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
import normalize_finding


BASE_ARGS = [
    "--title", "SQL Injection",
    "--severity", "S1",
    "--confidence", "C1",
    "--status", "Confirmed",
    "--category", "CWE-89",
    "--target", "/api/login",
    "--summary", "Unsanitized input in login endpoint",
    "--impact", "Authentication bypass and data exfiltration",
    "--remediation", "Use parameterized queries",
]


def run_normalizer(*extra_args):
    cmd = [sys.executable, str(SCRIPTS_DIR / "normalize_finding.py"), *BASE_ARGS, *extra_args]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


class TestValidateInputs:
    def _make_args(self, **overrides):
        defaults = {
            "severity": "S1", "confidence": "C1", "status": "Confirmed", "evidence": None
        }
        defaults.update(overrides)
        return MagicMock(**defaults)

    def test_valid_inputs_no_errors(self):
        args = self._make_args()
        errors = normalize_finding.validate_inputs(args)
        assert errors == []

    def test_invalid_severity_rejected(self):
        args = self._make_args(severity="S9")
        errors = normalize_finding.validate_inputs(args)
        assert any("severity" in e.lower() for e in errors)

    def test_invalid_confidence_rejected(self):
        args = self._make_args(confidence="C9")
        errors = normalize_finding.validate_inputs(args)
        assert any("confidence" in e.lower() for e in errors)

    def test_invalid_status_rejected(self):
        args = self._make_args(status="Unknown")
        errors = normalize_finding.validate_inputs(args)
        assert any("status" in e.lower() for e in errors)

    def test_missing_evidence_file_reported(self, tmp_path):
        args = self._make_args(evidence=str(tmp_path / "nonexistent.txt"))
        errors = normalize_finding.validate_inputs(args)
        assert any("evidence" in e.lower() for e in errors)


class TestRenderFinding:
    def _make_args(self, **overrides):
        defaults = {
            "id": "F-001",
            "title": "XSS in search",
            "severity": "S2",
            "confidence": "C1",
            "status": "Confirmed",
            "category": "CWE-79",
            "target": "/search?q=",
            "summary": "Reflected XSS via q param",
            "impact": "Session hijack",
            "evidence": None,
            "remediation": "Encode output",
            "validation": None,
        }
        defaults.update(overrides)
        return MagicMock(**defaults)

    def test_renders_title_in_output(self):
        args = self._make_args()
        output = normalize_finding.render_finding(args, "F-001")
        assert "XSS in search" in output

    def test_renders_severity_field(self):
        args = self._make_args()
        output = normalize_finding.render_finding(args, "F-001")
        assert "S2" in output

    def test_renders_target_field(self):
        args = self._make_args()
        output = normalize_finding.render_finding(args, "F-001")
        assert "/search?q=" in output

    def test_no_evidence_placeholder_used(self):
        args = self._make_args(evidence=None)
        output = normalize_finding.render_finding(args, "F-001")
        assert "[No evidence file provided" in output

    def test_evidence_file_content_included(self, tmp_path):
        ev = tmp_path / "evidence.txt"
        ev.write_text("curl -s https://target?q=<script>alert(1)</script>")
        args = self._make_args(evidence=str(ev))
        output = normalize_finding.render_finding(args, "F-001")
        assert "curl" in output

    def test_custom_id_used(self):
        args = self._make_args()
        output = normalize_finding.render_finding(args, "D-042")
        assert "D-042" in output


class TestCLI:
    def test_all_required_args_produce_output(self):
        rc, out, err = run_normalizer()
        assert rc == 0, f"Unexpected error: {err}"
        assert "SQL Injection" in out

    def test_invalid_severity_exits_nonzero(self):
        rc, _, err = run_normalizer("--severity", "X9")
        assert rc != 0
        assert "severity" in err.lower() or "invalid" in err.lower()

    def test_custom_id_in_output(self):
        rc, out, _ = run_normalizer("--id", "D-007")
        assert rc == 0
        assert "D-007" in out

    def test_all_severity_values_accepted(self):
        for sev in ["S1", "S2", "S3", "S4", "S5"]:
            cmd = [sys.executable, str(SCRIPTS_DIR / "normalize_finding.py"),
                   "--title", "Test", "--severity", sev, "--confidence", "C2",
                   "--status", "Suspected", "--category", "CWE-1",
                   "--target", "/test", "--summary", "test summary",
                   "--impact", "test impact", "--remediation", "fix it"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            assert result.returncode == 0, f"Failed for severity {sev}: {result.stderr}"
