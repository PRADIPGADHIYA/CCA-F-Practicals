# Exercise 2 — A Precise Refactor with the Built-in Tools (S5)

**Like Exercise 1, this is done by chatting with Claude Code, not by running
a Python script.** No API key setup, no `pip install` — this exercise is
purely about how Claude Code's built-in tools (`Glob`, `Grep`, `Read`,
`Edit`, `Write`) let it explore and change a codebase precisely instead of
reading everything "just in case."

## The scenario

In `sample_codebase/`, `logEvent(name, payload)` in `src/analytics.ts` is
**deprecated**. New code should call `track({ name, props })` instead. A
few call sites in `src/notifications.ts` and `src/orders.ts` still use the
old function. You'll migrate them.

## Files

| Path | Purpose |
|---|---|
| `sample_codebase/src/analytics.ts` | Defines both the deprecated `logEvent` and its replacement `track`. |
| `sample_codebase/src/notifications.ts` | 2 call sites to migrate. |
| `sample_codebase/src/orders.ts` | 2 more call sites (the "stretch" step). |
| `sample_codebase/tests/*.test.ts` | Tests that exercise both files — useful for `Glob` practice. |

## Prerequisite

The Claude Code CLI installed (`claude --version`). No Python setup needed
for this exercise.

## Run

Start Claude Code from **this** folder:

```powershell
cd "Exercise-2-Built-in-Tools"
claude
```

Then type each prompt below, one at a time, and compare against "Expected."

### Step 1 — Glob the test files

```
Glob for all *.test.ts files under sample_codebase and list them.
```

Expected: `sample_codebase/tests/notifications.test.ts` and
`sample_codebase/tests/orders.test.ts`.

### Step 2 — Grep for the deprecated call

```
Grep for `logEvent(` in sample_codebase/src and show the matches.
```

Expected: 4 real call sites (2 in `notifications.ts`, 2 in `orders.ts`),
plus the deprecated definition/comment in `analytics.ts` — 6 lines total.
The 4 calls are what you'll migrate.

### Step 3 — Read the replacement's signature

```
Read sample_codebase/src/analytics.ts so we know the track() signature.
```

The contract: `logEvent(name, payload)` took two positional arguments;
`track({ name, props })` takes a single object.

### Step 4 — Edit one file first

```
In sample_codebase/src/notifications.ts, replace each logEvent(name, payload) call with track({ name, props }), and update the import from logEvent to track.
```

Expected result:

```typescript
import { track } from "./analytics";

export function sendOrderShipped(orderId: string, email: string): void {
  // ... send the "your order shipped" email ...
  track({ name: "order_shipped_email", props: { orderId, email } });
}

export function sendReturnApproved(orderId: string): void {
  // ... send the "return approved" email ...
  track({ name: "return_approved_email", props: { orderId } });
}
```

### Step 5 — Stretch: migrate `src/orders.ts` too

```
Repeat the same migration for sample_codebase/src/orders.ts.
```

Expected result:

```typescript
import { track } from "./analytics";

export function markDelivered(orderId: string): void {
  track({ name: "order_delivered", props: { orderId } });
}

export function cancelOrder(orderId: string, reason: string): void {
  track({ name: "order_cancelled", props: { orderId, reason } });
}
```

Verify by Grepping `logEvent(` in `src/` again — it should now match only
the deprecated definition and its comment in `analytics.ts`, with no live
calls left.

### Step 6 — Write: record the migration in a new file

```
Write a new file sample_codebase/MIGRATION.md that records the logEvent -> track migration, and notes the upcoming order_cancelled -> order_canceled rename.
```

Expected: Claude Code uses **Write** (not Edit, since the file doesn't
exist yet) to create something like:

```markdown
# Migration Notes

- Replaced deprecated logEvent(name, payload) with track({ name, props })
  across src/notifications.ts and src/orders.ts; imports updated.
- Next (Exercise 3): rename analytics event order_cancelled -> order_canceled (one L).
```

## Reflection

- Skipping straight to "read every file in `sample_codebase`" would have
  cost more context for the exact same result, and it's less reliable:
  Grep guarantees you found every `logEvent(` call site deterministically,
  while skimming files by eye can miss one, especially as a codebase grows
  beyond 3 small files.
- Updating the import is part of the same minimal edit because the call
  site and the import are two halves of one dependency — if you change
  `logEvent(...)` to `track(...)` but leave `import { logEvent } from
  "./analytics"` unchanged, the file references a name (`track`) that was
  never imported, and it fails to compile.
- Grep found exactly 4 call sites across 2 files up front, so you know the
  scope of the job before you touch anything — verifying afterward is just
  re-running the same Grep and confirming 0 live calls remain. Reading
  files top to bottom gives no such guarantee; you only find out you
  missed one when something breaks later.
- `Write` is the wrong tool for a two-line change inside a file that
  already exists, because it implies replacing the whole file — for a
  small in-place change you want `Edit`, which touches only the lines that
  changed and leaves everything else untouched. Conversely, `Edit` doesn't
  apply to `MIGRATION.md` because there's no existing file to edit — `Write`
  is the only tool that can create it.
