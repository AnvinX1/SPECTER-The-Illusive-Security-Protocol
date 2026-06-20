"""
Shared pytest fixtures for SPECTER test suite.
"""
import json
import os
import sys
from pathlib import Path

import pytest

# Ensure toolkit scripts are importable
SCRIPTS_DIR = Path(__file__).parent.parent / "toolkit" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_report_path():
    """Path to the sample report fixture."""
    return FIXTURES_DIR / "sample_report.md"


@pytest.fixture
def sample_report_text(sample_report_path):
    """Full text of the sample report fixture."""
    return sample_report_path.read_text(encoding="utf-8")


@pytest.fixture
def tmp_specter_dir(tmp_path):
    """A temporary directory tree simulating an initialized .specter/ project."""
    specter_dir = tmp_path / ".specter"
    findings_dir = specter_dir / "findings"
    findings_dir.mkdir(parents=True)
    return specter_dir


@pytest.fixture
def tmp_index_path(tmp_specter_dir):
    """Path to a fresh findings index JSON file."""
    return tmp_specter_dir / "findings" / "index.json"


@pytest.fixture
def valid_finding_dict():
    """A valid finding dict as expected by findings_index."""
    return {
        "id": "D-001",
        "title": "SQL Injection in login endpoint",
        "severity": "S1",
        "confidence": "C1",
        "status": "Confirmed",
        "file": "api/login.py",
        "line": "42",
    }


@pytest.fixture
def minimal_finding_md():
    """A minimal valid finding in markdown format."""
    return """### Finding: Test Finding Title
| **Title** | Test Finding Title |
| **Severity** | S2 |
| **Confidence** | C2 |
| **Status** | Confirmed |
| **Category** | CWE-79: XSS |
| **Affected Target** | https://example.com |
| **Issue Summary** | Test issue |
| **Impact** | Test impact |
| **Evidence** | Test evidence |
| **Remediation** | Test remediation |
| **Validation Notes** | Test notes |
"""


@pytest.fixture
def delta_finding_md():
    """A finding using D-NNN ID format (specter-delta output)."""
    return """### D-042: Missing Input Validation
| **Severity** | S2 |
| **Confidence** | C1 |
| **Status** | Confirmed |
| **Category** | CWE-20: Improper Input Validation |
| **Affected Target** | src/api/users.ts |
| **Issue Summary** | User input passed directly to database |
| **Impact** | Potential SQL injection |
| **Evidence** | Line 42: `db.query(req.body.username)` |
| **Remediation** | Sanitize and validate all user input |
| **Validation Notes** | TODO: verify fix |
"""
