# Exercise 1 — Add a feature with a test-driven loop

You do **not** need to know Python. You will ask Claude to write a failing
test first, watch it fail, then implement just enough to make it pass.

**Time:** about 15 minutes  
**Open this folder in Cursor / VS Code** before you start  
(`LAB 03/Exercise_1_TDD_Loop`)

No API key is needed for this exercise.

---

## What this project is (in plain English)

NorthPeak decides how much money to refund a customer.

| Rule today | Meaning |
|---|---|
| Returned within 30 days | Full refund |
| Returned after 30 days | $0 |
| Negative price or days | Error |

**New rule to add:** if the item was **opened**, take a **15% restocking fee**
(refund 85% of the price) — but only inside the 30-day window. Outside the
window the refund is still $0.

---

## Step 0 — Confirm the environment (already done)

```powershell
.\.venv\Scripts\activate
pytest -q
```

You should see **`6 passed`**. Start Claude Code from this folder.

---

## Step 1 — Write the failing test first

Ask Claude. Do **not** let it change `refunds.py` yet:

```text
Write failing tests for a new rule: refund_amount should take an `opened`
flag; opened items within the window get 85% of the price (15% restocking
fee), and outside the window the refund is still 0. Don’t change refunds.py yet —
just add the tests and run them so we see them fail.
```

**Expected:** two new tests

- `test_opened_item_restocking_fee` — `refund_amount(100.0, 10, opened=True) == 85.0`
- `test_opened_item_outside_window_still_zero` — `refund_amount(100.0, 45, opened=True) == 0.0`

---

## Step 2 — Confirm it fails (red)

```powershell
pytest -q
```

**Expected:** **`2 failed, 6 passed`**. The new tests fail because
`refund_amount` does not accept `opened` yet. That proves the tests actually
check the new behaviour.

---

## Step 3 — Make it pass (green)

Ask:

```text
Now implement the `opened` parameter in refund_amount so all tests pass.
```

Claude should add `opened: bool = False` and a 15% restocking fee. Defaulting
to `False` keeps every existing call and the original 6 tests working.

**Hard rule from CLAUDE.md:** never weaken or delete a test to go green —
fix the code.

---

## Step 4 — Confirm green

```powershell
pytest -q
```

**Expected:** **`8 passed`**.

---

## What good looks like

- Two new tests were added and failed first (red)
- Then the implementation made the whole suite pass (green)
- The original 6 tests never changed
- `opened=False` by default keeps old callers working

---

## Reflection (answer in your own words)

1. Why write the failing test first? What does watching it fail (red) prove?
2. Why does `opened` default to `False`? Why does that matter for existing tests?
3. Why is “never weaken or delete a test to go green” essential to this loop?
