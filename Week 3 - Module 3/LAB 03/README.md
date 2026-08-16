# LAB 03 — Iterative Workflows & CI/CD (Lab 3.3)

NorthPeak Outfitters refunds service. Three **separate** projects, one per
exercise, so work in Exercise 1 cannot break Exercise 2 or 3.

You do **not** need to know Python. Open each folder, follow `START_HERE.md`,
and talk to Claude Code in plain English.

| Folder | Exercise | What you practice | Network? |
|---|---|---|---|
| `Exercise_1_TDD_Loop` | Ex 1 (~15 min) | Failing test first, then implement restocking fee | No |
| `Exercise_2_Headless_CI` | Ex 2 (~12 min) | Read the GitHub Action; optional `claude -p` | Optional |
| `Exercise_3_Review_Gate` | Ex 3 (~12 min) | JSON verdict → exit 0 / 1 gate | No |

Each folder is a full copy of the starter: refunds code (6 green tests),
`/pr-review`, the GitHub Action, `review_gate.py`, and sample JSON.

## How to work

1. **File > Open Folder...** and pick **one** exercise folder.
2. Open that folder's `START_HERE.md` and follow the steps.
3. Start Claude Code **from that folder** when the exercise asks you to.
4. When you finish, open the next exercise folder the same way.

## Environment

Each folder already has a `.venv`, pytest installed, and a git baseline.

```powershell
.\.venv\Scripts\activate
pytest -q
python scripts/review_gate.py samples/sample_review.json
python scripts/review_gate.py samples/sample_review_fail.json
```

Expect: **`6 passed`**, then PASS (exit 0), then FAIL (exit 1).

## Config map

```
src/northpeak/refunds.py              refund logic (TDD target in Ex 1)
src/tests/test_refunds.py             6 pytest tests (grows to 8 in Ex 1)
CLAUDE.md                             TDD style + never weaken a test
.claude/commands/pr-review.md         /pr-review → {decision, issues} JSON
.github/workflows/claude-review.yml   headless claude -p on every PR
scripts/review_gate.py                JSON verdict → exit 0 / 1
samples/sample_review*.json           approve / request_changes examples
```
