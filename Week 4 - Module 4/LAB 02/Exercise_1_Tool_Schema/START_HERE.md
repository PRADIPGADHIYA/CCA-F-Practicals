# Exercise 1 — Force structured output with a tool schema

You do **not** need to know Python. The tool schema is already filled in.
Your job is to add an API key, run the script, and inspect the JSON.

**Time:** about 15 minutes  
**Open this folder** (`Week 04/LAB 02/Exercise_1_Tool_Schema`)

---

## What this is (in plain English)

A recruiter dashboard cannot sort a paragraph. Every candidate must become
this object:

```json
{"name": "...", "recommendation": "hire", "score": 7, "reason": "..."}
```

`recommendation` is only `strong_hire`, `hire`, or `no_hire`. `score` is
an integer from 0 to 10.

Asking Claude to “reply in JSON” is unreliable (markdown fences, missing
fields). This exercise defines the object as a **tool** named
`record_evaluation` and **forces** Claude to call it. The tool’s arguments
**are** the structured record — no parsing.

---

## Step 0 — Setup (Windows)

1. Copy `.env.example` to `.env` and paste your `ANTHROPIC_API_KEY`.
2. In a terminal **in this folder**:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

(A `.venv` may already be present.)

---

## Step 1 — Look at the schema

Open `exercise_1_tool_schema.py` and find `EVALUATE_TOOL`. All four fields
are required. The call uses:

`tool_choice = {"type": "tool", "name": "record_evaluation"}`

---

## Step 2 — Run

```powershell
python exercise_1_tool_schema.py
```

**Expected:** three JSON lines (Maya Chen, Tom Ruiz, Priya Nair). Each has
all four fields, score inside 0–10, no prose, no markdown fences.

---

## Reflection

1. Why is a tool schema + `tool_choice` more reliable than “reply in JSON”?
2. The enum lives in the schema; `strong_hire` must score ≥ 8 does not. Why?
3. What breaks if you drop `"required"`?
