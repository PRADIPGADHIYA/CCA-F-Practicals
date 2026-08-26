# Exercise 1 — Explicit criteria to cut false positives

You do **not** need to know Python. The prompt is already filled in from the
lab PDF. Your job is to run the script and read the before/after scores.

**Time:** about 15 minutes  
**Open this folder** before you start  
(`Week 04/LAB 01/Exercise_1_Explicit_Criteria`)

---

## What this is (in plain English)

A community platform must route reported posts to one of three actions:

| Action | Meaning |
|---|---|
| **remove** | Take it down now (doxxing, credible threat, clearly illegal) |
| **review** | Send to a human (spam, borderline, ambiguous) |
| **allow** | Rude or off-topic, but not a violation |

A vague prompt over-uses **remove** and wrongfully takes down good posts.
This exercise gives each label a testable definition, plus: *if unsure
between remove and review, choose review*.

---

## Step 0 — One-time setup (Windows)

1. Copy `.env.example` to `.env`.
2. Paste your Anthropic API key into `.env` (replace `your_key_here`).
3. In a terminal **in this folder**:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

---

## Step 1 — Look at the two prompts

Open `exercise_1_explicit_criteria.py`.

- `VAGUE_PROMPT` only lists remove / review / allow.
- `EXPLICIT_PROMPT` defines each action and includes the tie-break.

You do not need to change the file.

---

## Step 2 — Run and compare

```powershell
python exercise_1_explicit_criteria.py
```

**Expected:** the explicit prompt raises accuracy and drives wrongful
“remove” calls toward **zero** (for example, a couple of false removes
under the vague prompt, then none).

Look at two numbers at the bottom of each block:

- **accuracy** — how many of 8 reports were labeled correctly
- **wrongful 'remove' calls** — the costly failure this lab cares about

---

## What good looks like

On the same model, the explicit prompt scores higher accuracy and — more
importantly — drops wrongful “remove” calls toward zero, because REMOVE
now has a testable definition and ambiguous cases go to REVIEW.

---

## Reflection (answer in your own words)

1. Why does a vague “remove / review / allow” prompt over-fire remove?
2. Why bake in “if unsure, choose review”? What cost does that protect?
3. Why track wrongful removes separately from overall accuracy?
