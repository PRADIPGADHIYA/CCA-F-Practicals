# Exercise 1 — The Agentic Loop (S1)

Builds a loop that keeps calling Claude and the `classify_ticket` tool
until the ticket is **fully** classified (`product_area`, `severity`,
`intent`) — driven entirely by the API's `stop_reason`, not by a fixed
number of iterations.

## Files

| File | Purpose |
|---|---|
| `tools.py` | The simulated `classify_ticket` tool Claude can call. |
| `loop.py` | The agentic loop itself — run this one. |

## Setup (one-time)

1. Open a terminal in this folder (`Exercise-1-Agentic-Loop`).
2. Create a virtual environment and activate it:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and paste in your real Anthropic API key:

   ```powershell
   Copy-Item .env.example .env
   ```

   Then edit `.env` and replace `your-api-key-here` with your key.

## Run

```powershell
python loop.py
```

## What to look for

- `stop_reason` is printed on every iteration.
- You'll see `-> Calling tool ...` / `<- Tool result: ...` lines between
  iterations whenever Claude decides to call the tool.
- The loop only stops once `stop_reason` is `"end_turn"` — i.e. once
  Claude has confirmed all three fields.

## Try the reflection experiments from the lab

- **How many tool calls happen?** Run it a few times and compare — this
  can vary because the model decides for itself how many calls it needs.
- **Break the ordering:** In `loop.py`, move the
  `messages.append({"role": "assistant", ...})` line to *after* the
  `if/elif` branches instead of right after the API call, and re-run.
  Watch it error out — this proves why the assistant turn must be
  appended first.
- **Replace `while True` with `for i in range(2):`** and re-run. Notice
  the loop can now cut off before all three fields are confirmed,
  proving why iteration counts are not a safe loop-exit strategy.
