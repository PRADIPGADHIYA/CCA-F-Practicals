# Exercise 3 — Retry-and-feedback loop

You do **not** need to know Python. The retry loop is already implemented.
First run `--demo` (no API), then optionally run live.

**Time:** about 15 minutes  
**Open this folder** (`Week 04/LAB 02/Exercise_3_Retry_Loop`)

---

## What this is (in plain English)

If validation fails, do not throw the result away. Tell Claude **exactly**
what was wrong, attached to the same tool call, and let it try again.

The API channel for that is a `tool_result` with `is_error=True`. Cap
retries (here, 3) so a stuck case cannot run forever.

---

## Step 0 — Setup

Offline `--demo` needs no API key.

```powershell
.\.venv\Scripts\activate
pip install -r requirements.txt
```

---

## Step 1 — Watch the loop offline

```powershell
python exercise_3_retry_loop.py --demo
```

Simulated candidate **Alex Park**:

1. Attempt 1: `strong_hire` scored **5** → invalid (`must score >= 8`)
2. The script prints the exact feedback string that would go back to Claude
3. Attempt 2: score **9** → valid, stop

No API calls.

---

## Step 2 — Live run (needs API key)

Copy `.env.example` to `.env`, paste your key, then:

```powershell
python exercise_3_retry_loop.py
```

**Expected:** a strong candidate often prints `attempt 1: valid` and a
final JSON payload with empty errors. If attempt 1 is inconsistent, you
should see it flagged and corrected on attempt 2.

---

## Reflection

1. Why send the error as `tool_result` with `is_error=True`, not a normal chat message?
2. Why append the assistant’s previous reply before the `tool_result`?
3. Why cap retries instead of looping until it is valid?
