# LAB 01 — Precision Prompting (Lab 4.1)

Trust & Safety triage: **REMOVE / REVIEW / ALLOW**. Three **separate**
projects, one per exercise. You do **not** need to write Python — each
folder’s prompt TODO is already filled in from the lab PDF.

| Folder | Exercise | What you practice |
|---|---|---|
| `Exercise_1_Explicit_Criteria` | Ex 1 (~15 min) | Testable definitions cut wrongful “remove” calls |
| `Exercise_2_Few_Shot` | Ex 2 (~12 min) | Three examples lock `ACTION \| rationale` |
| `Exercise_3_Generalization` | Ex 3 (~13 min) | Principles so unseen edge cases still route correctly |

## How to work

1. **File > Open Folder...** and pick **one** exercise folder.
2. Open that folder’s `START_HERE.md`.
3. Copy `.env.example` to `.env` and paste your `ANTHROPIC_API_KEY`.
4. Create `.venv`, install, then run the one Python file.

Each script makes a handful of small Claude API calls. Treat the reports
as professional triage — they are short, paraphrased descriptions.

## Why these three together

- **Criteria** fix the *decision* (what each label means).
- **Few-shot examples** fix the *format* (the exact output shape).
- **Principles** fix the *intent* (the boundary on cases you never showed).
