# LAB 02 — Targeted Behavior (Lab 3.2)

NorthPeak Outfitters backend services. Three **separate** projects, one per
exercise, so work in Exercise 1 cannot break Exercise 2 or 3.

You do **not** need to know Python. Open each folder, follow `START_HERE.md`,
and talk to Claude Code in plain English.

| Folder | Exercise | What you practice |
|---|---|---|
| `Exercise_1_Path_Specific_Rules` | Ex 1 (~12 min) | Same request is strict under `auth/`, clean under `orders/` |
| `Exercise_2_Plan_Mode` | Ex 2 (~15 min) | Approve a multi-file token migration before any edit |
| `Exercise_3_Explore_Subagent` | Ex 3 (~12 min) | Map `payments/` read-only, then add a $10,000 limit |

Exercise 1 and 2 start from the official 4-test baseline (old `verify_token_v1`
still in use). Exercise 3 already has that migration done, so you can explore
and then add the money limit.

## How to work

1. **File > Open Folder...** and pick **one** exercise folder.
2. Open that folder's `START_HERE.md` and follow the steps.
3. Start Claude Code **from that folder** so it finds the root `CLAUDE.md`
   and the per-module ones under `src/`.
4. When you finish, open the next exercise folder the same way.

## Environment

Each folder already has a `.venv`, pytest installed, and a git baseline.

```powershell
.\.venv\Scripts\activate
pytest -q
```

Expect **`4 passed`** at the start of each exercise.

## Config map

```
CLAUDE.md                      general rules; explains path-specific rules
src/auth/CLAUDE.md             SECURITY-CRITICAL — never weaken a credential check
src/orders/CLAUDE.md           order conventions (token first, Decimal money)
src/payments/CLAUDE.md         MONEY-CRITICAL — verify token, reject bad amounts
.claude/agents/explorer.md     read-only survey subagent (Read, Grep, Glob)
src/auth/tokens.py             verify_token (strict) + verify_token_v1 (Ex 1 & 2)
src/orders/service.py          place_order
src/payments/charges.py        charge
src/tests/test_smoke.py        4 green pytest tests
```
