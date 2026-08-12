"""
Exercise 1 — Tool Interfaces (S1).

Proves that tool-selection reliability is an INTERFACE problem, not a
model-size problem: the exact same model is run over a weak toolset and
a strong toolset against the same six support questions. The harness
forces a tool call with tool_choice={"type": "any"} so we are measuring
WHICH tool gets picked, not whether one gets picked at all.
"""

import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Every exercise reads its model from ANTHROPIC_MODEL so nothing is
# hard-coded; defaults to a Sonnet model per the lab spec.
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")

# --------------------------------------------------------------------------
# WEAK TOOLSET — vague names, overlapping descriptions, loose parameters.
# This gives the model nothing to disambiguate on.
# --------------------------------------------------------------------------

WEAK_TOOLS = [
    {
        "name": "search",
        "description": "Search for stuff in the system.",
        "input_schema": {
            "type": "object",
            "properties": {
                "q": {"type": "string", "description": "query"},
            },
            "required": ["q"],
        },
    },
    {
        "name": "lookup",
        "description": "Look up information.",
        "input_schema": {
            "type": "object",
            "properties": {
                "q": {"type": "string", "description": "query"},
            },
            "required": ["q"],
        },
    },
]

# --------------------------------------------------------------------------
# STRONG TOOLSET — object+action names, explicit when/when-NOT-to-use
# descriptions that defer to the sibling tool, and typed/constrained
# parameters (the order id is validated against a regex pattern).
# --------------------------------------------------------------------------

STRONG_TOOLS = [
    {
        "name": "search_products",
        "description": (
            "Search the NorthPeak product CATALOG for items we sell (tents, "
            "sleeping bags, stoves, boots, etc.) by free-text query. Use this "
            "for availability, price, or whether a product exists. Do NOT use "
            "this to check something a customer already bought — for an "
            "existing purchase use get_order_status instead."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Free-text product query, e.g. '4 person tent'.",
                },
                "max_results": {"type": "integer", "minimum": 1, "maximum": 10},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_order_status",
        "description": (
            "Retrieve the status of an EXISTING customer order by its order "
            "ID (shipping status, items, tracking). Use this whenever the "
            "customer gives an order number or references a purchase. Do NOT "
            "use this to browse the catalog — for products use "
            "search_products instead."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "Order ID in the format 'NP-XXXXXX'.",
                    "pattern": "^NP-[0-9]{6}$",
                },
            },
            "required": ["order_id"],
        },
    },
]

# --------------------------------------------------------------------------
# TEST CASES — six realistic support questions, each tagged with which
# KIND of task it is ("catalog" or "order"). This is the ground truth the
# harness scores against.
# --------------------------------------------------------------------------

TEST_CASES = [
    ("Do you carry a four-person tent?", "catalog"),
    ("Where is my order NP-100245?", "order"),
    ("What sleeping bags do you have for winter camping?", "catalog"),
    ("Can you check the status of order NP-100311?", "order"),
    ("Do you sell hiking boots in size 10?", "catalog"),
    ("I placed order NP-100190 last week, has it shipped yet?", "order"),
]

# Which tool name counts as "correct" for each kind, per toolset. The weak
# toolset's names are deliberately ambiguous — "search" is treated as the
# catalog-shaped tool and "lookup" as the order-shaped tool, but the weak
# descriptions give the model no real signal to land on that mapping
# reliably, which is exactly the point of this exercise.
WEAK_EXPECTED = {"catalog": "search", "order": "lookup"}
STRONG_EXPECTED = {"catalog": "search_products", "order": "get_order_status"}


def run_harness(tools, expected_map, label):
    """
    Run every TEST_CASES question against `tools`, forcing a tool call with
    tool_choice={"type": "any"}, and score how often the picked tool matches
    expected_map[kind]. Prints OK/MISS per question and a final total.
    """
    print(f"\n{'=' * 70}")
    print(f"{label} — forcing a tool call on each question")
    print("=" * 70)

    correct = 0
    for question, kind in TEST_CASES:
        response = client.messages.create(
            model=MODEL,
            max_tokens=300,
            tools=tools,
            tool_choice={"type": "any"},
            messages=[{"role": "user", "content": question}],
        )

        tool_use = next(
            (block for block in response.content if block.type == "tool_use"), None
        )
        picked = tool_use.name if tool_use else "(no tool_use block)"
        expected = expected_map[kind]

        if picked == expected:
            correct += 1
            print(f"  OK   [{kind:8}] '{question}' -> {picked}")
        else:
            print(
                f"  MISS [{kind:8}] '{question}' -> got '{picked}', expected '{expected}'"
            )

    print(f"\n{label} score: {correct}/{len(TEST_CASES)}")
    return correct


if __name__ == "__main__":
    weak_score = run_harness(WEAK_TOOLS, WEAK_EXPECTED, "WEAK TOOLSET")
    strong_score = run_harness(STRONG_TOOLS, STRONG_EXPECTED, "STRONG TOOLSET")

    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print("=" * 70)
    print(f"Weak toolset:   {weak_score}/{len(TEST_CASES)} correct")
    print(f"Strong toolset: {strong_score}/{len(TEST_CASES)} correct")
    print(
        "\nSame model, same six questions — only the tool interface changed. "
        "Any gap between these two scores is the interface's fault, not the "
        "model's."
    )
