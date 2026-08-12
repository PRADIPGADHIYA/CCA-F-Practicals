# Exercise 1 — MCP Servers (S4)

**This exercise is different from Lab 2.1's exercises.** There is no
`python something.py` script to run yourself. Instead, you set up two small
local MCP (Model Context Protocol) servers, then start **Claude Code**
(the CLI tool) from this folder — Claude Code launches the servers for you
and calls their tools automatically as you chat with it.

MCP servers give an agent live data sources it can call on demand, instead
of you copy-pasting JSON/text into the chat. This project wires up two:
- **`northpeak-orders`** — order lookups (`get_order`, `find_orders_by_email`) from `data/orders.json`.
- **`northpeak-docs`** — policy documents (`list_docs`, `read_doc`, `search_docs`) from `data/docs/`.

## Files

| Path | Purpose |
|---|---|
| `.mcp.json` | Tells Claude Code which two MCP servers to launch and how. |
| `requirements.txt` | The one dependency the servers need (`mcp`). |
| `mcp_servers/orders_server.py` | Orders source — `get_order`, `find_orders_by_email`. |
| `mcp_servers/docs_server.py` | Docs source — `list_docs`, `read_doc`, `search_docs`. |
| `data/orders.json` | 4 sample orders. |
| `data/docs/*.md` | 3 policy documents (returns, shipping, warranty). |

## Prerequisite: Claude Code installed

This exercise requires the **Claude Code CLI** (a separate tool from this
Cursor IDE). Check it's installed:

```powershell
claude --version
```

If that fails, install it first (see [docs.claude.com/en/docs/claude-code](https://docs.claude.com/en/docs/claude-code/overview)) before continuing.

## Setup (one-time)

```powershell
cd "Exercise-1-MCP-Servers"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Important: point `.mcp.json` at your venv's Python

`.mcp.json` currently launches the servers with `python3`, which works on
macOS/Linux. On Windows, `python3` usually isn't on your PATH, and even if
it is, it won't have the `mcp` package installed unless it's your venv.
Open `.mcp.json` and change both `"command": "python3"` lines to your venv's
interpreter:

```json
"command": ".venv\\Scripts\\python.exe"
```

## Run

Start Claude Code **from this folder** (this matters — it's how Claude Code
finds `.mcp.json`):

```powershell
cd "Exercise-1-MCP-Servers"
claude
```

Then, inside the Claude Code session, type these prompts one at a time:

### Step 1 — confirm both servers connected

```
/mcp
```

Expected: both `northpeak-orders` and `northpeak-docs` listed as connected,
exposing `get_order`, `find_orders_by_email`, `list_docs`, `read_doc`, `search_docs`.

### Step 2 — warm up with a single-source question

```
What's the status of order NP-100245?
```

Expected: Claude Code calls `get_order("NP-100245")` and reports status
`shipped`, items `["TENT-2P-RX", "BAG-20F-DN"]`, with a tracking number.

### Step 3 — ask a question that needs BOTH sources

```
Order NP-100190 was delivered. The customer wants to return one item — are they still inside the return window, and what condition rules apply?
```

Expected tool sequence: `get_order("NP-100190")` (status `delivered`, items
`["BOOT-GTX-M", "FILT-PMP"]`), then `read_doc("returns-policy")` (or
`search_docs("return")`), then a combined answer that:
- confirms the order is within the 30-day return window (measured from the delivery date), and
- flags that the order contains boots (`BOOT-GTX-M`), so **worn footwear cannot be returned**.

Try this too:

```
Which policy docs do you have?
```

Expected: Claude Code calls `list_docs()` and returns `returns-policy`,
`shipping-policy`, `warranty` — instead of guessing.

## Troubleshooting

If `/mcp` shows a server as not connected, it's almost always the
interpreter — `.mcp.json`'s `command` must point at a Python that has `mcp`
installed. Point it at `.venv\Scripts\python.exe` (see above) and re-run `/mcp`.

## Reflection

- Declaring two MCP servers instead of pasting order JSON and the returns
  doc into the chat means the data stays live and accurate for the whole
  session — every time you ask a new question, Claude Code re-fetches
  current data instead of working from a stale copy you pasted once. It
  also keeps the chat context small: the agent only pulls the specific
  order or doc it needs, not everything you might ever ask about.
- The agent picked `get_order` for the order and `read_doc`/`search_docs`
  for the policy because each tool's name and description are specific and
  non-overlapping ("look up a single order by ID" vs. "full text of one
  policy doc by name") — the same "strong tool interface" idea from Lab
  2.1's Exercise 1, just applied to MCP tools instead of hand-written ones.
- Without the orders server, the agent would only have the returns policy
  text — it would know boots generally can't be returned if worn, but it
  has no way to know THIS order (`NP-100190`) actually contains boots at
  all. It would have to ask the customer directly, or guess — exactly the
  kind of guess MCP sources are meant to eliminate.
