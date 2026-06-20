"""Tests for http_headers_check.py — HTTP security header checks."""
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "toolkit" / "scripts"

# ── Import the module under test ───────────────────────────────────────────────
sys.path.insert(0, str(SCRIPTS_DIR))
import http_headers_check as hhc


class TestFetchHeaders:
    def _make_mock_response(self, headers_dict, status=200, url="https://example.com"):
        mock_resp = MagicMock()
        mock_resp.getheaders.return_value = list(headers_dict.items())
        mock_resp.status = status
        mock_resp.url = url
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        return mock_resp

    def test_returns_headers_dict(self):
        mock_resp = self._make_mock_response({"Content-Type": "text/html"})
        with patch("urllib.request.urlopen", return_value=mock_resp):
            headers, status, final_url = hhc.fetch_headers("https://example.com")
        assert "content-type" in headers
        assert status == 200

    def test_no_follow_uses_custom_handler(self):
        """Verify that no-follow path builds an opener instead of using urlopen directly."""
        mock_resp = self._make_mock_response({"X-Frame-Options": "DENY"})
        mock_opener = MagicMock()
        mock_opener.open.return_value = mock_resp

        with patch("urllib.request.build_opener", return_value=mock_opener) as bp:
            hhc.fetch_headers("https://example.com", follow_redirects=False)
            # build_opener was called with a NoFollowRedirectHandler instance
            assert bp.called
            handler_arg = bp.call_args[0][0]
            assert isinstance(handler_arg, hhc.NoFollowRedirectHandler)

    def test_http_error_returns_headers(self):
        """An HTTP 4xx error should still return headers (not crash)."""
        mock_headers = MagicMock()
        mock_headers.items.return_value = [("X-Frame-Options", "DENY")]
        err = urllib.error.HTTPError(
            url="https://example.com", code=403, msg="Forbidden", hdrs=mock_headers, fp=None
        )
        with patch("urllib.request.urlopen", side_effect=err):
            headers, status, _ = hhc.fetch_headers("https://example.com")
        assert status == 403
        assert "x-frame-options" in headers


class TestNoFollowRedirectHandler:
    def test_redirect_request_returns_none(self):
        handler = hhc.NoFollowRedirectHandler()
        result = handler.redirect_request(None, None, 301, "Moved", {}, "https://other.com")
        assert result is None


class TestRunChecks:
    def _make_response_with_headers(self, headers_dict, url="https://example.com"):
        mock_resp = MagicMock()
        mock_resp.getheaders.return_value = list(headers_dict.items())
        mock_resp.status = 200
        mock_resp.url = url
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        return mock_resp

    def test_missing_hsts_flagged_as_s2(self):
        headers = {
            "Content-Security-Policy": "default-src 'self'",
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
        }
        mock_resp = self._make_response_with_headers(headers, url="https://example.com")
        with patch("urllib.request.urlopen", return_value=mock_resp):
            findings = hhc.run_checks("https://example.com")
        severities = [f["severity"] for f in findings]
        hsts_findings = [f for f in findings if "Strict-Transport-Security" in f["header"]]
        assert len(hsts_findings) > 0
        assert hsts_findings[0]["severity"] == "S2"

    def test_good_headers_produce_no_s1_s2(self):
        headers = {
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "camera=()",
        }
        mock_resp = self._make_response_with_headers(headers, url="https://example.com")
        with patch("urllib.request.urlopen", return_value=mock_resp):
            findings = hhc.run_checks("https://example.com")
        high_sev = [f for f in findings if f["severity"] in ("S1", "S2")]
        assert len(high_sev) == 0

    def test_leaky_server_header_flagged(self):
        headers = {"Server": "Apache/2.4.51 (Unix)"}
        mock_resp = self._make_response_with_headers(headers, url="http://example.com")
        with patch("urllib.request.urlopen", return_value=mock_resp):
            findings = hhc.run_checks("http://example.com")
        leaky = [f for f in findings if "Server" in f["header"]]
        assert len(leaky) > 0
        assert leaky[0]["severity"] == "S4"

    def test_hsts_excluded_on_http(self):
        """HSTS is https_only; should not be flagged for plain http targets."""
        headers = {
            "Content-Security-Policy": "default-src 'self'",
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
        }
        mock_resp = self._make_response_with_headers(headers, url="http://example.com")
        # Need to mock the http:// path — no SSL context used by urlopen for plain http
        with patch("urllib.request.urlopen", return_value=mock_resp):
            findings = hhc.run_checks("http://example.com")
        hsts_findings = [f for f in findings if "Strict-Transport-Security" in f["header"]]
        assert len(hsts_findings) == 0

    def test_misconfigured_csp_flagged(self):
        headers = {
            "Content-Security-Policy": "default-src 'self' 'unsafe-inline'",
            "Strict-Transport-Security": "max-age=31536000",
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
        }
        mock_resp = self._make_response_with_headers(headers, url="https://example.com")
        with patch("urllib.request.urlopen", return_value=mock_resp):
            findings = hhc.run_checks("https://example.com")
        csp_misconfigured = [
            f for f in findings
            if "Content-Security-Policy" in f["header"] and f["issue"] == "MISCONFIGURED"
        ]
        assert len(csp_misconfigured) > 0
