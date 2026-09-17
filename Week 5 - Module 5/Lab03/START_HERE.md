# Lab 5.3 — Trust & Traceability: Human Review, Confidence & Provenance

You do **not** need to know Python. The three lab TODOs are already filled
in. Your job is to run the reviewer and read the three buckets.

**Time:** about 40 minutes  
**Open this folder** before you start (`Week 05/Lab03`)

---

## What this is (in plain English)

You are reviewing a short **quarterly financial report** (AcmeCorp, Q2 FY26).
An AI flags possible compliance issues. In a regulated shop that is not
enough — a finding must be:

1. **Scored** — high confidence can auto-clear; low confidence goes to a human
2. **Cited** — the exact report line is attached from our data, not copied
   by the model
3. **Cross-checked** — two independent prompts; if they disagree, a human
   sees it as **contested**

Seeded issues you should expect the model to notice (live run may vary):

| Line | Text (short) | Why it is interesting |
|---|---|---|
| 4 | APAC revenue rose 200% with no explanation | unusual change, no disclosure |
| 7 | Forward-looking statements include uncertain outcomes | vague risk language |
| 9 | Material related-party transactions not detailed | missing disclosure |

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

## Step 1 — Prove the logic without spending API calls

```powershell
python main.py --check
```

**Expected:**

- Lines 4 and 9 keep real quotes from the report; **line 99 is dropped**
- **AUTO-CLEAR:** line 4 (avg confidence 0.91 ≥ 0.75)
- **HUMAN REVIEW:** line 7 (avg confidence 0.53 < 0.75)
- **CONTESTED:** line 9 (only pass A flagged it)
- Ends with `Offline check passed`

You do not need to change any file.

---

## Step 2 — Run the live reviewer

```powershell
python main.py
```

The script prints the numbered report, runs **pass A (strict)** then
**pass B (general)**, and prints three buckets:

- **AUTO-CLEAR** — both passes agreed, confidence ≥ 0.75
- **HUMAN REVIEW** — both agreed, but confidence is below 0.75
- **CONTESTED** — only one pass flagged that line

Exact flags can differ between runs. What must stay true: every printed
finding includes a **real source line and quote**.

---

## Files (you can open them, you do not need to edit them)

| File | What it does |
|---|---|
| `confidence.py` | Splits findings into auto_clear / human_review / contested |
| `reviewer.py` | Calls Claude, parses JSON, attaches quotes from the report |
| `main.py` | Runs two passes and prints the buckets |
| `sample_report.py` | Ten fake report lines + line-number lookup |

---

## What good looks like

- A finding always shows `line N` plus the **exact report sentence**.
- A made-up line number never appears (it is dropped).
- Agreement + high confidence → auto-clear; disagreement → contested.

---

## Reflection (answer in your own words)

1. Why send **low-confidence** findings to a human instead of auto-clearing
   everything?
2. Why attach the quote from **our report file** instead of letting the
   model copy the sentence?
3. Why is a line that only **one pass** flagged treated as contested, not
   as a confirmed issue?
