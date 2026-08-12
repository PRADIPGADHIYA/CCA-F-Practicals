# Lab 2.2 — Connecting the Ecosystem: MCP Servers & Built-in Claude Code Tools (CCA-F, Module 2)

**This lab works differently from Lab 2.1.** Lab 2.1's exercises were
Python scripts you ran with `python something.py`, calling the Anthropic
API directly. Lab 2.2 is run **inside the Claude Code CLI** — you set up
some files, start `claude` from a folder, and type prompts at it. Claude
Code itself decides when to call an MCP tool or a built-in tool
(`Glob`/`Grep`/`Read`/`Edit`/`Write`) — there's no custom Python "harness"
script to write for this lab.

| Folder | Section | What it covers |
|---|---|---|
| `Exercise-1-MCP-Servers` | S4 | Two local MCP servers (orders + policy docs) that Claude Code calls live instead of you pasting data in. |
| `Exercise-2-Built-in-Tools` | S5 | Migrate a deprecated function across a small TypeScript codebase using `Glob` → `Grep` → `Read` → `Edit` → `Write`. |
| `Exercise-3-Incremental-Exploration` | S6 | A one-letter rename done via the efficient `Grep` → `Read` → `Edit` loop, contrasted with reading the whole codebase. |

Each folder is self-contained with its own `README.md` giving the exact
prompts to type into Claude Code and what to expect back.

## You don't know Python — what you actually need to do here

Good news: this lab needs almost no Python from you.

- **Exercise 1** needs a virtual environment with one package (`mcp`)
  installed, so the two local MCP servers can run — but you never write or
  run Python code yourself; Claude Code launches the servers for you.
- **Exercises 2 and 3** need **no Python at all** — they're about a small
  TypeScript sample codebase, but you never compile or run it either; you
  just ask Claude Code to explore and edit it.

## Prerequisite for all three exercises: Claude Code CLI

Check it's installed:

```powershell
claude --version
```

If missing, install it first — see
[docs.claude.com/en/docs/claude-code/overview](https://docs.claude.com/en/docs/claude-code/overview).
(On the course's Blue Labs VM this is pre-installed and your API key is
pre-configured — you don't need to set an API key manually there.)

## Suggested order

Work through them in order — 1 → 2 → 3, matching the PDF's own S4 → S5 → S6
structure:

1. **Exercise 1 (S4)** — wire up and use two MCP servers.
2. **Exercise 2 (S5)** — precise refactor with the built-in tools.
3. **Exercise 3 (S6)** — the same idea, taken further: locate → read → change, touching exactly one file.

Open each folder's own `README.md` before starting it — it has the exact
setup commands, the exact prompts to type at Claude Code, and what "good"
looks like for that exercise.

## Common issue: an MCP server shows as "not connected"

This only applies to Exercise 1. It's almost always the Python
interpreter: `.mcp.json` launches the servers with `python3`, which must
have the `mcp` package installed. On Windows this usually fails because
`python3` isn't on PATH or isn't your venv. Point `.mcp.json`'s `command`
at your venv's interpreter (`.venv\Scripts\python.exe`) and re-run `/mcp`
inside Claude Code. Exercise 1's own README covers this in detail.
