#!/usr/bin/env python3
"""
post_task_audit.py

Runs after every Claude Code task via the Stop hook in .claude/settings.json.
Checks git diff for changed files in security-relevant directories,
then writes .specter/.audit-pending so the AI knows a delta audit is due
at the start of the next message.

Hook configuration (.claude/settings.json):
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [{"type": "command", "command": "python3 .specter/scripts/post_task_audit.py"}]
      }
    ]
  }
}

Safe to run repeatedly — idempotent. If no watched files changed, any
existing .audit-pending file is removed.
"""

import subprocess
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Configuration ────────────────────────────────────────────────────────────

SPECTER_DIR = Path(__file__).parent.parent
PENDING_FILE = SPECTER_DIR / ".audit-pending"

# Directories to watch. Adjust for the host project's layout.
WATCHED_PREFIXES = {
    "electron/",
    "lib/",
    "components/",
    "tesserin-mcp/",
    "tesserin-cli/",
    "tesserin-daemon/",
    "src/",
    "app/",
    "api/",
    "server/",
    "backend/",
}

# File extensions considered security-relevant
WATCHED_EXTENSIONS = {
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    ".py", ".go", ".rs", ".java", ".kt",
    ".yaml", ".yml", ".json", ".toml", ".env",
    ".sh", ".bash",
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def get_changed_files() -> list[str]:
    """Return changed files from git diff HEAD (unstaged + staged)."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        # Fallback: compare last two commits (useful in CI / clean working tree)
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            capture_output=True, text=True
        )
    return result.stdout.strip().splitlines() if result.returncode == 0 else []


def is_watched(filepath: str) -> bool:
    """Return True if the file is in a watched directory with a watched extension."""
    p = Path(filepath)
    has_watched_ext = p.suffix.lower() in WATCHED_EXTENSIONS
    in_watched_dir = any(filepath.startswith(prefix) for prefix in WATCHED_PREFIXES)
    return has_watched_ext or in_watched_dir


def filter_files(all_files: list[str]) -> list[str]:
    return [f for f in all_files if is_watched(f)]


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    all_changed = get_changed_files()
    watched = filter_files(all_changed)

    if not watched:
        PENDING_FILE.unlink(missing_ok=True)
        return 0

    payload = {
        "triggered_at": datetime.now(timezone.utc).isoformat(),
        "changed_files": watched,
        "total_changed": len(all_changed),
    }

    PENDING_FILE.parent.mkdir(parents=True, exist_ok=True)
    PENDING_FILE.write_text(json.dumps(payload, indent=2))

    preview = ", ".join(watched[:5])
    ellipsis = f" … (+{len(watched) - 5} more)" if len(watched) > 5 else ""
    print(f"[SPECTER] Audit pending for {len(watched)} file(s): {preview}{ellipsis}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        # Never block Claude Code's Stop flow
        print(f"[SPECTER] post_task_audit.py error (non-fatal): {exc}", file=sys.stderr)
        sys.exit(0)
