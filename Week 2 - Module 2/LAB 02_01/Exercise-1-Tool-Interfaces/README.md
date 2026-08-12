# Exercise 1 — Tool Interfaces (S1)

Proves that tool-selection reliability is an **interface problem**, not a
model-size problem. The exact same model is run over a **weak** toolset
(vague names, overlapping descriptions, loose parameters) and a
**strong** toolset (object+action names, explicit when/when-NOT-to-use
descriptions, typed & constrained parameters) against the same six
support questions.

## Files

| File | Purpose |
|---|---|
| `exercise_1_tool_interfaces.py` | `WEAK_TOOLS`, `STRONG_TOOLS`, six `TEST_CASES`, and the scoring harness — run this. |

## Setup (one-time)

```powershell
cd "Exercise-1-Tool-Interfaces"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Then edit `.env` and replace `your-api-key-here` with your real Anthropic API key.

## Run

```powershell
python exercise_1_tool_interfaces.py
```

## What you'll see

The harness runs all six support questions against the **weak** toolset
first, then the **strong** toolset, forcing a tool call each time with
`tool_choice={"type": "any"}` (so we measure *which* tool gets picked,
not *whether* one gets picked). Each question prints `OK` or `MISS`,
followed by a score out of 6 for each toolset, and a summary comparing
the two.

Expect the weak toolset to misroute several questions (its vague names
`search` / `lookup` and overlapping description "search for stuff" give
the model nothing to disambiguate on), while the strong toolset should
route all six correctly — same model, same questions, only the interface
changed.

## Reflection

- If accuracy jumps from something like 3/6 (weak) to 6/6 (strong) using
  the *identical* model, that proves selection reliability comes from
  the **interface** (names, descriptions, schemas), not from model
  capability — "just use a bigger model" would not have fixed the weak
  toolset's ambiguity.
- The strong order tool's `"pattern": "^NP-[0-9]{6}$"` helps the model
  route correctly, but the Anthropic API does **not** enforce JSON
  Schema patterns server-side — it's descriptive metadata for the model,
  not validation. A malformed id like `100245` can still reach your tool
  function at call time, so your own code must validate and reject it
  (see Exercise 2's structured-error envelope for exactly this).
- Explicit negative contrast ("Do NOT use this... use the other tool
  instead") is more reliable than two good positive-only descriptions
  because it directly names the boundary between the two tools — without
  it, the model has to *infer* the boundary from two descriptions that
  might both sound plausible for an ambiguous question.
