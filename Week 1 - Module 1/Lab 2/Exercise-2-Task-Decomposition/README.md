# Exercise 2 — Fixed vs Adaptive Decomposition (S6)

Builds **both** decomposition styles in one file:

- **Fixed**: `run_fixed_intel_digest` — three hard-coded steps, run in
  the same order every time (extract IoCs → match assets → exec brief).
  Use this when the task's shape is certain.
- **Adaptive**: `run_adaptive_triage` — classifies the alert first, then
  routes to one of six specialist playbooks. Use this when the input
  determines the path.

## Files

| File | Purpose |
|---|---|
| `decompose.py` | Both decomposition styles + a shared `ask_claude` helper — run this. |

## Setup (one-time)

```powershell
cd "Exercise-2-Task-Decomposition"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Then edit `.env` and replace `your-api-key-here` with your real Anthropic API key.

## Run

```powershell
python decompose.py
```

## What you'll see

1. **Fixed digest**: the three steps run in order over a simulated
   overnight threat-intel feed — IoCs extracted, matched against
   NorthGate's asset inventory, then compressed into a 3-bullet
   executive brief.
2. **Adaptive triage**: three different alerts (the live test alert
   `NG-2027-1142` — a data-exfiltration case, a phishing report, and a
   brute-force password spray) are each classified and routed to the
   matching specialist playbook. Verify each one lands in the correct
   branch (`data_exfiltration`, `phishing`, `brute_force` respectively).

## Reflection

- Replacing the fixed digest with adaptive routing would cost an extra
  classification call per step and add latency + a new failure mode
  (misclassification) — worth it only when the next step genuinely
  isn't knowable in advance.
- If the classifier silently mislabels a real data-exfiltration event as
  `false_positive`, the case gets closed instead of escalated — a
  serious miss. You'd detect this by periodically auditing a sample of
  `false_positive` closures against ground truth, or by adding a
  low-confidence-score threshold that routes uncertain cases to a human.
- The morning digest could be made partially adaptive: keep steps 1 and
  3 fixed, but make step 2 branch on what step 1 finds (e.g. "if any IoC
  matches a production asset, run an urgent match-analysis prompt;
  otherwise run the routine one").
