"""
Exercise 1 — Step 2: the agentic loop.

This loop calls Claude repeatedly until the model itself signals it is
done (stop_reason == "end_turn"), executing the classify_ticket tool
along the way whenever Claude asks for it (stop_reason == "tool_use").

Run this file directly:
    python loop.py
"""

import json
import os

from anthropic import Anthropic
from dotenv import load_dotenv

from tools import classify_ticket

# Loads ANTHROPIC_API_KEY from a local .env file (see .env.example).
load_dotenv()

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

MODEL = "claude-haiku-4-5-20251001"

# The same test ticket is reused across all four exercises in this lab.
TEST_TICKET = (
    "From: sarah.chen@globalcorp.com\n"
    "Subject: Cannot access SSO login — entire team locked out\n\n"
    "Our team of 40 has been unable to log in via SSO since 09:00 this "
    "morning. We have a client demo in 3 hours. This is completely "
    "blocking us."
)

# The tool schema Claude uses to decide when/how to call classify_ticket.
tools = [
    {
        "name": "classify_ticket",
        "description": (
            "Classify a support ticket. Call this as many times as needed, "
            "requesting only the fields you still need, until product_area, "
            "severity, and intent have all been confirmed."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ticket_text": {
                    "type": "string",
                    "description": "The full raw text of the support ticket to classify.",
                },
                "fields_needed": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Which classification fields to return in this call. "
                        "Valid values: 'product_area', 'severity', 'intent'."
                    ),
                },
            },
            "required": ["ticket_text", "fields_needed"],
        },
    }
]

# Maps tool names to the Python functions that implement them.
TOOL_FUNCTIONS = {"classify_ticket": classify_ticket}

messages = [
    {
        "role": "user",
        "content": (
            "Classify the following support ticket completely. You must "
            "determine all three fields: product_area, severity, and "
            "intent. Use the classify_ticket tool as many times as "
            "necessary until all three fields are confirmed — do not guess "
            "the values yourself, only trust values returned by the tool. "
            "Once you have all three fields, respond with a final summary "
            "of the classification and stop.\n\n"
            f"Ticket:\n{TEST_TICKET}"
        ),
    }
]

iteration = 0
while True:
    iteration += 1

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        tools=tools,
        messages=messages,
    )

    print(f"\n--- Iteration {iteration} | stop_reason = {response.stop_reason} ---")

    # MANDATORY and must come first: append the assistant turn before any
    # branching. If you append tool results first, the messages array
    # becomes malformed and the next API call will error.
    messages.append({"role": "assistant", "content": response.content})

    if response.stop_reason == "end_turn":
        final_text = "".join(
            block.text for block in response.content if block.type == "text"
        )
        print("\nFinal classification result:\n")
        print(final_text)
        break

    if response.stop_reason == "tool_use":
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"  -> Calling tool '{block.name}' with input: {block.input}")
                function = TOOL_FUNCTIONS[block.name]
                result = function(**block.input)
                print(f"  <- Tool result: {result}")
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result),
                    }
                )
        messages.append({"role": "user", "content": tool_results})
        continue

    if response.stop_reason == "max_tokens":
        print("Warning: response was cut off at the token limit. Stopping.")
        break

    # "stop_sequence" or any other value: treat like end_turn for this lab.
    print(f"Unhandled stop_reason '{response.stop_reason}', stopping.")
    break
