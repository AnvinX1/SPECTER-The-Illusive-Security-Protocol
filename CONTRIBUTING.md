# Contributing to Specter Toolkit

Specter Toolkit is the open-source layer. Cerberus is the Araskova Labs
Rust-native agentic upgrade path; keep toolkit contributions reusable and avoid
placing private Cerberus-only behavior in public skills or scripts.

## Three-File Sync Rule (CRITICAL)

When adding **or removing** a skill, ALL THREE of these must be updated atomically
(i.e. in the same commit):

| File | Where | What to change |
|------|-------|----------------|
| `package.json` | `files` array | Add `"new-skill-name/"` |
| `setup.sh` | `skill_dirs` array | Add `new-skill-name` in alphabetical position |
| `bin/specter.js` | `SKILL_DIRS` array | Add `'new-skill-name'` in alphabetical position |

**Also update after adding a skill:**
- `bin/specter.js` → `SKILL_META`: add to the correct category
- All adapter files in `adapters/`: bump skill count + add row to skill table
- `bin/postinstall.js`: update skill count in both static banner and animated stats
- `README.md`: update skill count in intro paragraph and the Included table row

> Tip: search for the count of any existing skill (e.g. `18`) across all files before committing —
> the number should appear consistently everywhere.

---

## Python Script Standards

All scripts in `scripts/` must follow:

1. **`argparse` only** — never access `sys.argv` directly
2. **`encoding="utf-8"`** on every file open
3. **Never duplicate `parse_findings()`** — import from `specter_utils`
4. **Use shared constants** — `VALID_SEVERITIES`, `VALID_CONFIDENCES`, `VALID_STATUSES` from `specter_utils`
5. **Shebang** — `#!/usr/bin/env python3`
6. **Module docstring** with `Usage:` example at the top

### Import pattern for specter_utils

```python
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from specter_utils import parse_findings, VALID_SEVERITIES, VALID_CONFIDENCES, VALID_STATUSES
```

---

## Skill SKILL.md Format

Each skill directory must contain a `SKILL.md` with this header:

```markdown
---
name: skill-name
path: .specter/skills/skill-name/SKILL.md
applyTo: "**"
---
```

Followed by:
- Numbered step-by-step workflow
- Tool commands in fenced shell code blocks
- Output template with SPECTER-format finding tables (`| **Severity** | S? |` etc.)
- References section linking to `references/*.md` docs

---

## Running Tests

```bash
pip install pytest
pytest tests/ -v --tb=short
```

Tests live in `tests/` with one file per script. Reuse fixtures from `tests/conftest.py`
(`sample_report_path`, `tmp_specter_dir`, `minimal_finding_md`, etc.).

### Syntax check all scripts

```bash
for f in scripts/*.py; do python3 -m py_compile "$f" && echo "OK $f"; done
```

---

## PR Checklist

Before opening a pull request:

- [ ] **Three-file sync rule** followed (if adding/removing skills)
- [ ] All adapter files updated with correct skill count (if count changed)
- [ ] `pytest tests/ -v` passes with 0 failures
- [ ] Python syntax check passes for all `scripts/*.py`
- [ ] No real secrets in fixture files — use clearly fake patterns like `AKIAIOSFODNN7EXAMPLE`
- [ ] `CHANGELOG.md` updated with a `[Unreleased]` entry describing the change
- [ ] New scripts added to `package.json` `files` array

---

## Release Process

1. Update version in `package.json`, `setup.sh` (`VERSION=`), `bin/postinstall.js` banners
2. Add dated entry to `CHANGELOG.md`
3. `npm publish` from the repo root
