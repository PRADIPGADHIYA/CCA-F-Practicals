# Exercise 2 — Run Claude headless in CI

You do **not** need to know Python. This exercise is about reading a GitHub
Action and understanding `claude -p` (one-shot, no chat).

**Time:** about 12 minutes  
**Open this folder in Cursor / VS Code** before you start  
(`LAB 03/Exercise_2_Headless_CI`)

Reading the workflow needs **no API key**. The optional live `claude -p`
command does need `ANTHROPIC_API_KEY` and Claude Code installed.

---

## What “headless” means (in plain English)

Interactive Claude is a conversation: you type, it replies, you type again.

`claude -p "your prompt"` runs **once**, prints a result, and exits. That is
what CI needs — there is no human sitting at a terminal.

The workflow in `.github/workflows/claude-review.yml` does this on every
pull request.

---

## Step 0 — Confirm the environment (already done)

```powershell
.\.venv\Scripts\activate
pytest -q
```

You should see **`6 passed`**. Start Claude Code from this folder if you want
to try the live command later.

---

## Step 1 — Read the workflow

Open `.github/workflows/claude-review.yml`. Trace these steps in order:

| Step | What it does |
|---|---|
| Checkout `fetch-depth: 0` | Full git history so the base branch can be diffed |
| Install Claude Code | `npm install -g @anthropic-ai/claude-code` |
| `git diff origin/<base>...HEAD > pr.diff` | Capture **only the PR changes** |
| `claude -p ... --output-format json` | Headless review; writes JSON |
| `python scripts/review_gate.py review.json` | Pass (exit 0) or fail (exit 1) |

Also open `.claude/commands/pr-review.md` — that is the review contract the
workflow asks Claude to follow.

---

## Step 2 — Run the headless command locally (optional)

Only if `ANTHROPIC_API_KEY` is set and Claude Code is installed:

```powershell
claude -p "Summarize what src/northpeak/refunds.py does in one sentence." --output-format json
```

The result is a JSON **envelope**. The assistant’s text is in the `result`
field. That is why the gate unwraps `result`:

```json
{
  "type": "result",
  "is_error": false,
  "result": "refund_amount returns the refund for a NorthPeak order ..."
}
```

If you do not have an API key, skip this step. You can still explain the
workflow from Step 1.

---

## Step 3 — Use it for real (optional)

Push this folder to GitHub and add `ANTHROPIC_API_KEY` as an Actions secret
(**Settings > Secrets and variables > Actions**). Open a pull request and the
workflow runs the review automatically on the diff.

**Never commit the API key.**

---

## What good looks like

You can explain each workflow step — full-history checkout, install, diff the
base branch, headless `claude -p`, gate the JSON — and you understand why the
run is non-interactive and why the key is a repo secret.

---

## Reflection (answer in your own words)

1. What does `claude -p` change versus an interactive session, and why does CI need that?
2. Why review only the PR diff, not the whole repo? Why is `fetch-depth: 0` needed?
3. Why is the key an Actions secret rather than a file in the repo?
