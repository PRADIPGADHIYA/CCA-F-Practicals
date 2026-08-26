"""Exercise 3 — Retry-and-feedback loop that self-corrects.

When the validator rejects a payload, feed the error back as a tool_result
with is_error=True so the model can fix it. Cap retries so the loop always
terminates.
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
    errors = []
    if not isinstance(payload, dict):
        return False, ["payload is not an object"]
    if not isinstance(payload.get("name"), str) or not payload.get("name", "").strip():
        errors.append("name must be a non-empty string")
    rec = payload.get("recommendation")
    if rec not in RECS:
        errors.append(f"recommendation must be one of {sorted(RECS)}")
    score = payload.get("score")
    is_int = isinstance(score, int) and not isinstance(score, bool)
    if not is_int or not (0 <= score <= 10):
        errors.append("score must be an integer 0..10")
    if not isinstance(payload.get("reason"), str) or not payload.get("reason", "").strip():
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


def assess_with_retry(client, candidate, max_attempts=3):
    messages = [{"role": "user", "content": f"Evaluate this candidate:\n{candidate}"}]
    last_payload = None
    last_errors = ["no tool call received"]

    for attempt in range(1, max_attempts + 1):
        resp = client.messages.create(
            model=MODEL,
            max_tokens=300,
            tools=[EVALUATE_TOOL],
            tool_choice={"type": "tool", "name": "record_evaluation"},
            messages=messages,
        )
        tool_use = next((b for b in resp.content if b.type == "tool_use"), None)
        if tool_use is None:
            print(f"  attempt {attempt}: no tool_use block")
            last_errors = ["no tool_use block in the response"]
            continue

        last_payload = tool_use.input
        ok, errors = validate(tool_use.input)
        last_errors = errors
        if ok:
            print(f"  attempt {attempt}: valid")
            return tool_use.input, []

        print(f"  attempt {attempt}: invalid -> {errors}")
        messages.append({"role": "assistant", "content": resp.content})
        messages.append({
            "role": "user",
            "content": [{
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "is_error": True,
                "content": (
                    "Validation failed: " + "; ".join(errors)
                    + ". Call record_evaluation again with corrected values."
                ),
            }],
        })

    return last_payload, last_errors


def main():
    client = get_client()
    print(f"Model: {MODEL}")
    candidate = ("Role: Staff Engineer. Alex Park - 10 years, led platform "
                 "re-architecture, excellent design interview, strong references.")
    payload, errors = assess_with_retry(client, candidate)
    print("\nfinal:", json.dumps(payload), "| errors:", errors)


def demo():
    simulated = [
        {"name": "Alex Park", "recommendation": "strong_hire", "score": 5,
         "reason": "Strong all-around."},
        {"name": "Alex Park", "recommendation": "strong_hire", "score": 9,
         "reason": "Led re-architecture, excellent design, strong references."},
    ]
    for attempt, payload in enumerate(simulated, 1):
        ok, errors = validate(payload)
        print(f"attempt {attempt}: {json.dumps(payload)}")
        if ok:
            print("  -> valid, stop")
            break
        print(f"  -> invalid: {errors}")
        print(f"  -> feedback to model: 'Validation failed: {'; '.join(errors)}. "
              f"Call record_evaluation again with corrected values.'")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo()
    else:
        main()
