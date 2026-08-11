# Exercise 1 — PostToolUse Hooks & Interception (S5)

Builds a **hook chain** (log / validate / block) that sits between the
model's decision to call a tool and the tool's real side-effect. If any
hook blocks a call, the real action never happens — the model only sees
a `"BLOCKED by policy: ..."` string.

## Files

| File | Purpose |
|---|---|
| `tool_hooks.py` | The hook engine itself — pure Python, **no API key needed**. Run this first. |
| `agent_with_hooks.py` | A live agentic loop (like Lab 1.1) with the hooks wired into every tool call. |

## Setup (one-time)

1. Open a terminal in this folder (`Exercise-1-Hooks-Interception`).
2. Create and activate a virtual environment:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and add your real Anthropic API key
   (only needed for `agent_with_hooks.py` — Step 1 below needs no key at all):

   ```powershell
   Copy-Item .env.example .env
   ```

## Step 1 — Run the hook engine (no API key needed)

```powershell
python tool_hooks.py
```

You should see, in order:
- An **ALLOWED** quarantine of the suspicious analyst laptop.
- A **[BLOCK]** line for quarantining `trading-prod-01` (protected asset).
- A **[BLOCK]** line for a malformed IP passed to `block_ip`.
- A **[BLOCK]** line for an empty username passed to `disable_user`.
- A **[BLOCK]** line for disabling the `ceo` account (executive dual-approval rule).
- An **ALLOWED** SIEM query.
- A full numbered **audit log** at the end recording every attempt.

## Step 2 — Run the live agent with hooks wired in

```powershell
python agent_with_hooks.py
```

This sends the agent a task containing a deliberate **trap**: quarantine
the analyst laptop (should succeed), block the suspicious IP (should
succeed), and — "as a precaution" — also quarantine `trading-prod-01`
(must be blocked).

Verify:
- The hook prints a `[BLOCK]` line for `trading-prod-01`.
- The agent receives the `BLOCKED by policy: ...` result and does **not**
  retry that action.
- The agent's final incident summary names which actions succeeded and
  which were blocked.
- The audit log at the end records all attempts, allowed and blocked.

> Note: `agent_with_hooks.py` uses `claude-haiku-4-5-20251001` (fast and
> cost-efficient). If you want the strongest reasoning for multi-step
> tool-routing decisions instead, open the file and change `MODEL` to
> `"claude-opus-4-6"` or another model you have access to.

## Reflection

- **Why is hook-level enforcement strictly safer than a prompt rule** like
  "never quarantine trading-prod-*"? Because the hook is deterministic
  Python that runs *before* the tool executes, regardless of what the
  model decides — a prompt rule is just a suggestion the model can
  ignore under pressure, ambiguity, or a cleverly-worded request.
- If `arg_validation_hook` raised an exception instead of returning
  `False`, the loop would crash before `run_tool` ever got to append a
  BLOCKED entry to the audit log — you'd lose the audit trail for
  exactly the malformed calls you most need to record.
- `protected_asset_hook` checks substrings (`if protected in hostname`).
  A hostname like `not-trading-prod-01-really` would incorrectly match,
  and a hostname like `TRADING-PROD-01` (different case) would NOT match
  in a case-sensitive substring check. Tightening it means exact,
  case-normalized matching against a known asset list — not substring
  matching.
