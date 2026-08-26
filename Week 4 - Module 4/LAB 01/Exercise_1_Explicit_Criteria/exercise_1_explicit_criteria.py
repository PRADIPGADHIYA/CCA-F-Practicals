"""Exercise 1 — Explicit criteria to cut false positives.

Same model, two prompts. A vague prompt lets REMOVE over-fire (wrongful
takedowns). The explicit prompt defines each action and uses a tie-break.
"""

from __future__ import annotations

import os
from pathlib import Path

from anthropic import Anthropic

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
    load_env()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("Set ANTHROPIC_API_KEY first (copy .env.example to .env).")
    return Anthropic()


# Eight labeled reports. `gold` is the correct action for scoring.
REPORTS = [
    ("A user posted another member's home address and workplace without consent.", "remove"),
    ("A member wrote a credible threat of violence naming a specific user.", "remove"),
    ("A post shares a screenshot exposing a private person's phone number.", "remove"),
    ("A member called someone's argument 'completely stupid' during a debate.", "allow"),
    ("A user disagreed strongly but politely with a moderator's decision.", "allow"),
    ("A slightly off-topic reply in a discussion thread.", "allow"),
    ("A user keeps posting the same 'Buy crypto here!' link in every thread.", "review"),
    ("Several members report a heated but on-topic political argument.", "review"),
]

VAGUE_PROMPT = """Decide the moderation action for this reported post: remove, review, or allow.

Report: {report}

Answer with one word only."""


EXPLICIT_PROMPT = """Decide the moderation action for this reported post.
Choose the action using these exact definitions:

- remove: a clear, unambiguous violation — doxxing or exposure of private
  personal data, a credible threat against a specific person, or clearly
  illegal content. Reserve this for cases with no reasonable doubt.
- review: may violate policy but needs a human — likely spam, borderline
  harassment, ambiguous threats said in jest, heated arguments.
- allow: rude, blunt, off-topic, or unpopular but not a violation.

If unsure between remove and review, choose review — do not remove unless
the violation is unambiguous.

Report: {report}

Answer with one word only: remove, review, or allow."""


def classify(client, prompt_template, report):
    msg = client.messages.create(
        model=MODEL, max_tokens=10,
        messages=[{"role": "user", "content": prompt_template.format(report=report)}],
    )
    text = "".join(b.text for b in msg.content if b.type == "text").strip().lower()
    for label in ("remove", "review", "allow"):
        if label in text:
            return label
    return text


def score(client, label, prompt):
    print(f"\n=== {label} ===")
    correct = false_removes = 0
    for report, gold in REPORTS:
        pred = classify(client, prompt, report)
        ok = pred == gold
        correct += ok
        if pred == "remove" and gold != "remove":
            false_removes += 1
        print(f"[{'OK ' if ok else 'XX '}] gold={gold:6} pred={pred:6} | {report[:48]}")
    print(f"--> accuracy {correct}/{len(REPORTS)}, wrongful 'remove' calls: {false_removes}")


def main():
    client = get_client()
    print(f"Model: {MODEL}")
    score(client, "VAGUE prompt", VAGUE_PROMPT)
    score(client, "EXPLICIT prompt", EXPLICIT_PROMPT)


if __name__ == "__main__":
    main()
