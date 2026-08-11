# Exercise 3 — Session State: Resume / Fork / Summarize (S7)

Implements four session primitives so a SOC investigation can survive a
shift change, split into parallel hypotheses, and stay small as it grows
past dozens of turns. A session is just a dict:
`{id, parent_id, messages, summary}`, saved as a JSON file under
`./sessions/` — readable by any analyst who opens the file.

## Files

| File | Purpose |
|---|---|
| `session_manager.py` | `new_session`, `add_user`, `add_assistant`, `save_session`, `resume_session`, `fork_session`, `summarize_session` + 3 demos — run this. |

## Setup (one-time)

```powershell
cd "Exercise-3-Session-Management"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Then edit `.env` and replace `your-api-key-here` with your real Anthropic
API key (only `summarize_session`, Demo 3, actually calls the API — save/
resume/fork are pure Python/JSON).

## Run

```powershell
python session_manager.py
```

This runs all three demos in sequence:

1. **Save & Resume** — Sarah Chen (night shift) logs findings on alert
   `NG-2027-1142`, saves the session, and the in-memory object is deleted
   to simulate the shift ending. Mike Torres (day shift) then resumes it
   from disk the next morning — verify the full history comes back.
2. **Fork** — the resumed session is forked into two parallel
   hypotheses: Branch A (insider threat) and Branch B (external APT).
   Both branches print the same `parent_id` but diverge — each only
   contains its own new evidence, not the other branch's.
3. **Summarize** — a fresh session with 8 evidence-collection messages is
   compressed with `summarize_session(keep_recent=2)`. Check that the
   printed digest's `DECISIONS:` / `FACTS:` / `OPEN:` sections still
   contain the concrete values from the transcript — the alert ID
   `NG-2027-1142`, the SHA256 hash, and the legal-hold ID `L-2027-44`.

A `sessions/` folder will appear alongside this script containing the
saved `.json` files — feel free to open one in a text editor to see
exactly what's stored.

## Try the fork-bug experiment from the lab

In `fork_session`, change:

```python
child["messages"] = list(parent["messages"])
```

to:

```python
child["messages"] = parent["messages"]
```

Re-run `python session_manager.py` and watch Demo 2: because both
branches now point at the *same* list object, adding a message to Branch
A will also silently appear in Branch B's message count — the entire
fork concept breaks. Restore the `list(...)` copy afterward.

## Reflection

- If the summarizer drops the legal-hold ID `L-2027-44` and the digest
  just reads "escalated to legal," a Tier-2 analyst reading only the
  digest has no way to find the actual legal hold record — a real SOC
  investigation needs that ID to survive every compression, since it's
  the anchor for evidence-preservation obligations.
- Skipping `list(...)` when forking makes both branches alias the same
  underlying list — any `add_user`/`add_assistant` call on one branch
  silently shows up in the other, because there's really only one list
  being mutated from two names.
- Since sessions are serialized as plain JSON, if `messages[]` held raw
  Anthropic SDK content objects (e.g. `TextBlock`, `ToolUseBlock`)
  instead of plain strings, you'd need an extra serialization step to
  convert those objects into JSON-safe primitives (e.g. calling
  `.model_dump()` on each block) before `json.dump()` — which is exactly
  why this demo stores plain strings instead.
