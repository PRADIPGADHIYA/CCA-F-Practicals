---
name: changelog-entry
description: >
  Use when the user wants to add a CHANGELOG entry, write release
  notes, or summarize a change. Triggers include "update the changelog",
  "add a changelog entry", and "release notes".
---

# Changelog entry

Turn the current uncommitted code changes into a Keep a Changelog entry.

## Steps

1. Inspect the change with `git diff` and `git status`. If there is no diff, say so and stop.
2. Skip formatting-only edits (whitespace, comments, rename-only). Do not write an entry for those.
3. Group remaining changes under **Added**, **Changed**, **Fixed**, or **Removed**.
4. Write **user-facing sentences** — what a shopper or teammate would notice, not implementation details.
5. Prepend the entry under `## [Unreleased]` at the top of `CHANGELOG.md`. Create the file if it does not exist.

## Output format

```markdown
## [Unreleased]

### Added
- Optional gift-wrap fee helper for orders.
```

Use only the headings that apply. Keep each bullet to one short sentence.
