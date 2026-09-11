# Exercise 2 — Parallel processing (breaking-news burst)

You do **not** need to know Python. `run_parallel()` is already implemented.
This exercise makes **real API calls** (sequential, then parallel).

**Time:** about 15 minutes  
**Open this folder** (`Week 04/LAB 03/Exercise_2_Parallel`)

---

## What this is (in plain English)

When a story breaks, waiting overnight is too slow. Classifying eight
headlines **one after another** waits for eight round trips. A **thread
pool** starts several at once so the waiting overlaps.

Most of the time is spent waiting on the network (I/O-bound), so threads
are the right tool. Too many workers hit **429** rate-limit errors. This
lab uses **5** workers.

`.map` keeps results in the **same order** as the headlines.

---

## Step 0 — Setup

Copy `.env.example` to `.env` and paste your API key.

```powershell
.\.venv\Scripts\activate
python exercise_2_parallel.py
```

**Expected:** parallel finishes about **3–5×** faster than sequential on
this size. Exact speedup depends on latency and your rate limits.

---

## Reflection

1. Why threads (not processes or async) for this workload?
2. What stops speedup from growing forever as you add workers?
3. How would you pick `workers` in production?
