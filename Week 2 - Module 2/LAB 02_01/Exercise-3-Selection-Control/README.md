# Exercise 3 — Tool Distribution & Selection Control (S3)

Runs the same four support tickets through a triage step under three
different `tool_choice` settings — `auto`, `any`, and a **forced**
`classify_ticket` call — to show which one reliably produces exactly one
clean classification per ticket, every time.

## Files

| File | Purpose |
|---|---|
| `exercise_3_tool_choice.py` | `classify_ticket` + `draft_customer_reply` tools run under all 3 modes — run this. |

## Setup (one-time)

```powershell
cd "Exercise-3-Selection-Control"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Then edit `.env` and replace `your-api-key-here` with your real Anthropic API key.

## Run

```powershell
python exercise_3_tool_choice.py
```

## What you'll see

Three blocks, one per mode, each running the same 4 tickets:

- **`auto`** (`{"type": "auto"}`) — the model may answer in plain text,
  pick either tool, or pick no tool. Expect some tickets to come back
  with no classification at all.
- **`any`** (`{"type": "any"}`) — the model must call *some* tool, but
  it chooses which one — it may pick `draft_customer_reply` instead of
  `classify_ticket`.
- **`FORCED`** (`{"type": "tool", "name": "classify_ticket"}`) — the
  model must call exactly `classify_ticket`. Every ticket comes back
  with a clean classification.

The summary at the end tallies how many of the 4 tickets got a clean
`classify_ticket` call under each mode — only `FORCED` should score 4/4
every run.

## Reflection

- `auto`, `any`, and `FORCED` form a spectrum from least to most
  constrained. "Use the narrowest setting that still works" is the right
  default because over-constraining blocks legitimate model behavior —
  e.g. a turn that genuinely needed to ask a clarifying question instead
  of forcing a classification it isn't confident about.
- Under `any`, the model is required to call *some* tool but may pick
  `draft_customer_reply` instead of `classify_ticket`. For a triage
  step, "called the wrong tool" is arguably worse than "called no tool
  at all," because a wrong-tool result can look superficially valid to
  downstream code that isn't checking which tool actually fired — a
  routing pipeline that only checks "did a tool run?" would be silently
  fooled.
- Forcing `classify_ticket` guarantees the *shape* of the turn (you will
  get a `category` and a `reason`) but not the *correctness* of the
  category — a confident-but-wrong classification still passes through
  cleanly. That safety net belongs one step downstream: e.g. a
  validation/confidence-check stage that flags low-confidence or
  contradictory classifications for human review before they're acted on.
