"""Tests for specter_utils — the shared utility module."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from specter_utils import (
    CONFIDENCE_LABELS,
    FINDING_HEADER_RE,
    SEVERITY_LABELS,
    SEVERITY_ORDER,
    SEVERITY_WEIGHTS,
    VALID_CONFIDENCES,
    VALID_SEVERITIES,
    VALID_STATUSES,
    confidence_is_valid,
    parse_findings,
    resolve_index_path,
    severity_is_valid,
    severity_sort_key,
    status_is_valid,
)


class TestFindingHeaderRegex:
    """FINDING_HEADER_RE must match all in-use finding ID formats."""

    def _m(self, line):
        return FINDING_HEADER_RE.match(line)

    def test_finding_colon(self):
        m = self._m("### Finding: My Title Here")
        assert m is not None
        assert m.group(1) == "Finding"
        assert m.group(2) == "My Title Here"

    def test_finding_dash(self):
        m = self._m("### Finding - Title With Dash")
        assert m is not None
        assert m.group(2) == "Title With Dash"

    def test_d_prefix(self):
        m = self._m("### D-001: SQL Injection")
        assert m is not None
        assert m.group(1) == "D-001"
        assert m.group(2) == "SQL Injection"

    def test_f_prefix(self):
        m = self._m("### F-042: Missing HSTS")
        assert m is not None
        assert m.group(1) == "F-042"

    def test_bracket_wrapped(self):
        m = self._m("### [D-001]: Title With Brackets")
        assert m is not None
        assert m.group(1) == "D-001"
        assert m.group(2) == "Title With Brackets"

    def test_ad_prefix(self):
        m = self._m("### AD-007: Kerberoastable Account Found")
        assert m is not None
        assert m.group(1) == "AD-007"

    def test_does_not_match_h2(self):
        assert self._m("## Section Header") is None

    def test_does_not_match_h4(self):
        assert self._m("#### Sub-section") is None

    def test_does_not_match_plain_text(self):
        assert self._m("Just a normal line") is None


class TestParseFindings:
    """parse_findings() must extract structured findings from markdown."""

    def test_single_finding_standard_format(self, minimal_finding_md):
        results = parse_findings(minimal_finding_md)
        assert len(results) == 1
        f = results[0]
        assert f["id"] == "Finding"
        assert f["title"] == "Test Finding Title"
        assert f["fields"]["severity"] == "S2"
        assert f["fields"]["confidence"] == "C2"
        assert f["fields"]["status"] == "Confirmed"

    def test_delta_id_format(self, delta_finding_md):
        results = parse_findings(delta_finding_md)
        assert len(results) == 1
        assert results[0]["id"] == "D-042"
        assert results[0]["fields"]["severity"] == "S2"

    def test_multiple_findings(self, sample_report_text):
        results = parse_findings(sample_report_text)
        assert len(results) == 3

    def test_finding_ids_extracted(self, sample_report_text):
        results = parse_findings(sample_report_text)
        ids = [f["id"] for f in results]
        assert "D-001" in ids
        assert "F-001" in ids
        # "Finding" is the id for the ### Finding: ... format
        assert "Finding" in ids

    def test_source_attached(self, minimal_finding_md):
        results = parse_findings(minimal_finding_md, source="test_report.md")
        assert results[0]["source"] == "test_report.md"

    def test_source_none_by_default(self, minimal_finding_md):
        results = parse_findings(minimal_finding_md)
        assert results[0]["source"] is None

    def test_raw_text_preserved(self, minimal_finding_md):
        results = parse_findings(minimal_finding_md)
        assert "Test Finding Title" in results[0]["raw"]
        assert "S2" in results[0]["raw"]

    def test_empty_text_returns_empty(self):
        assert parse_findings("") == []
        assert parse_findings("# Just a header\n\nNo findings here.") == []

    def test_s1_severity_in_sample(self, sample_report_text):
        findings = parse_findings(sample_report_text)
        s1_findings = [f for f in findings if f["fields"].get("severity") == "S1"]
        assert len(s1_findings) == 1

    def test_fields_are_lowercase(self, minimal_finding_md):
        results = parse_findings(minimal_finding_md)
        fields = results[0]["fields"]
        # Keys must be lowercase
        for key in fields:
            assert key == key.lower(), f"Field key {key!r} should be lowercase"


class TestSeverityConstants:
    def test_all_severities_present(self):
        assert VALID_SEVERITIES == {"S1", "S2", "S3", "S4", "S5"}

    def test_severity_labels_complete(self):
        for s in VALID_SEVERITIES:
            assert s in SEVERITY_LABELS

    def test_severity_order_complete(self):
        for s in VALID_SEVERITIES:
            assert s in SEVERITY_ORDER

    def test_severity_weights_complete(self):
        for s in VALID_SEVERITIES:
            assert s in SEVERITY_WEIGHTS

    def test_s1_highest_weight(self):
        assert SEVERITY_WEIGHTS["S1"] > SEVERITY_WEIGHTS["S2"]
        assert SEVERITY_WEIGHTS["S1"] > SEVERITY_WEIGHTS["S5"]

    def test_s1_lowest_order(self):
        assert SEVERITY_ORDER["S1"] < SEVERITY_ORDER["S5"]


class TestValidationHelpers:
    def test_severity_is_valid(self):
        for s in ["S1", "S2", "S3", "S4", "S5"]:
            assert severity_is_valid(s)

    def test_severity_invalid(self):
        assert not severity_is_valid("S6")
        assert not severity_is_valid("X1")
        assert not severity_is_valid("")

    def test_confidence_is_valid(self):
        for c in ["C1", "C2", "C3", "C4"]:
            assert confidence_is_valid(c)

    def test_confidence_invalid(self):
        assert not confidence_is_valid("C5")
        assert not confidence_is_valid("")

    def test_status_is_valid(self):
        for s in VALID_STATUSES:
            assert status_is_valid(s)

    def test_status_invalid(self):
        assert not status_is_valid("Unknown")
        assert not status_is_valid("Open")
        assert not status_is_valid("")


class TestSeveritySortKey:
    def _finding(self, sev):
        return {"fields": {"severity": sev}}

    def test_s1_sorts_first(self):
        findings = [
            self._finding("S5"),
            self._finding("S1"),
            self._finding("S3"),
        ]
        findings.sort(key=severity_sort_key)
        assert findings[0]["fields"]["severity"] == "S1"
        assert findings[-1]["fields"]["severity"] == "S5"

    def test_missing_severity_sorts_last(self):
        f = {"fields": {}}
        assert severity_sort_key(f) >= len(SEVERITY_ORDER)


class TestResolveIndexPath:
    def test_returns_path_object(self):
        result = resolve_index_path()
        assert isinstance(result, Path)

    def test_path_ends_with_index_json(self):
        result = resolve_index_path()
        assert result.name == "index.json"
        assert result.parent.name == "findings"

    def test_uses_specter_dir_when_present(self, tmp_path, monkeypatch):
        specter_dir = tmp_path / ".specter"
        specter_dir.mkdir()
        monkeypatch.chdir(tmp_path)
        result = resolve_index_path()
        assert str(tmp_path) in str(result)
        assert "findings" in str(result)
