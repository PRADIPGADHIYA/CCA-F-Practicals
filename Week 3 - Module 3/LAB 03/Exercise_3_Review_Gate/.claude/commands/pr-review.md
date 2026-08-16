---
description: Review current changes and emit only a {decision, issues} JSON verdict
allowed-tools: Bash(git diff:*), Bash(git status:*), Read, Grep
argument-hint: "[optional path or scope]"
---

Review the uncommitted changes (focus: $ARGUMENTS).

## What to do

1. Run `git status` and `git diff` (limit to $ARGUMENTS if a path was given).
2. Check for missing tests, bugs, and untested behaviour changes.
3. Output **only** the JSON object below — no prose, no Markdown fences.

## Output contract (emit this and nothing else)

```json
{
  "decision": "approve",
  "issues": [
    {"severity": "blocker", "message": "..."},
    {"severity": "warning", "message": "..."},
    {"severity": "nit", "message": "..."}
  ]
}
```

- `decision` must be exactly `approve` or `request_changes`.
- Use `request_changes` if there is any **blocker** (missing test, bug, weakened check).
- Use `approve` when there are no blockers (warnings and nits are allowed).
- `issues` is an array; use `[]` if there are none.
- Do **not** edit files. This command is read-only.
