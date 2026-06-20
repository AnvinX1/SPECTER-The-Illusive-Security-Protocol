"""Tests for tls_check.py — TLS/SSL configuration checks."""
import datetime
import socket
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "toolkit" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
import tls_check


class TestParsePorts:
    """Lightweight logic tests that never hit the network."""

    def _cert_dict(self, days_from_now=365, sans=None, sig_alg="sha256WithRSAEncryption"):
        """Build a minimal cert dict as returned by getpeercert()."""
        expiry = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=days_from_now)
        cert = {
            "notAfter": expiry.strftime("%b %d %H:%M:%S %Y GMT"),
            "subjectAltName": [("DNS", s) for s in (sans or ["example.com"])],
            "signatureAlgorithm": sig_alg,
        }
        return cert

    def test_expired_cert_flagged_s1(self):
        cert = self._cert_dict(days_from_now=-5)
        info = {"cert": cert, "cipher": "ECDHE-RSA-AES256-GCM-SHA384", "tls_version": "TLSv1.3", "error": None}

        with patch.object(tls_check, "get_conn_info", return_value=info), \
             patch.object(tls_check, "_probe_max_version", return_value=False):
            findings = tls_check.run_checks("example.com", 443)

        expired = [f for f in findings if "Expired" in f["check"]]
        assert len(expired) > 0
        assert expired[0]["severity"] == "S1"

    def test_expiring_soon_flagged_s2(self):
        cert = self._cert_dict(days_from_now=10)
        info = {"cert": cert, "cipher": "ECDHE-RSA-AES256-GCM-SHA384", "tls_version": "TLSv1.3", "error": None}

        with patch.object(tls_check, "get_conn_info", return_value=info), \
             patch.object(tls_check, "_probe_max_version", return_value=False):
            findings = tls_check.run_checks("example.com", 443)

        expiring = [f for f in findings if "14 Days" in f["check"]]
        assert len(expiring) > 0
        assert expiring[0]["severity"] == "S2"

    def test_hostname_mismatch_flagged_s1(self):
        cert = self._cert_dict(sans=["other.com", "www.other.com"])
        info = {"cert": cert, "cipher": "ECDHE-RSA-AES256-GCM-SHA384", "tls_version": "TLSv1.3", "error": None}

        with patch.object(tls_check, "get_conn_info", return_value=info), \
             patch.object(tls_check, "_probe_max_version", return_value=False):
            findings = tls_check.run_checks("example.com", 443)

        mismatch = [f for f in findings if "Mismatch" in f["check"]]
        assert len(mismatch) > 0
        assert mismatch[0]["severity"] == "S1"

    def test_wildcard_san_matches_subdomain(self):
        cert = self._cert_dict(sans=["*.example.com", "example.com"])
        info = {"cert": cert, "cipher": "ECDHE-RSA-AES256-GCM-SHA384", "tls_version": "TLSv1.3", "error": None}

        with patch.object(tls_check, "get_conn_info", return_value=info), \
             patch.object(tls_check, "_probe_max_version", return_value=False):
            findings = tls_check.run_checks("api.example.com", 443)

        mismatch = [f for f in findings if "Mismatch" in f["check"]]
        assert len(mismatch) == 0

    def test_weak_tls_version_flagged_s2(self):
        cert = self._cert_dict()
        info = {"cert": cert, "cipher": "AES128-SHA", "tls_version": "TLSv1", "error": None}

        with patch.object(tls_check, "get_conn_info", return_value=info), \
             patch.object(tls_check, "_probe_max_version", return_value=False):
            findings = tls_check.run_checks("example.com", 443)

        weak_tls = [f for f in findings if "Weak TLS" in f["check"]]
        assert len(weak_tls) > 0
        assert weak_tls[0]["severity"] == "S2"

    def test_weak_cipher_flagged_s2(self):
        cert = self._cert_dict()
        info = {"cert": cert, "cipher": "RC4-SHA", "tls_version": "TLSv1.3", "error": None}

        with patch.object(tls_check, "get_conn_info", return_value=info), \
             patch.object(tls_check, "_probe_max_version", return_value=False):
            findings = tls_check.run_checks("example.com", 443)

        weak_cipher = [f for f in findings if "Cipher" in f["check"]]
        assert len(weak_cipher) > 0
        assert weak_cipher[0]["severity"] == "S2"

    def test_sha1_signature_flagged(self):
        cert = self._cert_dict(sig_alg="sha1WithRSAEncryption")
        info = {"cert": cert, "cipher": "ECDHE-RSA-AES256-GCM-SHA384", "tls_version": "TLSv1.3", "error": None}

        with patch.object(tls_check, "get_conn_info", return_value=info), \
             patch.object(tls_check, "_probe_max_version", return_value=False):
            findings = tls_check.run_checks("example.com", 443)

        weak_sig = [f for f in findings if "Signature" in f["check"]]
        assert len(weak_sig) > 0

    def test_clean_tls_produces_no_findings(self):
        cert = self._cert_dict(days_from_now=200, sans=["example.com"])
        info = {"cert": cert, "cipher": "ECDHE-RSA-AES256-GCM-SHA384", "tls_version": "TLSv1.3", "error": None}

        with patch.object(tls_check, "get_conn_info", return_value=info), \
             patch.object(tls_check, "_probe_max_version", return_value=False):
            findings = tls_check.run_checks("example.com", 443)

        assert len(findings) == 0

    def test_no_deprecation_warning_for_utcnow(self):
        """Verify that tls_check does not call datetime.datetime.utcnow() (deprecated in Python 3.12+)."""
        import warnings
        cert = self._cert_dict()
        info = {"cert": cert, "cipher": "ECDHE-RSA-AES256-GCM-SHA384", "tls_version": "TLSv1.3", "error": None}

        with patch.object(tls_check, "get_conn_info", return_value=info), \
             patch.object(tls_check, "_probe_max_version", return_value=False):
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                tls_check.run_checks("example.com", 443)

        deprecation_warnings = [
            x for x in w
            if issubclass(x.category, DeprecationWarning)
            and "utcnow" in str(x.message).lower()
        ]
        assert len(deprecation_warnings) == 0, (
            f"DeprecationWarning for utcnow detected: {deprecation_warnings}"
        )
