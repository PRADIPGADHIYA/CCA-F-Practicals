# Exercise 2 — Coordinator & Subagents (S2)

Builds a coordinator that calls four independent specialist subagents in
sequence: **Classifier → CRM Enricher → Drafter → Validator**. Each
subagent makes exactly one Claude API call and has no memory of the
others — the coordinator explicitly passes each subagent only what it
needs.

## Files

| File | Purpose |
|---|---|
| `subagents.py` | The four subagent functions (Classifier, Enricher, Drafter, Validator). |
| `coordinator.py` | Calls the subagents in order — run this one. |

## Setup (one-time)

1. Open a terminal in this folder (`Exercise-2-Coordinator-Subagents`).
2. Create and activate a virtual environment:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and add your real API key:

   ```powershell
   Copy-Item .env.example .env
   ```

## Run

```powershell
python coordinator.py
```

You should see four labelled sections print in order, each showing the
output of that subagent.

## Try the Memory Isolation Experiment from the lab

1. Open `subagents.py` and temporarily change `run_drafter` so it ignores
   `classification` and `crm` (e.g. don't include them in the `context`
   string passed to Claude) — simulating a drafter that only sees the raw
   ticket text.
2. Re-run `python coordinator.py` and compare the draft output. Notice it
   may guess the wrong product area or omit the SLA tier — this is
   exactly the failure mode explicit context passing (Exercise 3) is
   designed to prevent.
3. Restore `run_drafter` to its original form before moving on to
   Exercise 3.

## Reflection

- The Validator never calls a tool, so it will always return
  `stop_reason == "end_turn"` — its caller code in the coordinator never
  needs to handle a tool-use branch.
- Passing the *entire* Exercise 1 messages list to each subagent instead
  of a structured dict would cost far more tokens and could leak
  irrelevant context that confuses the subagent.
