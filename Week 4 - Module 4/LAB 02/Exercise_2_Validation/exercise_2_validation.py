"""Exercise 2 — Schema plus semantic validation.

JSON Schema checks syntax (types, enum, range). Cross-field policy lives
in validate(): strong_hire => score >= 8, no_hire => score <= 4.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
RECS = {"strong_hire", "hire", "no_hire"}


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


def validate(payload):
    """Return (ok: bool, errors: list[str]). Never raise."""
    errors = []
    if not isinstance(payload, dict):
        return False, ["payload is not an object"]

    name = payload.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append("name must be a non-empty string")

    rec = payload.get("recommendation")
    if rec not in RECS:
        errors.append(f"recommendation must be one of {sorted(RECS)}")

    score = payload.get("score")
    is_int = isinstance(score, int) and not isinstance(score, bool)
    if not is_int:
        errors.append("score must be an integer")
    elif not (0 <= score <= 10):
        errors.append("score must be between 0 and 10")

    reason = payload.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        errors.append("reason must be a non-empty string")

    if rec == "strong_hire" and is_int and score < 8:
        errors.append("a 'strong_hire' must score >= 8")
    if rec == "no_hire" and is_int and score > 4:
        errors.append("a 'no_hire' must score <= 4")

    return (len(errors) == 0), errors


EVALUATE_TOOL = {
    "name": "record_evaluation",
    "description": "Record a structured screening evaluation for one job candidate.",
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "recommendation": {"type": "string", "enum": ["strong_hire", "hire", "no_hire"]},
            "score": {"type": "integer", "minimum": 0, "maximum": 10},
            "reason": {"type": "string"},
        },
        "required": ["name", "recommendation", "score", "reason"],
    },
}

CANDIDATES = [
    "Role: Staff Engineer. Dana Lee - 12 years, architected a high-traffic platform, "
    "mentors widely, outstanding system design.",
    "Role: Staff Engineer. Sam Ortiz - 1 year experience, no architecture work, "
    "struggled with the design exercise.",
]


def evaluate(client, candidate):
    msg = client.messages.create(
        model=MODEL, max_tokens=300, tools=[EVALUATE_TOOL],
        tool_choice={"type": "tool", "name": "record_evaluation"},
        messages=[{"role": "user", "content": f"Evaluate this candidate:\n{candidate}"}],
    )
    for block in msg.content:
        if block.type == "tool_use":
            return block.input
    return None


def main():
    client = get_client()
    print(f"Model: {MODEL}")
    for candidate in CANDIDATES:
        payload = evaluate(client, candidate)
        ok, errors = validate(payload)
        print(f"\ncandidate: {candidate[:55]}")
        print("payload:", json.dumps(payload))
        print("valid:", ok, "" if ok else f"-> {errors}")


def check():
    good = {"name": "Dana Lee", "recommendation": "strong_hire", "score": 9,
            "reason": "Deep architecture experience, strong design."}
    bad = {"name": "", "recommendation": "maybe", "score": 12, "reason": "Great."}
    cross = {"name": "Sam Ortiz", "recommendation": "strong_hire", "score": 4,
             "reason": "Limited experience."}
    assert validate(good) == (True, []), validate(good)
    assert validate(bad)[0] is False
    assert validate(cross)[0] is False
    print("offline validation check passed")
    print("bad ->", validate(bad)[1])
    print("cross ->", validate(cross)[1])


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        main()
