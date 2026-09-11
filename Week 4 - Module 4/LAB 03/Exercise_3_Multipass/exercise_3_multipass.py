"""Exercise 3 — Multi-pass review for higher quality.

Draft -> critique -> refine. Critique lists issues only (does not rewrite).
Refine applies every point and returns only the briefing text.
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


HEADLINES = [
    "Helix Robotics beats earnings expectations, shares jump 12%.",
    "Regulators open probe into Helix Robotics data practices.",
    "Analysts downgrade Helix Robotics on slowing growth.",
    "Helix Robotics partners with major retailer for nationwide rollout.",
    "Lawsuit alleges safety defects in Helix Robotics products.",
]

STANDARDS = (
    "Briefing standards: lead with the single most important development; balance "
    "positive and negative coverage fairly; be specific (numbers, who/what); stay "
    "neutral in tone; no speculation beyond the headlines; keep it under 120 words."
)


def ask(client, prompt, max_tokens=500):
    msg = client.messages.create(
        model=MODEL, max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in msg.content if b.type == "text").strip()


def draft(client, headlines):
    joined = "\n".join(f"- {h}" for h in headlines)
    return ask(client, f"Write a short morning media briefing from today's "
                       f"headlines about Helix Robotics:\n{joined}")


def critique(client, headlines, draft_text):
    joined = "\n".join(f"- {h}" for h in headlines)
    prompt = (
        f"{STANDARDS}\n\n"
        f"Headlines:\n{joined}\n\n"
        f"Draft briefing:\n{draft_text}\n\n"
        "Critique the draft against the standards above. List specific, actionable "
        "problems as short bullets (e.g. buries the regulatory probe, omits the "
        "12% figure, too long, leans positive). Do NOT rewrite — only list issues."
    )
    return ask(client, prompt)


def refine(client, headlines, draft_text, critique_text):
    joined = "\n".join(f"- {h}" for h in headlines)
    prompt = (
        f"{STANDARDS}\n\n"
        f"Headlines:\n{joined}\n\n"
        f"Draft briefing:\n{draft_text}\n\n"
        f"Critique to address:\n{critique_text}\n\n"
        "Rewrite the briefing so it fixes every point in the critique and meets the "
        "standards. Output only the final briefing text."
    )
    return ask(client, prompt)


def main():
    client = get_client()
    print(f"Model: {MODEL}\n")

    d = draft(client, HEADLINES)
    print("--- DRAFT ---\n" + d)

    c = critique(client, HEADLINES, d)
    print("\n--- CRITIQUE ---\n" + c)

    f = refine(client, HEADLINES, d, c)
    print("\n--- REFINED ---\n" + f)


if __name__ == "__main__":
    main()
