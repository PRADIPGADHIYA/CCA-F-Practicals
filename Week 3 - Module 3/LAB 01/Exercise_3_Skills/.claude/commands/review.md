---
description: Review current changes against the checklist
allowed-tools: Bash(git diff:*), Bash(git status:*), Read, Grep
argument-hint: "[optional path or scope]"
---

Review the uncommitted changes (focus: $ARGUMENTS).

## What to do

1. Run `git status` and `git diff` (limit to $ARGUMENTS if a path was given).
2. Apply the four-point checklist below.
3. Group every finding as **blocker**, **suggestion**, or **nit**.
4. End with a one-line verdict, for example: `Needs changes: 3` or `Looks good: 0 findings`.
5. Do **not** edit files. This command is read-only.

## Four-point checklist

1. **Tests** — Does every behaviour change have a test? (see `.claude/rules/testing.md`)
2. **Type hints & docstrings** — Does every new public function have both? (see `.claude/rules/style.md`)
3. **Input validation** — Are invalid inputs (for example negative money) rejected?
4. **Boundaries** — Is money rounded to 2 decimals? Are threshold edges covered?
