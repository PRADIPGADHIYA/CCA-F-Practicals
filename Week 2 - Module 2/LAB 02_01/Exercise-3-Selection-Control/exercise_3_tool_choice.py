"""
Exercise 3 — Tool Distribution & Selection Control (S3).

tool_choice scopes what the model may do on a turn:

    {"type": "auto"}                             -> may talk / pick any tool / pick none
    {"type": "any"}                               -> must call SOME tool (model picks which)
    {"type": "tool", "name": "classify_ticket"}   -> must call exactly that tool (deterministic)

A triage step needs to always produce exactly one classification, with
no chit-chat and no drafting. This file runs the same four tickets under
all three modes so you can see which one actually guarantees that.
"""

import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")

CLASSIFY_TOOL = {
    "name": "classify_ticket",
    "description": "Classify a support ticket into exactly one routing category.",
    "input_schema": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "enum": [
                    "order_issue",
                    "product_question",
                    "return_request",
                    "other",
                ],
            },
            "reason": {"type": "string"},
        },
        "required": ["category", "reason"],
    },
}

# A second tool the model can "wander" toward under auto/any, so the three
# modes visibly drift apart from each other.
DRAFT_TOOL = {
    "name": "draft_customer_reply",
    "description": "Draft a free-form customer support reply message.",
    "input_schema": {
        "type": "object",
        "properties": {
            "reply": {"type": "string", "description": "The drafted reply text."}
        },
        "required": ["reply"],
    },
}

TOOLS = [CLASSIFY_TOOL, DRAFT_TOOL]

SYSTEM_PROMPT = (
    "You are a triage assistant for NorthPeak Outfitters. When a new "
    "support ticket arrives, classify it with classify_ticket. If you "
    "think drafting a reply would be more helpful than classifying, you "
    "may use draft_customer_reply instead. You may also just respond "
    "directly in plain text if neither tool seems necessary."
)

TICKETS = [
    "My order NP-100245 never arrived, it's been two weeks!",
    "Do you have any waterproof hiking boots in size 11?",
    "I want to return the tent I bought, it doesn't fit my needs.",
    "Just wanted to say your customer service has been great!",
]

# Step 1 — the three tool_choice modes under test.
MODES = {
    "auto": {"type": "auto"},
    "any": {"type": "any"},
    "FORCED": {"type": "tool", "name": "classify_ticket"},
}


def describe_response(response):
    """Return a short human-readable description of what the model did."""
    tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
    text_blocks = [b for b in response.content if b.type == "text"]

    if tool_use_blocks:
        block = tool_use_blocks[0]
        if block.name == "classify_ticket":
            return f"classify_ticket({block.input}) -- CLEAN CLASSIFICATION", True
        return f"{block.name}({block.input}) -- WRONG TOOL FOR TRIAGE", False

    if text_blocks:
        text = "".join(b.text for b in text_blocks).strip()
        return f"plain text: '{text[:70]}...' -- NO CLASSIFICATION", False

    return "(empty response) -- NO CLASSIFICATION", False


def run_mode(mode_name, tool_choice):
    print(f"\n{'=' * 70}")
    print(f"MODE: {mode_name}  (tool_choice={tool_choice})")
    print("=" * 70)

    clean_count = 0
    for ticket in TICKETS:
        response = client.messages.create(
            model=MODEL,
            max_tokens=300,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            tool_choice=tool_choice,
            messages=[{"role": "user", "content": ticket}],
        )
        description, is_clean = describe_response(response)
        if is_clean:
            clean_count += 1
        print(f"  '{ticket[:55]}...'\n    -> {description}")

    print(f"\n{mode_name} mode: {clean_count}/{len(TICKETS)} tickets got a clean classification")
    return clean_count


if __name__ == "__main__":
    results = {}
    for mode_name, tool_choice in MODES.items():
        results[mode_name] = run_mode(mode_name, tool_choice)

    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print("=" * 70)
    for mode_name, count in results.items():
        print(f"  {mode_name:8}: {count}/{len(TICKETS)} clean classify_ticket calls")
    print(
        "\nOnly FORCED guarantees a classify_ticket call on every single "
        "ticket. auto may skip tools entirely; any guarantees SOME tool "
        "call but may pick draft_customer_reply instead. Use the "
        "narrowest tool_choice that still does the job — force only the "
        "steps that must be deterministic."
    )
