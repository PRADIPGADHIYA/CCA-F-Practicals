# Exercise 3 — Gate on structured JSON

You do **not** need to know Python. This exercise turns a `{decision, issues}`
JSON verdict into a pass/fail exit code that CI can use to block a bad PR.

**Time:** about 12 minutes  
**Open this folder in Cursor / VS Code** before you start  
(`LAB 03/Exercise_3_Review_Gate`)

The sample-file steps need **no API key**.

---

## The idea (in plain English)

Machines cannot reliably gate on a paragraph of English. They can gate on:

```json
{
  "decision": "approve",
  "issues": []
}
```

`scripts/review_gate.py` reads that object and:

- `approve` → exit **0** (CI step passes)
- `request_changes` → exit **1** (CI step fails, merge is blocked)

`/pr-review` (see `.claude/commands/pr-review.md`) tells Claude to emit
**only** that JSON.

---

## Step 0 — Confirm the environment (already done)

```powershell
.\.venv\Scripts\activate
pytest -q
```

You should see **`6 passed`**.

---

## Step 1 — Run the gate on the provided samples

```powershell
python scripts/review_gate.py samples/sample_review.json
echo $LASTEXITCODE
```

**Expected:** `review-gate: PASS` and exit code **0**.

```powershell
python scripts/review_gate.py samples/sample_review_fail.json
echo $LASTEXITCODE
```

**Expected:** `review-gate: FAIL` and exit code **1**.

The fail sample is wrapped in the `claude -p --output-format json` envelope
(the verdict is a JSON string inside `result`). The gate unwraps it
automatically.

---

## Step 2 — Generate a verdict with `/pr-review`

1. Ask Claude to make a small change (or edit a comment yourself).
2. In Claude Code, run:

   ```text
   /pr-review
   ```

3. Paste Claude’s JSON into a new file named `review.json` in this folder.
4. Run:

   ```powershell
   python scripts/review_gate.py review.json
   echo $LASTEXITCODE
   ```

---

## Step 3 — Read how the gate works

Open `scripts/review_gate.py`. In order it:

1. Strips Markdown code fences (```) if Claude wrapped the JSON
2. Unwraps the `result` envelope if present
3. Reads `decision`
4. Returns exit 0 for `approve`, exit 1 otherwise

CI treats a non-zero exit as a failed step — which blocks the merge.

---

## What good looks like

- An “approve” verdict passes the gate (exit 0)
- A “request_changes” verdict fails it (exit 1)
- `/pr-review` produces the `{decision, issues}` object the gate consumes

---

## Reflection (answer in your own words)

1. Why have Claude emit strict JSON instead of a prose review for the CI gate?
2. Why does the gate accept both a bare review object and the `--output-format json` envelope, and strip code fences?
3. How does an exit code become a PR gate, and why exit codes specifically?
