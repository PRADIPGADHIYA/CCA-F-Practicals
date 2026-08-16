# Exercise 3 — Skills (changelog entry)

You do **not** need to know Python. This exercise packages a multi-step
workflow that Claude starts on its own when your words match the skill
description.

**Time:** about 12 minutes  
**Open this folder in Cursor / VS Code** before you start  
(`LAB 01/Exercise_3_Skills`)

---

## What a skill is

A skill is a folder with a `SKILL.md`. Unlike a slash command, you do
**not** type `/changelog`. Claude auto-invokes it when your request
matches the `description` in the frontmatter.

This repo ships a **changelog-entry** skill that turns a code change into
a Keep a Changelog entry.

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

## Step 1 — Read the SKILL.md

Open `.claude/skills/changelog/SKILL.md`.

Notice:

- **Frontmatter** `name` and `description` — the description is the trigger
- Concrete phrases such as “update the changelog” and “release notes”
- Numbered steps
- Output format (`## [Unreleased]`, then Added / Changed / Fixed / Removed)

---

## Step 2 — Make a change to summarize

The skill summarizes what changed, so git needs a real diff.

Ask Claude:

```text
Add a new public function gift_wrap_fee to src/northpeak/pricing.py.
```

(Or keep any small one-line change.) You do not need to write the Python
yourself.

---

## Step 3 — Trigger the skill by description

Ask in **plain language**. Do **not** name the skill:

```text
Update the changelog for this change.
```

**Expected:** Claude recognizes the request, follows the skill steps
(look at `git diff`, group under Added/Changed/Fixed/Removed, write
user-facing sentences), and prepends a `## [Unreleased]` entry to
`CHANGELOG.md` (creating the file if needed).

A correct entry looks like:

```markdown
## [Unreleased]

### Added
- Optional gift-wrap fee helper for orders.
```

---

## What good looks like

- Asking “update the changelog” triggers the skill by description (you never name it)
- The entry groups changes under Added / Changed / Fixed / Removed
- Each bullet is a short user-facing sentence
- The entry is prepended under `## [Unreleased]` in `CHANGELOG.md`

---

## Reflection (answer in your own words)

1. A skill is auto-invoked by its description; a slash command is called by name. When is each the right way to package work?
2. Why does the quality of the `description` field matter so much? What happens if it is too narrow, or too broad?
3. The SKILL.md bakes in judgment (“user-facing sentences,” “skip formatting-only edits”). Why encode that in the skill rather than leaving it to each run?
