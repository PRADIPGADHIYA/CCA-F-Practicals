# Exercise 2 — Few-shot examples to lock consistent output

You do **not** need to know Python. Three labeled examples are already in
the script. Run it and see how format compliance changes.

**Time:** about 12 minutes  
**Open this folder** before you start  
(`Week 04/LAB 01/Exercise_2_Few_Shot`)

---

## What this is (in plain English)

Downstream code needs this **exact** shape:

```text
REMOVE | Doxxing - exposes private personal data with no reasonable doubt.
```

Uppercase action, a space-pipe-space, then a short rationale.

Telling the model “use ACTION | rationale” is not enough. **Showing** three
examples (one REMOVE, one ALLOW, one REVIEW) locks casing, the separator,
and rationale length.

The script scores format with a strict check: the line must start with
`REMOVE |`, `REVIEW |`, or `ALLOW |`.

---

## Step 0 — One-time setup (Windows)

1. Copy `.env.example` to `.env` and paste your API key.
2. In a terminal **in this folder**:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

---

## Step 1 — Look at zero-shot vs few-shot

Open `exercise_2_few_shot.py`.

- `ZERO_SHOT` describes the format but does not show it.
- `FEW_SHOT_EXAMPLES` shows one example per label in the exact shape.

---

## Step 2 — Run and compare

```powershell
python exercise_2_few_shot.py
```

**Expected:**

- Zero-shot often gets the decision right but in the **wrong shape**
  (prose, missing pipe, lowercase action).
- Few-shot matches the strict format on **every** report (`4/4`).

---

## What good looks like

Few-shot output matches `ACTION | rationale` on every report, so a parser
can consume it. Zero-shot may decide correctly but in a shape that breaks
parsing — which is exactly what the examples fix.

---

## Reflection (answer in your own words)

1. The instruction already says “respond as ACTION | rationale.” Why do examples lock the format better?
2. How many examples should you use, and what should they cover?
3. Why score format separately from whether the decision is correct?
