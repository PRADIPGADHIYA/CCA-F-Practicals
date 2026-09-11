"""Exercise 1 — Classify a workload with the Message Batches API.

Submit many requests, poll until processing_status == "ended", collect
results by custom_id. Re-fetch later with --fetch <batch_id>.
"""

from __future__ import annotations

import os
import sys
import time
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
    "Helix Robotics beats earnings expectations, shares jump 12%.",
    "Regulators open probe into Helix Robotics data practices.",
    "Helix Robotics names new chief financial officer.",
    "Analysts downgrade Helix Robotics on slowing growth.",
    "Helix Robotics unveils new warehouse automation line.",
    "Helix Robotics quarterly revenue comes in line with estimates.",
    "Lawsuit alleges safety defects in Helix Robotics products.",
    "Helix Robotics partners with major retailer for nationwide rollout.",
]

PROMPT = ("Classify the sentiment of this news headline toward the company as "
          "exactly one of: positive, neutral, negative. One word.\n\n"
          "Headline: {h}")


def build_requests(headlines):
    return [
        {
            "custom_id": f"headline-{i}",
            "params": {
                "model": MODEL,
                "max_tokens": 20,
                "messages": [{"role": "user", "content": PROMPT.format(h=h)}],
            },
        }
        for i, h in enumerate(headlines)
    ]


def fetch_results(client, batch_id):
    for entry in client.messages.batches.results(batch_id):
        if entry.result.type == "succeeded":
            text = "".join(b.text for b in entry.result.message.content
                           if b.type == "text").strip()
            print(f"{entry.custom_id}: {text}")
        else:
            print(f"{entry.custom_id}: ERROR ({entry.result.type})")


def main():
    client = get_client()
    print(f"Model: {MODEL}")

    batch = client.messages.batches.create(requests=build_requests(HEADLINES))
    print("submitted batch:", batch.id, "| status:", batch.processing_status)

    deadline = time.time() + 600  # wait up to 10 minutes in this demo
    while True:
        batch = client.messages.batches.retrieve(batch.id)
        print("status:", batch.processing_status, "| counts:", batch.request_counts)
        if batch.processing_status == "ended":
            break
        if time.time() > deadline:
            print("Still processing. Fetch later with --fetch", batch.id)
            print(f"  python exercise_1_message_batches.py --fetch {batch.id}")
            return
        time.sleep(10)

    print("\nResults:")
    fetch_results(client, batch.id)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--fetch":
        fetch_results(get_client(), sys.argv[2])
    else:
        main()
