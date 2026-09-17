# LAB 03 — Trust & Traceability (Lab 5.3)

AI compliance reviewer for a mock **AcmeCorp Q2 FY26** report. One project.
You do **not** need to write Python — each TODO from the lab is already
filled in.

| Demo | Section | What you practice |
|---|---|---|
| 1 — Confidence routing | S5 | Confirmed findings ≥ 0.75 auto-clear; below that go to a human |
| 2 — Provenance | S6 | Quote is attached from the real report line, never from the model |
| 3 — Confirmed vs contested | S5+S6 | Two passes; agreement confirms, disagreement is contested |

## How to work

1. **File > Open Folder...** and pick `Week 05/Lab03`.
2. Open `START_HERE.md`.
3. Copy `.env.example` to `.env` and paste your `ANTHROPIC_API_KEY`.
4. Create `.venv`, install, then run `python main.py`.

The two review passes make real Claude API calls. The report is synthetic —
no real financial data.

## Why these three together

- **Threshold** spends human time only where the model is unsure.
- **Local quotes** make every flag checkable in one click.
- **Two passes** surface disagreement instead of hiding it.
