"""Exercise 2 — Parallel processing for throughput.

I/O-bound API waits overlap in a thread pool. Compare sequential vs
parallel wall-clock time. Tune workers to your rate limits (too many => 429).
"""

from __future__ import annotations

import os
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")


def load_env() -> None:
    """Load KEY=value pairs from a local .env file (Windows-friendly)."""
    path = Path(__file__).resolve().parent / ".env"
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def get_client():
    from anthropic import Anthropic
    load_env()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("Set ANTHROPIC_API_KEY first (copy .env.example to .env).")
    return Anthropic()


HEADLINES = [
    "Helix Robotics beats earnings expectations, shares jump.",
    "Regulators open probe into Helix Robotics data practices.",
    "Helix Robotics names new chief financial officer.",
    "Analysts downgrade Helix Robotics on slowing growth.",
    "Helix Robotics unveils new warehouse automation line.",
    "Helix Robotics quarterly revenue in line with estimates.",
    "Lawsuit alleges safety defects in Helix Robotics products.",
    "Helix Robotics partners with major retailer for rollout.",
]

PROMPT = ("Classify sentiment toward the company as one of: positive, neutral, "
          "negative. One word.\n\nHeadline: {h}")


def classify(client, headline):
    msg = client.messages.create(
        model=MODEL, max_tokens=20,
        messages=[{"role": "user", "content": PROMPT.format(h=headline)}],
    )
    return "".join(b.text for b in msg.content if b.type == "text").strip()


def run_sequential(client, headlines):
    t0 = time.time()
    out = [classify(client, h) for h in headlines]
    return out, time.time() - t0


def run_parallel(client, headlines, workers=5):
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        # .map preserves input order, so results line up with headlines.
        out = list(pool.map(lambda h: classify(client, h), headlines))
    return out, time.time() - t0


def main():
    client = get_client()
    print(f"Model: {MODEL}")

    seq, seq_t = run_sequential(client, HEADLINES)
    print(f"\nSequential: {seq_t:.1f}s -> {seq}")

    par, par_t = run_parallel(client, HEADLINES, workers=5)
    print(f"Parallel  : {par_t:.1f}s -> {par}")

    if par_t > 0:
        print(f"\nSpeedup: {seq_t / par_t:.1f}x")
    print("\nTip: tune `workers` to your rate limits — too many will hit 429s.")


if __name__ == "__main__":
    main()
