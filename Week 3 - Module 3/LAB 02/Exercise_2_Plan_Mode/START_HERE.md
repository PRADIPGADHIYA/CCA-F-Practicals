# Exercise 2 — Plan mode for a multi-file migration

You do **not** need to know Python. This exercise is about approving a plan
**before** any file is edited.

**Time:** about 15 minutes  
**Open this folder in Cursor / VS Code** before you start  
(`LAB 02/Exercise_2_Plan_Mode`)

---

## The problem (in plain English)

`verify_token` is the **strict** check (token must start with `npk_` and be
at least 12 characters).

`verify_token_v1` is the **old, weak** check (any 6+ character string). Two
modules still use it:

- `src/orders/service.py`
- `src/payments/charges.py`

You will migrate every caller to the strict check, then delete the old function.

Because this touches several files, you use **Plan mode** first.

---

## Step 0 — Confirm the environment (already done)

```powershell
.\.venv\Scripts\activate
pytest -q
```

You should see **`4 passed`**. Start Claude Code from this folder.

---

## Step 1 — Enter Plan mode

In Claude Code, press **Shift+Tab** until the mode is **Plan**, or start with:

```text
claude --permission-mode plan
```

Claude should propose a plan and **wait** for your approval before editing.

If you are in Cursor chat instead, say “show the plan and wait for my approval
before editing any file.”

---

## Step 2 — Ask for the migration, planned first

```text
Migrate every caller of verify_token_v1 to verify_token across the
repo, keeping behaviour correct. Plan it first.
```

---

## Step 3 — Review and approve the plan

A good plan includes all of these:

1. Grep `verify_token_v1` to find call sites: `src/orders/service.py` and
   `src/payments/charges.py` (plus the definition in `src/auth/tokens.py`).
2. In each consumer, change the import and the call to `verify_token`.
3. Once no caller remains, remove the dead `verify_token_v1` from
   `src/auth/tokens.py`.
4. Run `pytest -q` to confirm nothing broke.

Approve the plan, then let Claude execute.

Both consumers should end up like this:

```python
from auth.tokens import verify_token
```

---

## Step 4 — Verify the suite is still green

```powershell
pytest -q
```

**Expected:** **`4 passed`**. (This folder starts at 4 tests. The migration
adds none. The smoke tests already use `npk_live_abcdef123456`, which passes
the stricter `verify_token`.)

---

## What good looks like

- A clear plan is shown and approved **before** any edit
- The two imports/calls change to `verify_token`
- The unused `verify_token_v1` is removed
- Tests stay green
- The plan lists “run the tests” as a final, non-optional step

---

## Reflection (answer in your own words)

1. Why is Plan mode worth the extra step for a multi-file migration?
2. Why bake “run the tests” into the plan rather than assume it?
3. Why is removing the dead function part of finishing the migration, not optional cleanup?
