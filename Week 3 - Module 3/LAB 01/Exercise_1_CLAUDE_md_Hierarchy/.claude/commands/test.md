---
description: Run the pytest suite and report pass/fail without changing code
allowed-tools: Bash(python:*), Bash(pytest:*), Read
argument-hint: "[optional pytest args]"
---

Run the NorthPeak test suite.

1. From the project root, run: `python -m pytest -q $ARGUMENTS`
2. Report the pass/fail count (for example: `4 passed`).
3. If anything failed, name the failing tests and explain the likely cause.
4. Do **not** edit any files. This command only runs tests and reports.
