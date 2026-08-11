# Exercise 3 — Explicit Context Passing (S3)

Introduces a typed `TicketContext` dataclass that carries all pipeline
state, replacing the loose variables passed around in Exercise 2. Missing
required fields fail loudly at construction time (`TypeError`) instead of
silently producing a wrong Claude answer downstream.

## Files

| File | Purpose |
|---|---|
| `context.py` | The `TicketContext` dataclass + completion-check helpers. |
| `subagents.py` | Same four subagents from Exercise 2 (carried forward). |
| `coordinator_v2.py` | Coordinator refactored to read/write `ctx` fields — run this one. |

## Setup (one-time)

1. Open a terminal in this folder (`Exercise-3-Context-Passing`).
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
python coordinator_v2.py
```

You'll see the same four pipeline steps as Exercise 2, plus a final
printout of the fully-populated `TicketContext`.

You can also run `context.py` directly to see the `TypeError` that fires
when required fields are missing:

```powershell
python context.py
```

## Reflection

- A missing key in a plain `dict` is only discovered the moment code
  tries to read that key — which could be several steps and API calls
  later. A dataclass's `TypeError` fires immediately at construction,
  which is much safer for a pipeline running unattended overnight.
- The `classification_complete()`, `enrichment_complete()`, and
  `draft_complete()` helper methods return `bool` — Exercise 4 turns
  these into hard programmatic **gates** that block a step from running
  until the previous one has actually finished.
