"""Exercise 2 — Few-shot examples to lock consistent output.

Instructions alone give inconsistent shapes. Three labeled examples pin
casing, the "|" separator, and a one-sentence rationale.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from anthropic import Anthropic

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
FORMAT_RE = re.compile(r"^(REMOVE|REVIEW|ALLOW) \| .+")


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


REPORTS = [
    "A user posted screenshots of a member's private messages and real name.",
    "A member wrote 'your take is garbage' in a design critique thread.",
    "Repeated identical affiliate links posted across ten threads in a minute.",
    "Two users trading sarcastic jabs that are getting more personal.",
]

INSTRUCTION = (
    "Decide the moderation action (REMOVE, REVIEW, or ALLOW) and give one short "
    "rationale. Respond in exactly this format: 'ACTION | rationale'."
)

ZERO_SHOT = INSTRUCTION + "\n\nReport: {report}"

FEW_SHOT_EXAMPLES = """Report: A user posted another member's home address and employer.
REMOVE | Doxxing - exposes private personal data with no reasonable doubt.

Report: A member said a popular opinion was "totally wrong and lazy".
ALLOW | Blunt criticism of an idea, not a policy violation.

Report: A thread has escalating personal insults between two users.
REVIEW | Possible harassment that needs a human judgment call."""

FEW_SHOT = INSTRUCTION + "\n\nExamples:\n" + FEW_SHOT_EXAMPLES + "\n\nReport: {report}"


def run(client, label, prompt):
    print(f"\n=== {label} ===")
    compliant = 0
    for report in REPORTS:
        msg = client.messages.create(
            model=MODEL, max_tokens=60,
            messages=[{"role": "user", "content": prompt.format(report=report)}],
        )
        out = "".join(b.text for b in msg.content if b.type == "text").strip()
        ok = bool(FORMAT_RE.match(out))
        compliant += ok
        print(f"[{'OK ' if ok else 'XX '}] {out!r}")
    print(f"--> {compliant}/{len(REPORTS)} matched the exact format")


def main():
    client = get_client()
    print(f"Model: {MODEL}")
    run(client, "ZERO-SHOT", ZERO_SHOT)
    run(client, "FEW-SHOT", FEW_SHOT)


if __name__ == "__main__":
    main()
