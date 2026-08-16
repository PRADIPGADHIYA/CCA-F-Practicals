# Exercise 3 — Explore before you change

You do **not** need to know Python. This exercise surveys an unfamiliar
module **read-only**, then makes a small, safe change.

**Time:** about 12 minutes  
**Open this folder in Cursor / VS Code** before you start  
(`LAB 02/Exercise_3_Explore_Subagent`)

This folder already has the Exercise 2 migration applied (`verify_token_v1`
is gone). You start where Exercise 3 of the lab PDF starts.

---

## What the explorer is

The explorer lives in `.claude/agents/explorer.md`.

- Its tools are only **Read, Grep, Glob**
- It **cannot** edit files
- It reports: Files, Public API, Dependencies, Watch out for

You ask the main agent to use it. You never write Python yourself.

---

## Step 0 — Confirm the environment (already done)

```powershell
.\.venv\Scripts\activate
pytest -q
```

You should see **`4 passed`**. Start Claude Code from this folder.

---

## Step 1 — Explore the payments module

Ask:

```text
Use the explorer subagent to map src/payments before we change anything.
```

**Expected:** a report that names:

- the files under `src/payments/`
- the public function `charge(token, amount)`
- that payments imports `verify_token` from `auth`
- the MONEY-CRITICAL rules (verify token, Decimal money, reject bad amounts)

Nothing should be edited. Because the migration is already done, there may
be no deprecated usage left to flag.

---

## Step 2 — Make a small, safe change with that map in hand

Ask:

```text
Add input validation so charge() rejects amounts over $10,000 with a
clear ValueError, and add a test.
```

**Expected:** `src/payments/CLAUDE.md` requires a test covering a successful
charge **and** a rejected one. Claude should add the upper-bound check
(the “amount must be positive” guard is already there) and tests for both
the accepted and the rejected case.

In plain English: a $50 charge still works; a $10,001 charge is refused.

---

## Step 3 — Confirm tests grew

```powershell
pytest -q
```

**Expected:** **`5 passed`** (the original 4 plus the new rejected-amount test).

---

## What good looks like

- Exploration happens first and changes nothing
- The report names files, `charge`, the `auth` dependency, and money-critical risks
- The follow-up edit adds the $10,000 `ValueError` plus tests for accepted and rejected cases

---

## Reflection (answer in your own words)

1. The explorer’s tools are Read, Grep, Glob — no edit. Why constrain it like that?
2. Why run exploration in a separate subagent instead of having the main agent read all the files itself?
3. How does “explore first” change the quality of the change that follows?
