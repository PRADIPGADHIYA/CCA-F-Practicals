# Exercise 3 — Explore Incrementally, Not All at Once (S6)

Same idea as Exercise 2 — you drive this by chatting with Claude Code, no
Python script to run. This exercise makes one small change — renaming an
analytics event — the efficient way: **find → read only what matters →
change minimally**, and then contrasts that with the expensive "read
everything first" alternative.

## The scenario

Rename the analytics event `order_cancelled` to `order_canceled` (one `L`).
It's used once, inside `cancelOrder` in `sample_codebase/src/orders.ts`.
This folder's copy of `sample_codebase` starts in the same pre-migration
state as Exercise 2 (the call is still `logEvent(...)`) — the rename works
identically either way, since only the event-name string changes.

## Files

| Path | Purpose |
|---|---|
| `sample_codebase/src/orders.ts` | Contains the one `order_cancelled` occurrence to rename. |
| `sample_codebase/src/*.ts`, `sample_codebase/tests/*.ts` | The rest of the codebase — deliberately present so you can see the incremental loop skip over it. |

## Prerequisite

The Claude Code CLI installed (`claude --version`).

## Run

Start Claude Code from **this** folder:

```powershell
cd "Exercise-3-Incremental-Exploration"
claude
```

### Step 1 — Ask for the change

```
We're renaming the analytics event `order_cancelled` to `order_canceled` (one L). Make that change.
```

### Step 2 — Watch the efficient path

Expected: Claude Code Greps for `order_cancelled` (one hit, in
`src/orders.ts`), Reads only that file, then Edits just that line:

```typescript
// before
logEvent("order_cancelled", { orderId, reason });
// after
logEvent("order_canceled", { orderId, reason });
```

(If you'd run Exercise 2's stretch step first, the call would already be
`track(...)` — either way, only the event-name string changes.)

### Step 3 — Contrast the heavy way

Try asking instead:

```
Read every file in sample_codebase first, then make the same rename.
```

Notice how much more context that burns to produce the exact same
one-line diff — that's the cost the incremental loop avoids.

### Step 4 — Update the migration note (if you did Exercise 2's Step 6)

If you're carrying `MIGRATION.md` over from Exercise 2, update its "Next
(Exercise 3)" line to record the rename as done. In this self-contained
folder, you can ask Claude Code to create it fresh:

```
Update (or create) sample_codebase/MIGRATION.md to record that the order_cancelled -> order_canceled rename is done.
```

## What good looks like

The rename touches exactly **one file** (`src/orders.ts`), found by Grep,
with no unnecessary reading of unrelated files (`analytics.ts`,
`notifications.ts`, the test files) that don't contain the string at all.

## Reflection

- A one-letter rename and a whole-repo read produce the identical final
  diff, but the path matters because cost and risk scale with how much
  you touch: on a real monorepo, "read everything first" burns far more
  context/time per change and gives more surface area for the model to
  accidentally edit something it wasn't asked to.
- "Read the whole file" (or several) is the right call when you're
  actually unsure how a symbol is used across a wider area — e.g. before a
  risky signature change, or when Grep's results are ambiguous and you
  need surrounding context to judge each hit. You can tell it's NOT one of
  those cases when, like here, Grep already returns one exact, unambiguous
  hit that fully describes the scope of the change.
- Good sources (MCP, in Exercises 1) and precise tools (Glob/Grep/Read/Edit,
  in Exercises 2-3) reinforce each other: sources without precise tools
  just gives the model more raw material to dump into context wholesale;
  precise tools without good sources means the agent acts confidently on
  a codebase or data it never actually loaded correctly, or has to guess
  at facts (like order contents) that live outside the file it's editing.
