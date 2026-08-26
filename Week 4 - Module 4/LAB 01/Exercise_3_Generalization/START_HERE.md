# Exercise 3 — Generalizing beyond the examples shown

You do **not** need to know Python. The principles block is already filled
in. Run the script on four edge cases the examples never showed.

**Time:** about 13 minutes  
**Open this folder** before you start  
(`Week 04/LAB 01/Exercise_3_Generalization`)

---

## What this is (in plain English)

Examples teach **format**. They cannot list every situation.

A short **principles** block teaches the **boundary**:

- Private person’s data = doxxing, even if they said “just a joke” → REMOVE
- Already-public / official info (company press number) → ALLOW
- Ambiguous joke-threats / disputes → REVIEW
- Rude, blunt, or boring is not a violation → ALLOW
- If unsure between REMOVE and REVIEW → REVIEW

The four test cases turn on context the examples never showed.

| Report (short) | Expected | Why |
|---|---|---|
| Company’s public press-office phone | allow | public/official is not doxxing |
| Private home address shared “as a joke” | remove | intent does not excuse doxxing |
| Friends joking “I’ll destroy you” about a match | review | playful / ambiguous |
| Long dull on-topic essay | allow | boring is not a violation |

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

## Step 1 — Look at principles vs examples

Open `exercise_3_generalization.py`.

- `EXAMPLES` — same three format examples as Exercise 2
- `PRINCIPLES` — the intent the examples cannot show

The scorer finds `ACTION |` even if the model adds a sentence first.
It does **not** blindly split on the first `|`.

---

## Step 2 — Run

```powershell
python exercise_3_generalization.py
```

**Expected:** all four cases route correctly (`4/4`).

---

## What good looks like

Public/official info is ALLOWED, doxxing-as-a-joke is REMOVED, the playful
threat goes to REVIEW — even though none of those appeared in the examples.

---

## Reflection (answer in your own words)

1. What does the principles block add that examples do not?
2. How do the principles get “public press number = allow” and “private address as a joke = remove” right?
3. Why extract the action with a regex on the `ACTION |` line instead of `split("|")[0]`?
