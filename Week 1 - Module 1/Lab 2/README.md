# Lab 1.2 — Controlling Execution: Hooks, Decomposition & Session State (CCA-F, Module 1)

This folder contains three **separate, self-contained** Python projects,
one per exercise from *Lab 1.2*, built around a SOC (Security Operations
Center) copilot scenario for a fictional financial firm, "NorthGate
Capital." This lab builds on Lab 1.1's agentic loop and coordinator
pattern, adding the three controls a production-grade agent needs:

| Folder | Section | What it builds |
|---|---|---|
| `Exercise-1-Hooks-Interception` | S5 | A hook chain (log / validate / block) that sits between the model's tool-call decision and the real side-effect. |
| `Exercise-2-Task-Decomposition` | S6 | A fixed 3-step intel digest vs. an adaptive alert-triage router that branches by incident type. |
| `Exercise-3-Session-Management` | S7 | Save/resume, fork (parallel hypotheses), and summarize — session state that outlives a single conversation. |

Each project is independent — its own `requirements.txt`, `.env.example`,
`.gitignore`, and `README.md` with exact run instructions.

## You don't know Python — here's the fastest path to running these

You already have Python installed. For each exercise, in order:

1. Open a terminal (PowerShell) inside that exercise's folder:

   ```powershell
   cd "Exercise-1-Hooks-Interception"
   ```

2. Create and activate a virtual environment:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

   > If PowerShell blocks the activation script, run once:
   > `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

3. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Set up your API key:

   ```powershell
   Copy-Item .env.example .env
   ```

   Then open `.env` in a text editor and replace `your-api-key-here` with
   your real key from [console.anthropic.com](https://console.anthropic.com/).
   Make sure the key's workspace has a real (non-zero) rate limit.

5. Run the exercise's script(s) — see each folder's own `README.md` for
   the exact commands and what to expect.

Repeat for all three folders.

## Suggested order

Work through them in order — 1 → 2 → 3 — since Exercise 1's hooks are
reused conceptually in the reflection questions for Exercise 2 and 3, and
each section is independent enough to run on its own once set up.

## Note on Exercise 1's model

`agent_with_hooks.py` uses `claude-haiku-4-5-20251001` (fast and
cost-efficient). If you want the strongest reasoning for multi-step tool
routing instead, open the file and change the `MODEL` variable to
`claude-opus-4-6` or another model you have access to.

## Common issue: authentication / rate-limit errors

If a script errors out on authentication or a `RateLimitError`:

- Confirm `.env` (not just `.env.example`) exists in that exercise's folder.
- Confirm the key has no extra quotes/spaces: `ANTHROPIC_API_KEY=sk-ant-...`
- Confirm you're running from inside that folder's activated virtual environment.
- If you see a rate limit of `0 tokens/minute` for a workspace, that
  workspace's admin needs to raise it — see the notes from Lab 1.1's
  README/troubleshooting for the full explanation.
