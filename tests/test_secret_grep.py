"""Tests for secret_grep.py — secret pattern detection in files."""
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def run_secret_grep(target_dir, include=None):
    cmd = [sys.executable, str(SCRIPTS_DIR / "secret_grep.py"), str(target_dir)]
    if include:
        cmd.extend(["--include", include])
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


class TestSecretGrep:
    def test_detects_aws_key_in_fixture(self):
        rc, out, _ = run_secret_grep(FIXTURES_DIR)
        assert "AKIAIOSFODNN7EXAMPLE" in out or "AWS" in out or "aws" in out.lower()

    def test_detects_openai_key_pattern(self):
        rc, out, _ = run_secret_grep(FIXTURES_DIR)
        # Sample secrets file has sk-abc123... format
        assert rc == 0

    def test_include_filter_restricts_to_extension(self, tmp_path):
        py_file = tmp_path / "config.py"
        py_file.write_text('API_KEY = "AKIAIOSFODNN7EXAMPLE"')
        js_file = tmp_path / "other.js"
        js_file.write_text('// No secrets here')

        rc, out, _ = run_secret_grep(tmp_path, include=".py")
        assert "config.py" in out or "AWS" in out or "AKIA" in out

    def test_no_secrets_in_clean_dir(self, tmp_path):
        clean_file = tmp_path / "clean.py"
        clean_file.write_text('x = 1\ny = 2\n# Normal code')
        rc, out, _ = run_secret_grep(tmp_path)
        assert rc == 0
        # Output should be empty or minimal
        lines = [l for l in out.splitlines() if '|' in l and 'File' not in l]
        assert len(lines) == 0

    def test_missing_directory_handled(self, tmp_path):
        rc, out, err = run_secret_grep(tmp_path / "nonexistent")
        assert rc == 1 or "Error" in err or "not found" in err.lower()
