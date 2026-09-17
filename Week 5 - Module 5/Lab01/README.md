# LAB 01 — Managing Context (Lab 5.1)

E-commerce support agent for **Aarti Sharma (C-1001)**. One project, three
demos in `main.py`. You do **not** need to write Python — each TODO from the
lab is already filled in.

| Demo | Section | What you practice |
|---|---|---|
| 1 — Preservation | S1 | `[CASE FACTS]` stays in the system prompt every turn |
| 2 — Optimization | S1 | Tool output is trimmed to a per-tool field whitelist |
| 3 — Escalation | S2 | Ambiguous “cancel my order” must ASK, not guess |

## How to work

1. **File > Open Folder...** and pick `Week 05/Lab01`.
2. Open `START_HERE.md`.
3. Copy `.env.example` to `.env` and paste your `ANTHROPIC_API_KEY`.
4. Create `.venv`, install, then run `python main.py`.

Demos 1–3 make real Claude API calls. Treat the customer and orders as
fictional — they are mock data, not real PII.

## Why these three together

- **Case facts** fix *memory* (identity survives a long chat).
- **Tool optimize** fixes *budget* (bulky rows never fill the window).
- **Ask-on-ambiguity** fixes *risk* (do not cancel the wrong order).
