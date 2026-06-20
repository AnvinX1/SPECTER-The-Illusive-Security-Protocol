"""Tests for cmd_runner.py — allowlisted tool execution."""
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"


def run_cmd_runner(*args):
    cmd = [sys.executable, str(SCRIPTS_DIR / "cmd_runner.py"), *args]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


class TestCmdRunner:
    def test_list_shows_tools(self):
        rc, out, _ = run_cmd_runner("--list")
        assert rc == 0
        # Should display a non-empty list of tools
        assert "nmap" in out or "nikto" in out or "sqlmap" in out or "ffuf" in out

    def test_non_allowlisted_tool_rejected(self):
        rc, _, err = run_cmd_runner("rm", "-rf", "/tmp/test")
        assert rc != 0
        assert "allowlist" in err.lower()

    def test_injection_chars_rejected(self):
        rc, _, err = run_cmd_runner("nmap", "127.0.0.1; rm -rf /")
        assert rc != 0
        assert "forbidden" in err.lower() or "injection" in err.lower() or rc == 1

    def test_semicolon_in_args_rejected(self):
        rc, _, err = run_cmd_runner("nmap", "target.com;id")
        assert rc not in (0, 124)  # Not success, not timeout

    def test_no_args_shows_usage(self):
        rc, out, err = run_cmd_runner()
        # Either shows usage/help or error — not a crash
        assert rc in (0, 1, 2)
        combined = out + err
        assert len(combined) > 0
