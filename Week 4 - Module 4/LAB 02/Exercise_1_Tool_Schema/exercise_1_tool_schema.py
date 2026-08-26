"""Exercise 1 — Force structured output with tool_use + JSON Schema.

Asking the model to "return JSON" in prose is unreliable. Defining the
target object as a tool's input_schema and forcing tool_choice means the
tool arguments ARE the structured object.
"""

from __future__ import annotations

import json
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


CANDIDATES = [
    "Role: Senior Backend Engineer. Maya Chen - 8 years Python/Go, led a 6-person "
    "team, scaled a payments system to 1M users, strong system-design answers.",
    "Role: Senior Backend Engineer. Tom Ruiz - bootcamp grad, 1 year support "
    "engineering, two small portfolio apps, no backend production experience.",
    "Role: Data Analyst. Priya Nair - 4 years SQL and dashboards, solid "
    "stakeholder communication, some Python, no ML background.",
]

EVALUATE_TOOL = {
    "name": "record_evaluation",
    "description": "Record a structured screening evaluation for one job candidate.",
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Candidate name."},
            "recommendation": {
                "type": "string",
                "enum": ["strong_hire", "hire", "no_hire"],
                "description": "Screening recommendation.",
            },
            "score": {
                "type": "integer",
                "minimum": 0,
                "maximum": 10,
                "description": "Overall fit, 0 (poor) to 10 (excellent).",
            },
            "reason": {"type": "string", "description": "One-sentence justification."},
        },
        "required": ["name", "recommendation", "score", "reason"],
    },
}


def evaluate(client, candidate):
    msg = client.messages.create(
        model=MODEL, max_tokens=300, tools=[EVALUATE_TOOL],
        tool_choice={"type": "tool", "name": "record_evaluation"},
        messages=[{"role": "user", "content": f"Evaluate this candidate:\n{candidate}"}],
    )
    for block in msg.content:
        if block.type == "tool_use":
            return block.input  # this IS the structured object
    return None


def main():
    client = get_client()
    print(f"Model: {MODEL}")
    for candidate in CANDIDATES:
        payload = evaluate(client, candidate)
        print(f"\ncandidate: {candidate[:55]}...")
        print("structured:", json.dumps(payload))


if __name__ == "__main__":
    main()
