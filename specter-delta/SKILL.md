---
name: specter-delta
description: >
  Fast-path security audit of files changed since last commit.
  Runs automatically after every coding task. Scopes exclusively to git diff.
  Escalates to the full applicable skill if S1 or S2 findings are discovered.
priority: CRITICAL
---

# SPECTER Delta — Fast-Path Post-Task Audit

## Purpose

Run a focused, time-boxed security review of only the files modified in the
current task. Designed to execute quickly. Output is written to
the persistent findings store for accumulation across sessions.

## Trigger

- `.specter/.audit-pending` file exists (written by `scripts/post_task_audit.py` hook)
- User explicitly requests "delta audit" or "quick security check"
- Before any task is marked as completed (enforced by `specter.instructions.md`)

## Workflow

### 1. Read scope

Read `.specter/.audit-pending` to get the changed file list.
If the file does not exist, run `git diff --name-only HEAD` directly.
If that returns nothing, run `git diff --name-only HEAD~1 HEAD`.

### 2. Classify files

For each changed file, determine which checks apply:

| File Pattern | Checks to Apply |
|-------------|-----------------|
| `electron/ipc-handlers.*` | CWE-20: missing validation on new handlers; privilege boundary checks |
| `electron/preload.*` | CWE-20: unvalidated IPC surface additions; `contextBridge` exposure |
| `electron/ai-service.*` | Prompt injection, info disclosure, model output handling |
| `electron/api-server.*` | Auth bypass, rate limiting, CORS, injection |
| `components/**/*.tsx` | XSS, unvalidated event handlers, `dangerouslySetInnerHTML` usage |
| `lib/**/*.ts` | Business logic, injection patterns, auth checks |
| `**/auth*`, `**/login*` | AuthN/AuthZ weaknesses, session handling |
| `**/db*`, `**/query*` | SQL/NoSQL injection, parameter binding |
| `**/config*`, `**/.env*` | Secret exposure, insecure defaults |
| `**/upload*`, `**/file*` | Path traversal, unrestricted upload |
| `**/crypto*`, `**/hash*` | Weak algorithms, hardcoded keys |

Only run checks relevant to each file's classification. Skip unrelated checks.

### 3. Run targeted checks

For each classified file:

1. Read the file content
2. Apply only the checks from the classification table above
3. Look for:
   - Missing input validation at trust boundaries
   - Direct use of user-controlled data in sensitive operations
   - Missing authorization checks before privileged operations
   - Secrets or credentials in code or config
   - Calls to dangerous functions (`eval`, `exec`, `dangerouslySetInnerHTML`, etc.)
   - Any regression from a previous finding in `findings/index.json`

### 4. Severity gate

| Result | Action |
|--------|--------|
| S1 Critical found | **STOP.** Surface the finding immediately. Invoke the full applicable skill. Task is NOT complete. |
| S2 High found | Surface the finding. Fix before closing task OR get explicit user acceptance in writing. Invoke full skill. |
| S3 Medium found | Log finding. Surface as a warning. Task may proceed. |
| S4 / S5 found | Log finding. Task may proceed. |
| No findings | Confirm clean. Task may close. |

### 5. Write findings

Append results to `.specter/findings/<ISO-date>-delta.md` using the standard
finding format from `references/report-template.md`. Prefix finding IDs with
`D-` (delta) to distinguish from full-audit findings.

Update `.specter/findings/index.json`:
```bash
python3 .specter/scripts/findings_index.py add '<json-finding>'
```

If `findings/index.json` does not exist, initialize it first:
```json
{
  "last_audit": null,
  "audit_type": "delta",
  "open": [],
  "remediated": [],
  "accepted_risk": [],
  "false_positives": []
}
```

### 6. Delete pending file

Remove `.specter/.audit-pending` on completion:
```bash
rm -f .specter/.audit-pending
```

### 7. Exit condition

| State | Outcome |
|-------|---------|
| Zero S1/S2 findings | Task may be marked complete |
| S1/S2 present | Task is NOT complete until findings are remediated and re-verified |

## Output Format

Use the standard finding format:

```markdown
### [D-NNN]: [Title]

| Field | Value |
|-------|-------|
| **Severity** | S1-S5 |
| **Confidence** | C1-C4 |
| **Status** | Confirmed / Suspected |
| **Category** | CWE-XXX |
| **Affected Target** | file:line |

#### Issue Summary
#### Impact
#### Evidence
#### Remediation
#### Validation Notes
```

## Time Budget

Target: under 60 seconds for 10 or fewer changed files.
If more than 10 files changed, audit in this priority order:

1. IPC handlers and preload scripts
2. Authentication and authorization files
3. Database query construction
4. API endpoints
5. Components with user-controlled rendering
6. All remaining files

## Escalation Matrix

| Trigger | Escalate To |
|---------|-------------|
| S1/S2 in Electron IPC | `skills/secure-code-review/SKILL.md` |
| S1/S2 in API endpoint | `skills/api-security-review/SKILL.md` |
| S1/S2 in AI/LLM code | `skills/llm-and-ai-security/SKILL.md` |
| Secret found in code | `skills/dependency-and-secret-audit/SKILL.md` |
| Auth logic changes | `skills/secure-code-review/SKILL.md` |
| Cloud/infra config | `skills/cloud-config-audit/SKILL.md` |
