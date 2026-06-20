"""Tests for port_probe.py — TCP port prober logic."""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
import port_probe


class TestParsePorts:
    def test_top100_returns_list(self):
        result = port_probe.parse_ports("top100")
        assert len(result) == len(port_probe.TOP_100)
        assert 80 in result
        assert 443 in result

    def test_top1000_returns_larger_list(self):
        result = port_probe.parse_ports("top1000")
        assert len(result) > len(port_probe.TOP_100)
        assert 1 in result
        assert 1024 in result

    def test_comma_separated_ports(self):
        result = port_probe.parse_ports("22,80,443")
        assert set(result) == {22, 80, 443}

    def test_range_spec(self):
        result = port_probe.parse_ports("100-105")
        assert result == [100, 101, 102, 103, 104, 105]

    def test_mixed_spec(self):
        result = port_probe.parse_ports("22,80-82,443")
        assert set(result) == {22, 80, 81, 82, 443}


class TestBuildFindings:
    def test_high_risk_port_severity_s2(self):
        open_ports = [{"port": 6379, "banner": "Redis"}]
        findings = port_probe.build_findings(open_ports, "127.0.0.1")
        assert findings[0]["severity"] == "S2"
        assert findings[0]["high_risk"] is True

    def test_normal_port_severity_s4(self):
        open_ports = [{"port": 8080, "banner": "HTTP-Alt"}]
        findings = port_probe.build_findings(open_ports, "127.0.0.1")
        assert findings[0]["severity"] == "S4"
        assert findings[0]["high_risk"] is False

    def test_service_name_populated(self):
        open_ports = [{"port": 22, "banner": "SSH-2.0-OpenSSH"}]
        findings = port_probe.build_findings(open_ports, "127.0.0.1")
        assert findings[0]["service"] == "SSH"

    def test_unknown_port_service_is_unknown(self):
        open_ports = [{"port": 12345, "banner": None}]
        findings = port_probe.build_findings(open_ports, "127.0.0.1")
        assert findings[0]["service"] == "Unknown"

    def test_banner_truncated_to_80_chars(self):
        long_banner = "A" * 100
        open_ports = [{"port": 80, "banner": long_banner}]
        findings = port_probe.build_findings(open_ports, "127.0.0.1")
        assert len(findings[0]["banner"]) <= 80


class TestProbePort:
    def test_closed_port_returns_none(self):
        with patch("socket.socket") as MockSocket:
            instance = MockSocket.return_value
            instance.connect_ex.return_value = 1  # Non-zero = connection refused
            result = port_probe.probe_port("127.0.0.1", 9999, 0.5)
        assert result is None

    def test_open_port_returns_dict(self):
        with patch("socket.socket") as MockSocket:
            instance = MockSocket.return_value
            instance.connect_ex.return_value = 0  # 0 = connected
            instance.recv.return_value = b"SSH-2.0-OpenSSH\r\n"
            result = port_probe.probe_port("127.0.0.1", 22, 0.5)
        assert result is not None
        assert result["port"] == 22


class TestHighRiskExitCode:
    def test_high_risk_triggers_exit_1(self):
        """scan() returning a high-risk port should cause sys.exit(1)."""
        open_ports = [{"port": 6379, "banner": "Redis"}]
        findings = port_probe.build_findings(open_ports, "127.0.0.1")
        assert any(f["high_risk"] for f in findings)

    def test_no_high_risk_no_exit(self):
        open_ports = [{"port": 80, "banner": None}]
        findings = port_probe.build_findings(open_ports, "127.0.0.1")
        assert not any(f["high_risk"] for f in findings)
