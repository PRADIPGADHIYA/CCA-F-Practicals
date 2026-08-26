# Exercise 2 — Schema plus semantic validation

You do **not** need to know Python. `validate()` is already implemented.
First run the **offline** check (no API key), then optionally run live.

**Time:** about 15 minutes  
**Open this folder** (`Week 04/LAB 02/Exercise_2_Validation`)

---

## What this is (in plain English)

JSON Schema can say “score is 0–10” and “recommendation is one of three
values.” It **cannot** say “a strong_hire must score at least 8.”

That cross-field policy lives in code. `validate()` returns
`(ok, list of error messages)` and never crashes.

| Rule | Example error |
|---|---|
| name is a non-empty string | `name must be a non-empty string` |
| recommendation is one of the three | `recommendation must be one of [...]` |
| score is an integer 0–10 | `score must be an integer` / `between 0 and 10` |
| reason is a non-empty string | `reason must be a non-empty string` |
| strong_hire ⇒ score ≥ 8 | `a 'strong_hire' must score >= 8` |
| no_hire ⇒ score ≤ 4 | `a 'no_hire' must score <= 4` |

Python trap: `True` counts as an integer. The validator rejects booleans.

---

## Step 0 — Setup

Copy `.env.example` to `.env` only if you will run **live**. Offline `--check`
needs no key.

```powershell
.\.venv\Scripts\activate
pip install -r requirements.txt
```

---

## Step 1 — Offline check (no API)

```powershell
python exercise_2_validation.py --check
```

**Expected:** `offline validation check passed`

It tests three fixtures:

- good record → passes
- empty name / invalid enum / score 12 → fails
- `strong_hire` with score 4 → fails (policy)

---

## Step 2 — Live run (needs API key)

```powershell
python exercise_2_validation.py
```

Each model payload should be well-formed (the schema), and `valid: True`
or a specific rule in the error list.

---

## Reflection

1. Why is `strong_hire` ⇒ score ≥ 8 in `validate()`, not in JSON Schema?
2. Why return `(ok, errors)` instead of raising an exception?
3. Why reject `bool` even after checking `isinstance(score, int)`?
