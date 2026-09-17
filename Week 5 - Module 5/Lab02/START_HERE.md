# Lab 5.2 — Resilient Systems: Error Propagation & Crash Recovery

You do **not** need to know Python. The three lab TODOs are already filled
in. Your job is to run the pipeline and read what it prints.

**Time:** about 40 minutes  
**Open this folder** before you start (`Week 05/Lab02`)

---

## What this is (in plain English)

You are running a **healthcare claims** batch. Each claim walks through
three specialist steps:

1. **Intake** — Claude turns the free-text narrative into structured fields
2. **Validation** — Python checks “is the member active?” and “is the
   procedure covered?”
3. **Adjudication** — Python decides approve / hold / deny by amount

There are three sample claims. One is **deliberately broken**:

| Claim | Member | Amount | What should happen |
|---|---|---|---|
| CLM-001 | active | 120 | all three stages pass → **done** |
| CLM-002 | **inactive** | 850 | validation fails → **failed** (`member_not_active`) |
| CLM-003 | active | 95 | all three stages pass → **done** |

If a stage crashed the whole program, you would lose the other claims.
This lab makes failures a normal return value, writes every finding to
disk immediately, and skips finished claims when you run it again.

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

- CLM-001 and CLM-003 validation ok, decision **approved**
- CLM-002 validation FAIL (`member_not_active`), adjudication skipped
- First pass: `done: 2` `failed: 1`
- Simulated restart skips all three
- Ends with `Offline check passed`

You do not need to change any file.

---

## Step 2 — Run the live pipeline

```powershell
python main.py
```

**Expected first run:** `SUMMARY  done: 2   failed: 1   skipped: 0`

Then run it **again** (do not delete `scratchpad.json`):

```powershell
python main.py
```

**Expected second run:** all three lines say `(already done|failed, skipping)`
and `skipped: 3`. That is crash recovery.

To start over, delete `scratchpad.json` by hand and run again. The lab
never deletes that file for you.

---

## Files (you can open them, you do not need to edit them)

| File | What it does |
|---|---|
| `agents.py` | Three subagents; each returns `StageResult` |
| `scratchpad.py` | Writes `scratchpad.json` after every change |
| `main.py` | Walks stages, logs, skips finished claims |
| `sample_claims.py` | Three fake claims (CLM-002 is inactive) |

---

## What good looks like

- CLM-002 fails at **validation** with `member_not_active` — the pipeline
  does **not** crash.
- `scratchpad.json` has findings for every stage that ran.
- A second run skips finished claims instead of processing them again.

---

## Reflection (answer in your own words)

1. Why should a subagent **return** `StageResult(ok=False)` instead of
   raising an exception into the coordinator?
2. Why flush `scratchpad.json` **after every mutation**, not at the end
   of the batch?
3. Why skip **both** `done` and `failed` on restart, instead of auto-
   retrying failures?
