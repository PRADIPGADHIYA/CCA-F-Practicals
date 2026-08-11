# Exercise 4 — Programmatic Step Enforcement (S4)

Adds hard programmatic **gates** between every pipeline step. A gate
checks a precondition in Python code — if it's not met, the pipeline
raises a named `PipelineGateError` and stops immediately, instead of
silently continuing with incomplete data (which a prompt instruction
alone cannot reliably prevent).

## Files

| File | Purpose |
|---|---|
| `gates.py` | `PipelineGateError` + the three gate functions. |
| `context.py` | `TicketContext` dataclass (carried forward from Exercise 3). |
| `subagents.py` | The four subagents (carried forward from Exercise 2/3). |
| `coordinator_v3.py` | Full pipeline with all three gates wired in — run this first. |
| `coordinator_v3_sabotage.py` | Deliberately breaks Gate 1 to prove it actually blocks execution. |

## Setup (one-time)

1. Open a terminal in this folder (`Exercise-4-Step-Enforcement`).
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

## Run — clean pipeline

```powershell
python coordinator_v3.py
```

You should see `Gate 1 passed`, `Gate 2 passed`, and `Gate 3 passed`
printed between the pipeline steps, followed by the final validated
output.

## Run — prove the gate blocks

```powershell
python coordinator_v3_sabotage.py
```

Expect to see:

- `PipelineGateError` raised immediately at Gate 1 — not later in the
  pipeline.
- The error message explicitly names `severity` as the missing field.
- Steps 2, 3, and 4 never run (no CRM/Drafter/Validator output appears).
- The message is printed with a clear `[PIPELINE BLOCKED]` label.

`coordinator_v3.py` itself is untouched and will still run cleanly.

## Reflection

- A named exception with a specific message (`PipelineGateError:
  "missing field(s): severity"`) is far more actionable during an
  incident than a bare `assert` — it tells you exactly what broke and
  what to rerun, without reading a stack trace to figure it out.
- Whether a gate failure should auto-retry or immediately alert a human
  depends on the failure's likely cause: a transient API hiccup might be
  safe to retry once, but a systematic data problem (e.g. CRM lookup
  consistently failing) should alert a human rather than retry blindly
  forever.
- `gate_enrichment` currently fails if *either* `account_tier` or
  `sla_tier` is missing. Consider whether partial CRM data (tier present,
  SLA missing) should behave differently — you could split it into two
  more specific error messages, or decide a partial result is acceptable
  for a lower-severity ticket.
