# Lab 5.1 — Managing Context: Preservation, Optimization & Escalation

You do **not** need to know Python. The three lab TODOs are already filled
in. Your job is to run the script and read what each demo prints.

**Time:** about 40 minutes  
**Open this folder** before you start (`Week 05/Lab01`)

---

## What this is (in plain English)

You are building a multi-turn support agent for an online shop. The sample
customer is **Aarti Sharma**, id **C-1001**, Gold tier, with three orders:

| Order | Status | Total |
|---|---|---|
| O-9001 | Delivered | 1499 |
| O-9002 | Shipped | 2799 |
| O-9003 | Processing | 549 |

A real chat can last 10–20 turns. Three things go wrong if you do nothing:

1. The agent **forgets** the customer id that was said on turn 2.
2. One order lookup dumps **too many fields** and crowds out earlier turns.
3. “Cancel my order” is **ambiguous** (two open orders) and guessing is costly.

This lab pins facts, trims tool output, and tells the agent to **ask** when
unsure.

---

## Step 0 — One-time setup (Windows)

1. Copy `.env.example` to `.env`.
2. Paste your Anthropic API key into `.env` (replace `your_key_here`).
3. In a terminal **in this folder**:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

---

## Step 1 — Prove the logic without spending API calls

```powershell
python main.py --check
```

**Expected:** it prints the `[CASE FACTS]` block (C-1001 / Aarti Sharma /
Gold), then a smaller optimized order list (no `customer_id`, no `items`),
then the two open order ids, and ends with `Offline check passed`.

You do not need to change any file.

---

## Step 2 — Run the three live demos

```powershell
python main.py
```

**Demo 1 — Preservation.** Four turns of small talk, then “what is my
customer ID and what tier am I?” The agent should answer **C-1001** and
**Gold** from the pinned `[CASE FACTS]` block, not by asking again.

**Demo 2 — Optimization.** You will see RAW vs OPTIMIZED JSON. Optimized
rows keep only `order_id`, `status`, `placed_on`, `total`. Then the agent
lists the orders.

**Demo 3 — Escalation.** The user says “Please cancel my order.” There are
two open orders (O-9002, O-9003). A good agent **asks which one**, and does
not pick.

---

## Files (you can open them, you do not need to edit them)

| File | What it does |
|---|---|
| `case_facts.py` | Builds the `[CASE FACTS]` block every turn |
| `tool_optimizer.py` | Drops extra tool fields before they reach Claude |
| `main.py` | Chat loop + three demos + the ASK-on-ambiguity prompt |
| `sample_data.py` | Fake customer and three orders |

---

## What good looks like

- Demo 1 last reply includes **C-1001** and **Gold**.
- Demo 2 optimized JSON is clearly smaller than raw JSON.
- Demo 3 reply is a **question** about which order, not a cancellation.

---

## Reflection (answer in your own words)

1. Why pin case facts in the **system prompt** instead of hoping the model
   remembers turn 2?
2. Why whitelist fields **per tool name** instead of sending the full order
   row every time?
3. Why is guessing on “cancel my order” more expensive than asking one
   clarifying question?
