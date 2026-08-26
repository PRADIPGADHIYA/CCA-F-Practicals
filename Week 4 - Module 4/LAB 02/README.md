# LAB 02 — Enforcing Structure (Lab 4.2)

Recruiting screen: every candidate becomes
`{name, recommendation, score, reason}`. Three **separate** projects.
You do **not** need to write Python — each TODO from the lab PDF is filled in.

| Folder | Exercise | What you practice | Needs API? |
|---|---|---|---|
| `Exercise_1_Tool_Schema` | Ex 1 (~15 min) | Tool schema + `tool_choice` forces a typed object | Yes |
| `Exercise_2_Validation` | Ex 2 (~15 min) | `validate()` for cross-field policy | `--check` no / live yes |
| `Exercise_3_Retry_Loop` | Ex 3 (~15 min) | Feed errors back via `tool_result`, capped | `--demo` no / live yes |

## How to work

1. **File > Open Folder...** and pick **one** exercise folder.
2. Open `START_HERE.md`.
3. For live runs, copy `.env.example` to `.env` and paste `ANTHROPIC_API_KEY`.

Offline first (recommended):

```powershell
python exercise_2_validation.py --check
python exercise_3_retry_loop.py --demo
```

## Why these three together

- **Schema** fixes the *shape* (typed object every time).
- **Validator** fixes the *meaning* (`strong_hire` cannot score 5).
- **Retry loop** fixes the *failure* (show the error; bound the attempts).
