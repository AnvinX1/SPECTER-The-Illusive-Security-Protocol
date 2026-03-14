# Changelog

All notable changes to SPECTER are documented here following [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.4.0] — 2026-03-14

### Added
- **World-class terminal animation** — 7-phase sequence in both `npm install` and `specter banner`: boot typewriter, matrix burst (katakana/block chars), tri-pulse scan bar, 3-pass glitch logo with gradient reveal, typewritten author line, count-up stats (0→18/14/15 with ✓ flash), status panel, blinking CTA cursor
- **3 new built-in agent adapters** — Zed Editor (`.zed/specter.md`), Continue.dev (`.continue/specter.md`), Cline (`.clinerules`) — now 8 total agents
- **`--agent custom`** — `specter init --agent custom --src <file> --dest <path>` installs SPECTER into any AI tool
- **`specter list --agents`** — lists all 8 supported platforms with target paths
- Auto-detection for Zed, Continue.dev, and Cline in `detectAgents()`
- **`LICENSE`** — explicit MIT license: `Copyright (c) 2026 Anvin (Illusive Operations)`
- `createdBy` field in `.specterrc` — authorship embedded in every initialized project
- SIGINT cleanup in both animated banners — restores cursor on Ctrl-C

### Changed
- `bin/postinstall.js` and `bin/specter.js` animation unified — both run identical 7-phase sequence
- `COUNTS` object in both JS files is single source of truth for skills/refs/scripts stats
- README intro updated: "8 agent platforms (5 auto-detected, 1 custom)"
- `CONTRIBUTING.md` adapter file reference updated from "5" to "all"

## [1.3.0] — 2026-03-14

### Added
- `specter scan` execution engine — `web`, `host`, `dir`, `all` modes with `--output` flag; runs TLS, HTTP header, port, and secret checks; exits 1 on S1 findings (`bin/specter.js`)
- `scripts/specter_utils.py` — shared utility module eliminating 4× `parse_findings()` duplication across scripts
- Full `pytest` test suite (`tests/` — 14 test files, 146 tests)
- `CONTRIBUTING.md` — three-file sync rule and Python script standards
- `references/mitre-attack-mapping.md` — full SPECTER skill-to-ATT&CK technique mapping table
- `references/attack-chains-and-pivoting.md` — common chain patterns, pivot techniques, severity calculation
- `CHANGELOG.md` (this file)
- MITRE ATT&CK mapping sections in `active-directory-and-identity-audit`, `network-infrastructure-pentest`, `exploit-validation`, `indepth-recon-analysis`, `ci-cd-supply-chain-security`
- `red-team-simulation/SKILL.md` — 19th skill: full kill-chain adversarial simulation

### Fixed
- **Installer parity** — `bin/specter.js` SKILL_DIRS and `setup.sh` skill_dirs were missing different skills; both now install the identical 18-skill set
- **`severity_stats.py` regex** — replaced `r"(?=^### F-\d+:)"` (matches only `F-NNN` format) with line-by-line iterator using unified `FINDING_HEADER_RE` matching all ID formats (`D-NNN`, `F-NNN`, `[F-NNN]`, `Finding:`)
- **`http_headers_check.py --no-follow`** — flag was parsed but never wired; fixed via `NoFollowRedirectHandler` class
- **`tls_check.py` Python 3.12+ deprecation** — replaced `datetime.datetime.utcnow()` with `datetime.datetime.now(datetime.timezone.utc)`
- **`redact_evidence.py` dead code** — removed identical if/else branch; replaced with single `pattern.sub(replacement, result)`
- **`redact_evidence.py` variable-width lookbehind** — replaced `(?<=aws_secret_access_key\s{0,5}=\s{0,5})` (invalid in Python 3.14+) with capturing group approach
- **`findings_index.py` path resolution** — index path now walks CWD ancestors for `.specter/` directory; `__file__`-relative fallback for dev/test mode
- **`specter_utils.severity_sort_key`** — missing severity now returns `len(SEVERITY_ORDER)` (sorts after S5, not at S5 position)
- Adapter counts updated to 18 skills across all 5 adapter files
- `README.md` corrected skill/ref/script counts; fixed Claude Code auto-detect cell; updated Scripts count 8→14
- `bin/postinstall.js` reference count 11→12 in both static and animated banner

### Changed
- `deduplicate_findings.py`, `export_findings.py`, `merge_reports.py`, `validate_finding.py` — all now import `parse_findings` from `specter_utils` (no inline duplication)
- `bin/specter.js` — `cmdHelp()` and `cmdRun()` formatting cleaned up; `cmdScan()` added
- `.github/workflows/specter.yml` — added `pytest` step after syntax check; added `tests/**` to path trigger
- `.gitignore` — added `.pytest_cache/` and `tests/__pycache__/`
- `package.json` — added `scripts/specter_utils.py`, `CHANGELOG.md`, `CONTRIBUTING.md`, `references/` to `files` array

---

## [1.2.0] — 2026-03-13

### Added
- `specter-delta/SKILL.md` — fast-path post-task audit skill (18th skill)
- `scripts/post_task_audit.py` — Stop hook script writing `.specter/.audit-pending`
- `scripts/findings_index.py` — manages `.specter/findings/index.json` (add/update/list/stats subcommands)
- `.github/workflows/specter.yml` — CI for this repo + template for user project merge gate

### Changed
- `specter.instructions.md` — added mandatory Post-Task Security Gate (Steps 1–5)
- `specter.md` — added `specter-delta` to skill index; new scripts to table; Session Protocol section
- `package.json` — bumped to 1.2.0; new files in `files` array
- `setup.sh` — added `specter-delta` to `skill_dirs`; added `findings/` directory creation
- `bin/postinstall.js` — updated counts: 18 skills, 14 scripts

---

## [1.1.1] — 2026-03-11

### Fixed
- npm bin path (`npm pkg fix`)

---

## [1.1.0] — 2026-03-10

### Added
- `llm-and-ai-security` skill covering OWASP LLM Top 10, prompt injection, AI red teaming
- Active testing workflows with tool commands to existing skills

---

## [1.0.0] — 2026-03-07

### Added
- Initial release: 17 security skills, 11 reference documents, 8 helper scripts
- Agent adapters for Claude Code, Cursor, GitHub Copilot, Windsurf, Generic (AGENTS.md)
- `specter init`, `specter list`, `specter doctor`, `specter update`, `specter run` CLI commands
- `bin/postinstall.js` animated banner
