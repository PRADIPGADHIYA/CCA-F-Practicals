# Exercise 1 — Message Batches API (overnight bulk)

You do **not** need to know Python. `build_requests()` and the polling
loop are already filled in. This exercise **submits a real batch** and
may take several minutes.

**Time:** about 15 minutes  
**Open this folder** (`Week 04/LAB 03/Exercise_1_Message_Batches`)

---

## What this is (in plain English)

Overnight, a media team classifies thousands of headlines. They do **not**
need the answer in one second — they need it cheap and complete by morning.

The Message Batches API:

1. You submit many requests at once, each tagged `headline-0`, `headline-1`, …
2. Claude processes them in the background
3. You poll until status is `ended`
4. You match results by `custom_id` (not by order)

If the script hits a 10-minute deadline, it prints a `--fetch` command.
Nothing is lost — you can collect later.

---

## Step 0 — Setup (Windows)

1. Copy `.env.example` to `.env` and paste your `ANTHROPIC_API_KEY`.
2. In a terminal **in this folder**:

```powershell
.\.venv\Scripts\activate
pip install -r requirements.txt
python exercise_1_message_batches.py
```

---

## If it is still processing

```powershell
python exercise_1_message_batches.py --fetch <batch_id>
```

Use the id the script printed (`submitted batch: ...`).

**Expected:** one line per headline, e.g. `headline-0: positive`.

---

## Reflection

1. When is batch the right tool, and when is it the wrong one?
2. Why does every request need a `custom_id`?
3. Why a 10-minute deadline plus `--fetch`, instead of waiting forever?
