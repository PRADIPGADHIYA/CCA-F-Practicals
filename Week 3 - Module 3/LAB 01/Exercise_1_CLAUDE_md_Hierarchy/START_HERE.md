# Exercise 1 — CLAUDE.md hierarchy and @import

You do **not** need to know Python. This exercise is about how Claude Code
reads team rules from files.

**Time:** about 12 minutes  
**Open this folder in Cursor / VS Code** before you start  
(`LAB 01/Exercise_1_CLAUDE_md_Hierarchy`)

---

## What this project is (in plain English)

NorthPeak Outfitters has a tiny pricing calculator:

| Function | What it does |
|---|---|
| `apply_member_discount` | Members get 10% off |
| `shipping_cost` | Shipping is $7.95, or free at $75+ |
| `order_total` | Discount first, then add shipping |

You will not write this code yourself. You will ask Claude to follow the
project's rules.

---

## Step 0 — Confirm the environment (already done)

A Python environment and a git baseline are already set up in this folder.
In a terminal here, you can confirm the 4 tests are green:

```powershell
.\.venv\Scripts\activate
pytest -q
```

You should see **`4 passed`**. Then start Claude Code from this folder
(Claude Code panel, or the `claude` command).

---

## Step 1 — Read the memory files

Open these three files and notice how they connect:

1. `CLAUDE.md` — short table of contents. It does **not** list the rules itself.
2. `.claude/rules/style.md` — how to write functions (pure, validate inputs, type hints).
3. `.claude/rules/testing.md` — how to write tests (every change, sentence-style names, boundaries).

The two lines in `CLAUDE.md` that start with `@` **import** those rule files
into project memory.

---

## Step 2 — Ask Claude about a rule it never had to open

In Claude Code, type exactly:

```text
What are this project's testing rules?
```

**Expected:** Claude answers from `testing.md` without you opening that file:

- tests for every behaviour change
- sentence-style names
- cover the boundary and both sides
- `pytest -q` must pass

That works because project memory is loaded when Claude Code starts.

---

## Step 3 — Add a user-level rule and see the layering

User-level memory applies to **every** project on your machine.

1. Copy `templates/user-level-CLAUDE.md` to:

   `C:\Users\pradip.gadhiya\.claude\CLAUDE.md`

   If the `.claude` folder does not exist yet, create it first.

2. The file should contain this one rule:

   ```text
   - Always explain a change in one sentence before editing files.
   ```

3. **Restart** Claude Code so the new user rule is picked up.

4. Then ask:

   ```text
   add a loyalty_points helper to src/northpeak/pricing.py
   ```

**Watch for three layers at once:**

| Level | File | What you should see |
|---|---|---|
| User | `~/.claude/CLAUDE.md` | Claude explains the change in one sentence **before** editing |
| Project style | `.claude/rules/style.md` | Function is pure and validates inputs |
| Project testing | `.claude/rules/testing.md` | Claude also adds a test |

---

## Step 4 — Discard the demo edit

This change was only to demonstrate layering. Put the project back to
the original 4 tests before you leave:

- In Source Control, choose **Discard All Changes**, or
- In the terminal:

```powershell
git restore .
git clean -fd src/
```

Then run `pytest -q` again. You should still see **`4 passed`**.

---

## What good looks like

- `CLAUDE.md` stays short and `@imports` `style.md` and `testing.md`
- The testing-rules question is answered from the imported file
- The user-level rule layers on top: explain first, still add a test

---

## Reflection (answer in your own words)

1. Why keep rules in small `@imported` files instead of one giant `CLAUDE.md`?
2. Claude answered without opening `testing.md`. When is project memory loaded, and why does that matter?
3. If a user-level rule and a project rule conflict, which wins? When would you put a rule at user level vs project level?
