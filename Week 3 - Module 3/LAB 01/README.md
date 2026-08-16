# LAB 01 — Configuring Claude Code (Lab 3.1)

NorthPeak Outfitters pricing service. Three **separate** projects, one per
exercise, so work in Exercise 1 cannot break Exercise 2 or 3.

You do **not** need to know Python. Open each folder, follow `START_HERE.md`,
and talk to Claude Code in plain English.

| Folder | Exercise | What you practice |
|---|---|---|
| `Exercise_1_CLAUDE_md_Hierarchy` | Ex 1 (~12 min) | `CLAUDE.md`, `@import`, user-level vs project memory |
| `Exercise_2_Slash_Commands` | Ex 2 (~15 min) | `/test` and `/review` slash commands |
| `Exercise_3_Skills` | Ex 3 (~12 min) | Changelog skill auto-invoked by description |

Each folder is a full copy of the starter: the pricing library, a green
pytest suite (4 tests), and the `.claude/` config.

## How to work

1. In Cursor / VS Code: **File > Open Folder...** and pick **one** exercise folder.
2. Open that folder's `START_HERE.md` and follow the steps.
3. Start Claude Code **from that folder** so it finds `CLAUDE.md` and `.claude/`.
4. When you finish, open the next exercise folder the same way.

## Environment

Each exercise folder already has a `.venv`, pytest installed, and a git
baseline commit (needed so `/review` and the changelog skill can see diffs).

To re-check tests:

```powershell
.\.venv\Scripts\activate
pytest -q
```

Expect: `4 passed`.

## Config map (same in every exercise folder)

```
CLAUDE.md                          project memory; @imports the rule modules
.claude/rules/style.md             how to write functions
.claude/rules/testing.md           how to write tests
.claude/commands/test.md           /test
.claude/commands/review.md         /review
.claude/skills/changelog/SKILL.md  changelog skill (auto-invoked)
src/northpeak/pricing.py           the pricing code
src/tests/test_pricing.py          4 pytest tests
```

## Memory hierarchy (Exercise 1)

More specific wins on conflict:

1. User — `C:\Users\<you>\.claude\CLAUDE.md` (every project)
2. Project — `./CLAUDE.md`
3. Imported modules — `.claude/rules/*.md`
