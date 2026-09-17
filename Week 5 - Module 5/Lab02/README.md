# LAB 02 — Resilient Systems (Lab 5.2)

Healthcare claims pipeline: **intake → validation → adjudication**. One
project. You do **not** need to write Python — each TODO from the lab is
already filled in.

| Demo | Section | What you practice |
|---|---|---|
| 1 — Error propagation | S3 | Subagents return `StageResult`; they never raise |
| 2 — Scratchpad | S4 | Every finding is flushed to `scratchpad.json` |
| 3 — Crash recovery | S4 | Re-run skips claims already `done` or `failed` |

## How to work

1. **File > Open Folder...** and pick `Week 05/Lab02`.
2. Open `START_HERE.md`.
3. Copy `.env.example` to `.env` and paste your `ANTHROPIC_API_KEY`.
4. Create `.venv`, install, then run `python main.py`.

Intake makes a real Claude API call per claim. Claims are synthetic — no
real patient data.

## Why these three together

- **StageResult** fixes *silence* (you always know which stage failed).
- **Scratchpad** fixes *amnesia* (a crash does not wipe the audit).
- **Skip-on-restart** fixes *duplicates* (finished work is not billed twice).
