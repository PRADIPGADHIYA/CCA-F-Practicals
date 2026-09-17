"""
main.py - Lab 5.1: Managing Context for an E-commerce Support Agent.

This file runs THREE clearly labeled demos:

  DEMO 1  Case facts survive across many turns.
  DEMO 2  Bulky tool outputs get optimized down to relevant fields.
  DEMO 3  Ambiguous user requests trigger a clarifying question.

The three lab TODOs are already filled in (you do not need to write Python):

  DEMO 1  ->  case_facts.py : as_system_block()   (render the pinned facts)
  DEMO 2  ->  tool_optimizer.py : optimize()      (trim tool output)
  DEMO 3  ->  main.py : SYSTEM_BASE               (the ASK-on-ambiguity rule)

The chat loop, tool dispatch, and demos are provided - read them top to bottom.

Offline check (no API key needed):

  python main.py --check
"""

import json
import os
import sys

# Windows consoles default to cp1252, which crashes on characters the model
# may emit. Force UTF-8 so the lab runs everywhere.
sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
from anthropic import Anthropic

from case_facts import CaseFacts
from tool_optimizer import optimize
from sample_data import (
    get_customer,
    get_orders_for_customer,
    get_open_orders_for_customer,
)

load_dotenv()
MODEL_NAME = os.getenv("MODEL_NAME", "claude-haiku-4-5-20251001")


def get_client():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit(
            "Set ANTHROPIC_API_KEY first (copy .env.example to .env).\n"
            "Or run without a key:  python main.py --check"
        )
    return Anthropic()


TOOLS = [
    {
        "name": "lookup_orders",
        "description": ("Return the list of orders for the current customer. "
                        "Each order has order_id, status, placed_on and total."),
        "input_schema": {
            "type": "object",
            "properties": {"customer_id": {"type": "string"}},
            "required": ["customer_id"],
        },
    },
    {
        "name": "get_order_details",
        "description": "Return the full details of a single order by id.",
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    },
]

# Demo 3 — Escalation, plus Demo 1's authority rule.
# If the request is ambiguous, ASK instead of guessing. Treat [CASE FACTS]
# as confirmed so the agent does not re-ask for values already pinned there.
SYSTEM_BASE = (
    "You are a helpful support agent for an online retail company. "
    "Be concise. If a request is ambiguous (e.g. the customer has multiple "
    "open orders and didn't specify which), ASK a clarifying question "
    "instead of guessing. Always rely on the [CASE FACTS] block — those "
    "values are authoritative and you do not need to ask for them again."
)


def run_tool(name: str, args: dict) -> str:
    """Execute a tool, optimize the result, return JSON for the model."""
    if name == "lookup_orders":
        raw = get_orders_for_customer(args["customer_id"])
    elif name == "get_order_details":
        from sample_data import ORDERS
        raw = ORDERS.get(args["order_id"]) or {}
    else:
        raw = {"error": f"unknown tool {name}"}

    trimmed = optimize(name, raw)
    return json.dumps(trimmed)


def chat(client, messages: list, facts: CaseFacts) -> str:
    """Send messages + current case facts; resolve any tool calls; return reply text."""
    system_prompt = SYSTEM_BASE
    facts_block = facts.as_system_block()
    if facts_block:
        system_prompt = system_prompt + "\n\n" + facts_block

    while True:
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=1024,
            system=system_prompt,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"   [tool call] {block.name}({block.input})")
                    result_str = run_tool(block.name, block.input)
                    print(f"   [optimized result] {result_str}")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_str,
                    })
            messages.append({"role": "user", "content": tool_results})
            continue

        text = "".join(b.text for b in response.content if b.type == "text")
        messages.append({"role": "assistant", "content": text})
        return text


def demo_1_case_facts(client):
    print("\n" + "=" * 70)
    print("DEMO 1: Case facts survive long sessions")
    print("=" * 70)

    facts = CaseFacts()
    customer = get_customer("C-1001")
    facts.set("customer_id", customer["customer_id"])
    facts.set("customer_name", customer["name"])
    facts.set("tier", customer["tier"])

    messages = []
    turns = [
        "Hi, what are your store hours?",
        "Do you ship to Hyderabad?",
        "What payment methods do you accept?",
        "Quick check: what is my customer ID and what tier am I?",
    ]
    for user_msg in turns:
        print(f"\nUSER : {user_msg}")
        messages.append({"role": "user", "content": user_msg})
        reply = chat(client, messages, facts)
        print(f"AGENT: {reply}")


def demo_2_tool_optimization(client):
    print("\n" + "=" * 70)
    print("DEMO 2: Bulky tool output is trimmed before it reaches the model")
    print("=" * 70)

    facts = CaseFacts()
    facts.set("customer_id", "C-1001")

    raw = get_orders_for_customer("C-1001")
    trimmed = optimize("lookup_orders", raw)
    print("\nRAW tool output (what a naive agent would paste):")
    print(json.dumps(raw, indent=2))
    print("\nOPTIMIZED output (what actually reaches the model):")
    print(json.dumps(trimmed, indent=2))

    print("\nNow let the agent actually use it ↓")
    messages = [{"role": "user", "content": "List my orders, just status and total."}]
    reply = chat(client, messages, facts)
    print(f"AGENT: {reply}")


def demo_3_escalate_ambiguity(client):
    print("\n" + "=" * 70)
    print("DEMO 3: Ambiguous request triggers a clarifying question")
    print("=" * 70)

    facts = CaseFacts()
    facts.set("customer_id", "C-1001")

    open_orders = get_open_orders_for_customer("C-1001")
    print(f"\nCustomer has {len(open_orders)} open orders: "
          f"{[o['order_id'] for o in open_orders]}")
    print("They are about to say 'cancel my order' without specifying which.")
    print("A good agent must ASK, not guess.\n")

    messages = [{"role": "user", "content": "Please cancel my order."}]
    reply = chat(client, messages, facts)
    print(f"AGENT: {reply}")
    print("\n^ Notice the agent asked which order rather than picking one.")


def check_offline() -> None:
    """Verify Demo 1 + Demo 2 logic without calling the Claude API."""
    print("=" * 70)
    print("OFFLINE CHECK (no API calls)")
    print("=" * 70)

    empty = CaseFacts()
    assert empty.as_system_block() == "", "empty store should render as ''"

    facts = CaseFacts()
    customer = get_customer("C-1001")
    facts.set("customer_id", customer["customer_id"])
    facts.set("customer_name", customer["name"])
    facts.set("tier", customer["tier"])
    block = facts.as_system_block()
    print("\n[CASE FACTS] block that will be pinned on every turn:\n")
    print(block)
    assert "[CASE FACTS" in block
    assert "C-1001" in block
    assert "Gold" in block
    assert "Aarti Sharma" in block

    raw = get_orders_for_customer("C-1001")
    trimmed = optimize("lookup_orders", raw)
    print("\nRAW lookup_orders size:      ", len(json.dumps(raw)), "chars")
    print("OPTIMIZED lookup_orders size:", len(json.dumps(trimmed)), "chars")
    print("\nOPTIMIZED rows:")
    print(json.dumps(trimmed, indent=2))
    assert isinstance(trimmed, list) and len(trimmed) == 3
    for row in trimmed:
        assert set(row.keys()) <= {"order_id", "status", "placed_on", "total"}
        assert "customer_id" not in row
        assert "items" not in row

    details = optimize("get_order_details", raw[0])
    assert "items" in details
    assert optimize("unknown_tool", {"keep": "me"}) == {"keep": "me"}

    open_orders = get_open_orders_for_customer("C-1001")
    print("\nOpen orders (Demo 3 must ASK which one):",
          [o["order_id"] for o in open_orders])
    assert "ASK" in SYSTEM_BASE.upper()
    assert "CASE FACTS" in SYSTEM_BASE
    print("\nSYSTEM_BASE includes ASK-on-ambiguity and [CASE FACTS] authority.")
    print("\nOffline check passed. Next: copy .env.example to .env and run:")
    print("  python main.py")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check_offline()
    else:
        client = get_client()
        demo_1_case_facts(client)
        demo_2_tool_optimization(client)
        demo_3_escalate_ambiguity(client)
        print("\nAll demos done. Read the printed output above to see the techniques in action.")
