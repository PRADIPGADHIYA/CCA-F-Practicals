# Exercise 3 — Multi-pass review (morning briefing)

You do **not** need to know Python. `critique()` and `refine()` are already
filled in. This exercise makes **three** real API calls: draft, critique, refine.

**Time:** about 15 minutes  
**Open this folder** (`Week 04/LAB 03/Exercise_3_Multipass`)

---

## What this is (in plain English)

A morning briefing must be balanced, specific, and short. One shot often
fails: too long, too positive, buries the bad news.

Three separate passes:

1. **DRAFT** — write the briefing
2. **CRITIQUE** — list problems only (do **not** rewrite)
3. **REFINED** — fix every bullet; output **only** the briefing

Standards: lead with the biggest item; balance good and bad news; use
numbers; stay neutral; no speculation; **under 120 words**.

If refined looks the same as draft, the critique was too vague.

---

## Step 0 — Setup

Copy `.env.example` to `.env` and paste your API key.

```powershell
.\.venv\Scripts\activate
python exercise_3_multipass.py
```

**Expected:** three labelled blocks — DRAFT, CRITIQUE (short bullets),
REFINED (tighter, balanced, ≤120 words).

---

## Reflection

1. Why two extra calls (critique, then refine) instead of one “review and rewrite”?
2. What goes wrong if critique is allowed to rewrite?
3. When would you use a different model just for the critique?
