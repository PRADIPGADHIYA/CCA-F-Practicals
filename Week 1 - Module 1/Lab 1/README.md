# Lab 1.1 — Building the Agentic Loop (CCA-F, Module 1)

This folder contains four **separate, self-contained** Python projects,
one per exercise from *Lab 1.1: Building the Agentic Loop: Orchestration
& Subagent Coordination*. They build a support-ticket triage pipeline
for a fictional company, "Arctive":

```
Inbound Ticket → [COORDINATOR] → Classifier → CRM Enricher → Drafter → Validator → Outbound Response
```

| Folder | Exercise | What it builds |
|---|---|---|
| `Exercise-1-Agentic-Loop` | Ex 1 (S1) | A loop that calls a classification tool until `stop_reason` says it's done. |
| `Exercise-2-Coordinator-Subagents` | Ex 2 (S2) | A coordinator that calls 4 specialist subagents (hub-and-spoke, no shared memory). |
| `Exercise-3-Context-Passing` | Ex 3 (S3) | A typed `TicketContext` object that makes every handoff explicit. |
| `Exercise-4-Step-Enforcement` | Ex 4 (S4) | Programmatic gates that block a step until the previous one is verified complete. |

Each project is independent — it has its own `requirements.txt`,
`.env.example`, and `README.md` with exact run instructions, and can be
opened/run without needing the others. Later exercises carry forward the
files they build on (e.g. Exercise 4 reuses Exercise 3's `context.py`),
copied into their own folder so each exercise stays self-contained.

## You don't know Python — here's the fastest path to running these

You already have **Python 3.14** installed, which is great. For each
exercise, in order:

1. Open a terminal (PowerShell) inside that exercise's folder, e.g.:

   ```powershell
   cd "Exercise-1-Agentic-Loop"
   ```

2. Create an isolated environment for that project (keeps its packages
   separate from everything else on your machine) and activate it:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

   > If PowerShell blocks the activation script with an
   > "execution policy" error, run this once (as your normal user, not
   > admin) and try again:
   > `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

3. Install that project's dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Set up your Anthropic API key. Copy the example env file and edit it:

   ```powershell
   Copy-Item .env.example .env
   ```

   Then open `.env` in any text editor and replace `your-api-key-here`
   with your real key from <https://console.anthropic.com/>. (This lab
   was originally written for a pre-configured Blue Labs VM — since
   you're running locally on Windows, the `.env` file + `python-dotenv`
   is the equivalent way to supply the key.)

5. Run the exercise's main script (each README names the exact command),
   e.g.:

   ```powershell
   python loop.py
   ```

Repeat steps 1–5 for each of the four exercise folders. Full details,
expected output, and the lab's reflection questions/experiments are in
each folder's own `README.md`.

## Suggested order

Work through them in order — 1 → 2 → 3 → 4 — since each one deepens the
same triage pipeline: Exercise 1 teaches the loop mechanics in
isolation, Exercise 2 splits work across specialist subagents, Exercise
3 formalizes the state they share, and Exercise 4 makes the step order
impossible to violate silently.

## Common issue: authentication error

If a script errors out complaining about authentication, double check:

- `.env` exists in that exercise's folder (not just `.env.example`).
- The key inside it has no extra quotes or spaces:
  `ANTHROPIC_API_KEY=sk-ant-...`
- You're running the script from inside the activated virtual
  environment for that folder.
