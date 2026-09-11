# LAB 03 — Batch Processing & Multi-Pass Review (Lab 4.3)

Helix Robotics media-monitoring pipeline. Three **separate** projects.
You do **not** need to write Python — each TODO from the lab PDF is filled in.

**All three exercises make real API calls.** There is no offline mode.

| Folder | Exercise | Pattern | Job it fits |
|---|---|---|---|
| `Exercise_1_Message_Batches` | Ex 1 (~15 min) | Message Batches API | Overnight bulk (cheap, slow) |
| `Exercise_2_Parallel` | Ex 2 (~15 min) | Thread pool | Breaking-news burst (fast) |
| `Exercise_3_Multipass` | Ex 3 (~15 min) | Draft → critique → refine | Morning briefing (quality) |

## How to work

1. **File > Open Folder...** and pick **one** exercise folder.
2. Open `START_HERE.md`.
3. Copy `.env.example` to `.env` and paste `ANTHROPIC_API_KEY`.

Exercise 1 can take several minutes. If it times out:

```powershell
python exercise_1_message_batches.py --fetch <batch_id>
```

## Why these three together

- **Batches** save money when you can wait.
- **Threads** save time when you cannot wait.
- **Multi-pass** raises quality when one shot is not enough.

Mixing them up wastes time or money (for example, putting breaking news
through a batch that finishes after the story has moved on).
