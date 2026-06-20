"""Tests for findings_index.py — persistent findings store."""
import json
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"

sys.path.insert(0, str(SCRIPTS_DIR))


def run_index(args, cwd):
    """Run findings_index as a subprocess in cwd."""
    import subprocess
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "findings_index.py")] + args,
        capture_output=True,
        text=True,
        cwd=str(cwd),
    )
    return result.returncode, result.stdout, result.stderr


@pytest.fixture
def project_dir(tmp_path):
    """A temp directory with a .specter/findings/ structure."""
    specter = tmp_path / ".specter"
    (specter / "findings").mkdir(parents=True)
    return tmp_path


class TestFindingsIndexInit:
    def test_init_creates_index(self, project_dir):
        rc, out, _ = run_index(["init"], project_dir)
        assert rc == 0
        index_path = project_dir / ".specter" / "findings" / "index.json"
        assert index_path.exists()

    def test_init_idempotent(self, project_dir):
        run_index(["init"], project_dir)
        rc, out, _ = run_index(["init"], project_dir)
        assert rc == 0
        assert "already exists" in out

    def test_init_does_not_set_last_audit(self, project_dir):
        run_index(["init"], project_dir)
        index_data = json.loads(
            (project_dir / ".specter" / "findings" / "index.json").read_text()
        )
        assert index_data["last_audit"] is None


class TestFindingsIndexAdd:
    def test_add_finding(self, project_dir):
        run_index(["init"], project_dir)
        finding = json.dumps({
            "id": "T-001",
            "title": "SQL Injection",
            "severity": "S1",
        })
        rc, out, _ = run_index(["add", finding], project_dir)
        assert rc == 0
        assert "T-001" in out

    def test_add_appears_in_open(self, project_dir):
        run_index(["init"], project_dir)
        finding = json.dumps({"id": "T-002", "title": "XSS", "severity": "S2"})
        run_index(["add", finding], project_dir)
        data = json.loads(
            (project_dir / ".specter" / "findings" / "index.json").read_text()
        )
        assert any(f["id"] == "T-002" for f in data["open"])

    def test_add_duplicate_id_fails(self, project_dir):
        run_index(["init"], project_dir)
        finding = json.dumps({"id": "T-003", "title": "Test", "severity": "S3"})
        run_index(["add", finding], project_dir)
        rc, _, err = run_index(["add", finding], project_dir)
        assert rc == 1
        assert "already exists" in err

    def test_add_invalid_severity_fails(self, project_dir):
        run_index(["init"], project_dir)
        finding = json.dumps({"id": "T-004", "title": "Test", "severity": "X9"})
        rc, _, err = run_index(["add", finding], project_dir)
        assert rc == 1

    def test_add_missing_required_field_fails(self, project_dir):
        run_index(["init"], project_dir)
        finding = json.dumps({"title": "Missing ID", "severity": "S3"})
        rc, _, err = run_index(["add", finding], project_dir)
        assert rc == 1
        assert "id" in err


class TestFindingsIndexUpdate:
    def test_update_status_to_remediated(self, project_dir):
        run_index(["init"], project_dir)
        finding = json.dumps({"id": "U-001", "title": "Test", "severity": "S2"})
        run_index(["add", finding], project_dir)
        rc, out, _ = run_index(["update", "U-001", "Remediated"], project_dir)
        assert rc == 0
        data = json.loads(
            (project_dir / ".specter" / "findings" / "index.json").read_text()
        )
        assert any(f["id"] == "U-001" for f in data["remediated"])
        assert not any(f["id"] == "U-001" for f in data["open"])

    def test_update_nonexistent_id_fails(self, project_dir):
        run_index(["init"], project_dir)
        rc, _, err = run_index(["update", "NOEXIST", "Remediated"], project_dir)
        assert rc == 1

    def test_update_invalid_status_fails(self, project_dir):
        run_index(["init"], project_dir)
        finding = json.dumps({"id": "U-002", "title": "Test", "severity": "S3"})
        run_index(["add", finding], project_dir)
        rc, _, err = run_index(["update", "U-002", "BadStatus"], project_dir)
        assert rc == 1


class TestFindingsIndexList:
    def test_list_open_findings(self, project_dir):
        run_index(["init"], project_dir)
        finding = json.dumps({"id": "L-001", "title": "Listed Finding", "severity": "S2"})
        run_index(["add", finding], project_dir)
        rc, out, _ = run_index(["list"], project_dir)
        assert rc == 0
        assert "L-001" in out

    def test_list_empty(self, project_dir):
        run_index(["init"], project_dir)
        rc, out, _ = run_index(["list"], project_dir)
        assert rc == 0
        assert "No findings" in out

    def test_list_severity_filter(self, project_dir):
        run_index(["init"], project_dir)
        run_index(["add", json.dumps({"id": "LF-001", "title": "S1 finding", "severity": "S1"})], project_dir)
        run_index(["add", json.dumps({"id": "LF-002", "title": "S4 finding", "severity": "S4"})], project_dir)
        rc, out, _ = run_index(["list", "--severity", "S1"], project_dir)
        assert "LF-001" in out
        assert "LF-002" not in out


class TestFindingsIndexStats:
    def test_stats_shows_counts(self, project_dir):
        run_index(["init"], project_dir)
        run_index(["add", json.dumps({"id": "S-001", "title": "Test S1", "severity": "S1"})], project_dir)
        run_index(["add", json.dumps({"id": "S-002", "title": "Test S3", "severity": "S3"})], project_dir)
        rc, out, _ = run_index(["stats"], project_dir)
        assert rc == 0
        assert "Open findings:" in out
        assert "S1:" in out
        assert "BLOCKING" in out
