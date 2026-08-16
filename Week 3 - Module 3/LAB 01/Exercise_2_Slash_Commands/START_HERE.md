# Exercise 2 — Slash commands (`/test` and `/review`)

You do **not** need to know Python. This exercise turns two recurring chores
into one-word commands.

**Time:** about 15 minutes  
**Open this folder in Cursor / VS Code** before you start  
(`LAB 01/Exercise_2_Slash_Commands`)

---

## What a slash command is

A command is just a Markdown file in `.claude/commands/`.

| File | Command you type |
|---|---|
| `.claude/commands/test.md` | `/test` |
| `.claude/commands/review.md` | `/review` |

The **filename is the command name**. YAML at the top of the file sets
`description`, `allowed-tools`, and `argument-hint`. `$ARGUMENTS` is
replaced by whatever you type after the command.

---

## Step 0 — Confirm the environment (already done)

A Python environment and a git baseline are already set up in this folder.
In a terminal here, you can confirm the 4 tests are green:

```powershell
.\.venv\Scripts\activate
pytest -q
```

You should see **`4 passed`**. Then start Claude Code from this folder.

---

## Step 1 — Read the command files

Open:

1. `.claude/commands/test.md` — runs tests, must not change code.
2. `.claude/commands/review.md` — notice:
   - `allowed-tools` is **read-only** (`git diff`, `git status`, Read, Grep)
   - `$ARGUMENTS` is the optional path you pass in
   - it says **do not edit files**

---

## Step 2 — Run `/test`

In Claude Code, type:

```text
/test
```

**Expected:** Claude runs `python -m pytest -q` and reports **`4 passed`**.

If something failed, the command should name the failing tests and explain
the likely cause — without changing any code.

---

## Step 3 — Make a change, then run `/review`

Ask Claude (or paste this request):

```text
Add a new public function gift_wrap_fee to src/northpeak/pricing.py.
Do not add a test.
```

You do not need to write the Python yourself. Then run:

```text
/review pricing.py
```

`pricing.py` is passed in as `$ARGUMENTS`.

**Expected:** Claude runs `git diff`, applies the four-point checklist, and
groups findings as **blocker / suggestion / nit**. It should flag:

- missing test (`testing.md`)
- missing type hint or docstring if those are absent (`style.md`)

It should end with a verdict like `Needs changes: 3` and **must not edit files**.

---

## Step 4 — Make the command your own

1. Open `.claude/commands/review.md`.
2. Edit the checklist — add a rule or reword a check.
   Example extra check: "Does the change mention money units (USD) in the docstring?"
3. Save the file.
4. Run `/review` again and confirm your new check appears in the review.

Because the file is in the repo, the whole team would get the updated checklist.

---

## What good looks like

- `/test` reports the real pytest pass/fail count
- `/review` reads the diff, groups findings, ends with a one-line verdict
- `/review` never edits files (its tools are read-only)
- The command name matches the filename exactly

---

## Reflection (answer in your own words)

1. `/review` lists read-only tools and says “do not edit files.” Why scope a command’s tools so tightly?
2. What do you gain by checking `/test` and `/review` into the repo versus typing the prompt by hand every time?
3. What is `$ARGUMENTS` for, and how does it let one command serve many situations?
