"""Exercise 3 — Generalizing beyond the examples shown.

Examples teach the FORMAT. A short PRINCIPLES block teaches the BOUNDARY
so context-heavy reports the examples never showed still route correctly.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from anthropic import Anthropic

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")

# Read the action off the 'ACTION | rationale' line even if there is a preamble.
ACTION_RE = re.compile(r"\b(REMOVE|REVIEW|ALLOW)\b\s*\|", re.IGNORECASE)


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


EDGE_CASES = [
    ("A user posted a company's official public press-office phone number.",
     "allow", "public/official info is not doxxing"),
    ("A user shared a private individual's home address 'as a joke'.",
     "remove", "doxxing regardless of stated intent"),
    ("Two friends in a gaming thread joke 'I'll destroy you' about a match.",
     "review", "ambiguous threat in playful context needs a human"),
    ("A member posted a long, dull but on-topic essay nobody asked for.",
     "allow", "boring is not a violation"),
]

EXAMPLES = """Report: A user posted another member's home address and employer.
REMOVE | Doxxing - exposes private personal data with no reasonable doubt.

Report: A member said a popular opinion was "totally wrong and lazy".
ALLOW | Blunt criticism of an idea, not a policy violation.

Report: A thread has escalating personal insults between two users.
REVIEW | Possible harassment that needs a human judgment call."""

PRINCIPLES = """- REMOVE only for unambiguous violations: exposure of a PRIVATE person's
  data (doxxing), credible threats, or clearly illegal content. Stated
  intent ("just a joke") does not excuse doxxing.
- Already-public or official info (a company's press line) is not doxxing — ALLOW.
- REVIEW anything genuinely ambiguous: possible jokes, spam, escalating disputes.
- ALLOW speech that is merely rude, blunt, unpopular, boring, or off-topic.
- When unsure between REMOVE and REVIEW, choose REVIEW."""

PROMPT = (
    "Decide the moderation action (REMOVE, REVIEW, or ALLOW). "
    "Respond in exactly this format: 'ACTION | rationale'.\n\n"
    "Principles:\n" + PRINCIPLES + "\n\nExamples:\n" + EXAMPLES + "\n\nReport: {report}"
)


def predict(client, report):
    msg = client.messages.create(
        model=MODEL, max_tokens=60,
        messages=[{"role": "user", "content": PROMPT.format(report=report)}],
    )
    out = "".join(b.text for b in msg.content if b.type == "text").strip()
    m = ACTION_RE.search(out)
    action = m.group(1).lower() if m else out.split("|")[0].strip().lower()
    return action, out


def main():
    client = get_client()
    print(f"Model: {MODEL}")
    correct = 0
    for report, expected, nuance in EDGE_CASES:
        action, out = predict(client, report)
        ok = action == expected
        correct += ok
        print(f"\n[{'OK ' if ok else 'XX '}] expected={expected} (tests: {nuance})")
        print(f"      {out}")
    print(f"\n--> {correct}/{len(EDGE_CASES)} edge cases generalized correctly")


if __name__ == "__main__":
    main()
