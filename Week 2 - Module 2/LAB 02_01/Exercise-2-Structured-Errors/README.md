# Exercise 2 — Structured Errors & Retries (S2)

Wraps a deliberately flaky "Orders" backend so it **always** returns a
structured `isError` / `isRetryable` envelope instead of raising an
exception — then builds a retry loop that backs off on transient
failures (timeout, 503) and stops immediately on permanent ones (404, 400).

## Files

| File | Purpose |
|---|---|
| `exercise_2_structured_errors.py` | Mock service, `call_order_tool`, `run_with_retry`, live agent loop — run this. |

## Setup (one-time)

```powershell
cd "Exercise-2-Structured-Errors"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Then edit `.env` and replace `your-api-key-here` with your real Anthropic API key
(only needed for the live demo below — the offline check needs no key at all).

## Step 1 — Offline self-check (no API key needed)

```powershell
python exercise_2_structured_errors.py --check
```

Proves the envelope logic in isolation:
1. A good id (`NP-100245`) that times out once (504) succeeds after one retry.
2. A 404 (`NP-999999`) comes back non-retryable.
3. A malformed id (`100245`, missing the `NP-` prefix) comes back as a
   non-retryable 400.
4. A queued 503 (`NP-100311`) comes back retryable.

## Step 2 — Live agent over three failure shapes

```powershell
python exercise_2_structured_errors.py
```

Runs three support tickets through a minimal agentic loop:
- **Case A** — `NP-100245` times out once (504); the loop waits and
  retries; the second attempt succeeds and the agent answers normally.
- **Case B** — `NP-999999` returns 404; no retry; the agent tells the
  customer the order wasn't found.
- **Case C** — `100245` is malformed (400); no retry; the agent asks for
  a correctly formatted id.

Watch the printed `Structured result: {...}` lines for each case — the
model only ever sees clean `tool_result` data with `is_error` set, never
a Python traceback.

## Reflection

- If a tool raised a Python exception mid-loop instead of returning
  data, the whole agentic loop would crash before the model ever got a
  turn to respond — there is no `tool_result` for the model to reason
  about, so it can't "recover" the way it recovers from an error marked
  `is_error: true`. The conversation just ends abnormally.
- Dropping the attempt cap on `run_with_retry` risks retrying forever
  against a genuinely down service — the loop (and the customer) hangs
  indefinitely. Dropping the exponential backoff but keeping the cap
  means you hammer a struggling service with rapid-fire retries, which
  can make an already-degraded backend worse.
- 404 ("not found") and 400 ("malformed id") are both non-retryable but
  mean very different things to a customer. The structured error already
  carries a `status` code and a human-readable `error` message — the
  agent's system prompt tells it to phrase the two differently (report
  "not found" vs. ask the customer to resend a correctly formatted id),
  which only works because the envelope gives the model enough
  information to tell the two cases apart.
