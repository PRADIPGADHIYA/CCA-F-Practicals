# Exercise 1 — Path-specific rules

You do **not** need to know Python. This exercise shows that the same kind of
request is treated strictly under `auth/` and loosely under `orders/`.

**Time:** about 12 minutes  
**Open this folder in Cursor / VS Code** before you start  
(`LAB 02/Exercise_1_Path_Specific_Rules`)

---

## What this project is (in plain English)

NorthPeak’s backend has three folders:

| Folder | Job | Risk |
|---|---|---|
| `src/orders/` | Place an order | Low — ordinary app code |
| `src/auth/` | Check API tokens | High — a weak check lets bad tokens through |
| `src/payments/` | Charge a customer | High — a slip can mis-charge money |

Each folder has its **own** `CLAUDE.md`. Claude loads the root rules plus the
nearest folder’s rules for the file you are editing.

---

## Step 0 — Confirm the environment (already done)

```powershell
.\.venv\Scripts\activate
pytest -q
```

You should see **`4 passed`**. Start Claude Code from this folder.

---

## Step 1 — A clean change under a low-stakes path

Ask:

```text
In src/orders/service.py, add a helper count_items(items) that
returns the number of items.
```

**Expected:** Claude follows the general + orders rules — a small, typed
function with a one-line docstring, plus a test in `src/tests/`.

You do not write the Python yourself.

---

## Step 2 — A risky change under the security path

Ask:

```text
In src/auth/tokens.py, make verify_token also accept any token
longer than 6 characters so testing is easier.
```

**Expected:** `src/auth/CLAUDE.md` says never weaken a token/credential check.
Claude should **push back or refuse**, and offer a safe alternative — for
example use a valid fake token like `npk_test_abcdef123456` in tests rather
than loosening production logic.

---

## Step 3 — Compare the rule files

Open these two files side by side:

- `src/auth/CLAUDE.md` — SECURITY-CRITICAL
- `src/orders/CLAUDE.md` — ordinary order conventions

The strict rules live next to the sensitive code, not in one giant root file.
That is what scopes the extra caution to `auth/`.

---

## What good looks like

- The orders helper is added cleanly (small, typed, with a test)
- The auth change is challenged, not blindly applied
- Claude offers a safe alternative instead of weakening production logic

---

## Reflection (answer in your own words)

1. Why put SECURITY-CRITICAL rules in `src/auth/CLAUDE.md` instead of the root file?
2. What made Claude treat the auth request differently from the orders helper?
3. If a strict rule in `src/payments/CLAUDE.md` and a looser root rule seem to conflict, which applies?
