# Lab 2.1 — Designing Reliable Tools: Interfaces, Errors & Selection Control (CCA-F, Module 2)

This folder contains three **separate, self-contained** Python projects,
one per exercise from *Lab 2.1*, built around a customer-support agent
for a fictional online outdoor-gear store, "NorthPeak Outfitters."

| Folder | Section | What it builds |
|---|---|---|
| `Exercise-1-Tool-Interfaces` | S1 | A weak toolset vs. a strong toolset, scored on how often each routes 6 questions to the correct tool. |
| `Exercise-2-Structured-Errors` | S2 | A flaky Orders service wrapped so it always returns an `isError`/`isRetryable` envelope, plus a retry-with-backoff loop. |
| `Exercise-3-Selection-Control` | S3 | The same triage step run under `auto`, `any`, and a forced `tool_choice` to see which one is deterministic. |

Each project is independent — its own `requirements.txt`, `.env.example`,
`.gitignore`, and `README.md` with exact run instructions.

## You don't know Python — here's the fastest path to running these

For each exercise, in order:

1. Open a terminal (PowerShell) inside that exercise's folder:

   ```powershell
   cd "Exercise-1-Tool-Interfaces"
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

5. Run the exercise's script — see each folder's own `README.md` for
   exact commands and what to expect.

Repeat for all three folders.

## Note on the model

Every script reads its model from the `ANTHROPIC_MODEL` environment
variable and defaults to `claude-haiku-4-5-20251001` if it isn't set — per
the lab spec, nothing is hard-coded. To use a different model (e.g.
Sonnet, for stronger reasoning), uncomment and edit the `ANTHROPIC_MODEL`
line already included in each `.env.example` / `.env`.

## Suggested order

Work through them in order — 1 → 2 → 3 — since the lab's own framing
builds from "does the model pick the right tool" (Ex 1), to "what
happens when that tool fails" (Ex 2), to "is the model even allowed to
reach for a tool this turn" (Ex 3).

## Common issue: authentication / rate-limit errors

If a script errors out on authentication or a `RateLimitError`:

- Confirm `.env` (not just `.env.example`) exists in that exercise's folder.
- Confirm the key has no extra quotes/spaces: `ANTHROPIC_API_KEY=sk-ant-...`
- Confirm you're running from inside that folder's activated virtual environment.
- If you see a rate limit of `0` for a workspace, that workspace's admin
  needs to raise it, or use a personal key from a workspace with a real
  limit instead.
