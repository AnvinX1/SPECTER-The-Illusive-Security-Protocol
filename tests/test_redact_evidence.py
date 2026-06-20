"""Tests for redact_evidence.py — PII and secret redaction."""
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "toolkit" / "scripts"


def run_redact(input_text=None, input_file=None, args=None):
    cmd = [sys.executable, str(SCRIPTS_DIR / "redact_evidence.py")]
    if input_file:
        cmd.append(str(input_file))
    else:
        cmd.append("-")
    if args:
        cmd.extend(args)
    if input_text:
        result = subprocess.run(cmd, input=input_text, capture_output=True, text=True)
    else:
        result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


class TestRedactEvidence:
    def test_email_redacted(self):
        rc, out, _ = run_redact("Contact user@example.com for support")
        assert rc == 0
        assert "user@example.com" not in out
        assert "[REDACTED_EMAIL]" in out

    def test_aws_key_redacted(self):
        rc, out, _ = run_redact("AWS Key: AKIAIOSFODNN7EXAMPLE is exposed")
        assert rc == 0
        assert "AKIAIOSFODNN7EXAMPLE" not in out
        assert "AKIA[REDACTED]" in out

    def test_jwt_redacted(self):
        jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        # Use 'Value:' prefix — no keyboard trigger word — so JWT pattern fires
        rc, out, _ = run_redact(f"Value: {jwt}")
        assert rc == 0
        assert jwt not in out
        assert "[REDACTED_JWT]" in out

    def test_dry_run_shows_count_no_change(self):
        text = "Email: user@example.com"
        rc, out, _ = run_redact(text, args=["--dry-run"])
        assert rc == 0
        assert "user@example.com" in out or "Dry Run" in out
        # Dry run should show the count table, not the redacted text
        assert "[REDACTED_EMAIL]" not in out

    def test_clean_text_passes_through(self):
        text = "# Security Report\n\nNo sensitive data here."
        rc, out, _ = run_redact(text)
        assert rc == 0
        assert "Security Report" in out

    def test_output_to_file(self, tmp_path):
        input_file = tmp_path / "input.md"
        output_file = tmp_path / "redacted.md"
        input_file.write_text("User: admin@example.com logged in")
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "redact_evidence.py"),
                str(input_file),
                "-o",
                str(output_file),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert output_file.exists()
        content = output_file.read_text()
        assert "admin@example.com" not in content
        assert "[REDACTED_EMAIL]" in content
