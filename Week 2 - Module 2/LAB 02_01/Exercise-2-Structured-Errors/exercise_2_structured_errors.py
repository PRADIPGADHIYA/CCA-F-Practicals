"""
Exercise 2 — Structured Errors & Retries (S2).

NorthPeak's Orders service is flaky. Transient failures (timeout, 429,
503, etc.) are worth retrying; permanent ones (404, 400) are not. The
core rule: a tool must NEVER raise an exception into the agentic loop —
it always returns a structured envelope so the model (and our own retry
loop) can reason about what happened.

    success -> {"isError": False, ...order fields}
    failure -> {"isError": True, "isRetryable": <bool>, "status": <int>, "error": <msg>}

Run modes:
    python exercise_2_structured_errors.py --check   # offline, no API key needed
    python exercise_2_structured_errors.py            # live agent over 3 failure shapes
"""

import json
import os
import re
import sys
import time

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")

ORDER_ID_PATTERN = re.compile(r"^NP-[0-9]{6}$")

RETRYABLE = {408, 429, 500, 502, 503, 504}

# --------------------------------------------------------------------------
# MOCK ORDERS SERVICE — a deliberately flaky backend.
# --------------------------------------------------------------------------

MOCK_ORDERS = {
    "NP-100245": {
        "order_id": "NP-100245",
        "status": "shipped",
        "items": ["4-Person Tent"],
        "tracking": "1Z999AA10123456784",
    },
    "NP-100311": {
        "order_id": "NP-100311",
        "status": "processing",
        "items": ["Sleeping Bag - Winter"],
        "tracking": None,
    },
    "NP-100190": {
        "order_id": "NP-100190",
        "status": "delivered",
        "items": ["Hiking Boots - Size 10"],
        "tracking": "1Z999AA10123456785",
    },
}

# Orders that fail their first N calls with a scripted status, then start
# succeeding — simulates a transient timeout/503 that clears up on retry.
FAILURE_SCRIPT = {
    "NP-100245": [504],  # 1st call: gateway timeout. 2nd+ call: succeeds.
    "NP-100311": [503],  # used by --check to prove a 503 is retryable.
}

# Orders that always fail, no matter how many times you call them.
ALWAYS_FAIL = {
    "NP-999999": 404,
}

# Tracks how many times orders_service() has been called per order_id, so
# FAILURE_SCRIPT can simulate "fails once, then succeeds."
_call_counts = {}


class ServiceError(Exception):
    """Raised by the raw (unwrapped) orders_service backend."""

    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
        self.message = message


def orders_service(order_id):
    """The raw, flaky backend. Raises ServiceError — call_order_tool wraps this."""
    if not ORDER_ID_PATTERN.match(order_id):
        raise ServiceError(
            400, f"'{order_id}' is not a valid order id (expected format NP-XXXXXX)."
        )

    if order_id in ALWAYS_FAIL:
        raise ServiceError(ALWAYS_FAIL[order_id], f"Order '{order_id}' not found.")

    scripted = FAILURE_SCRIPT.get(order_id, [])
    call_number = _call_counts.get(order_id, 0)
    _call_counts[order_id] = call_number + 1

    if call_number < len(scripted):
        status = scripted[call_number]
        raise ServiceError(
            status,
            f"Orders service returned {status} for '{order_id}' (simulated transient failure).",
        )

    if order_id not in MOCK_ORDERS:
        raise ServiceError(404, f"Order '{order_id}' not found.")

    return dict(MOCK_ORDERS[order_id])


def call_order_tool(order_id):
    """
    Wraps the raw service and converts a ServiceError into a structured
    dict. This function must NEVER raise — every outcome, success or
    failure, comes back as data.
    """
    try:
        data = orders_service(order_id)
        return {"isError": False, **data}
    except ServiceError as err:
        return {
            "isError": True,
            "isRetryable": err.status in RETRYABLE,
            "status": err.status,
            "error": err.message,
        }


def run_with_retry(order_id, max_attempts=4):
    """
    Retry while isRetryable, with exponential backoff, up to max_attempts.
    Stop immediately on a permanent error, or once attempts run out.
    """
    delay = 0.2
    for attempt in range(1, max_attempts + 1):
        result = call_order_tool(order_id)
        if not result["isError"]:
            return result
        if result["isRetryable"] and attempt < max_attempts:
            print(
                f"    attempt {attempt}: {result['status']} (retryable) — "
                f"waiting {delay:.1f}s before retry"
            )
            time.sleep(delay)
            delay *= 2  # exponential backoff
            continue
        return result  # permanent, or out of attempts -> stop
    return result


# --------------------------------------------------------------------------
# STEP 2 — OFFLINE SELF-CHECK (no API key needed)
# --------------------------------------------------------------------------

def run_offline_checks():
    _call_counts.clear()
    print("=" * 70)
    print("OFFLINE SELF-CHECK (no API calls)")
    print("=" * 70)

    print("\n1. A good id that times out once, then succeeds on retry:")
    result = run_with_retry("NP-100245")
    assert result["isError"] is False, "expected NP-100245 to eventually succeed"
    print(f"   OK -> {result}")

    print("\n2. A 404 (not found) must be non-retryable:")
    result = call_order_tool("NP-999999")
    assert result["isError"] is True
    assert result["isRetryable"] is False
    assert result["status"] == 404
    print(f"   OK -> {result}")

    print("\n3. A malformed id (400) must be non-retryable:")
    result = call_order_tool("100245")  # missing the 'NP-' prefix
    assert result["isError"] is True
    assert result["isRetryable"] is False
    assert result["status"] == 400
    print(f"   OK -> {result}")

    print("\n4. A queued 503 must be retryable:")
    result = call_order_tool("NP-100311")
    assert result["isError"] is True
    assert result["isRetryable"] is True
    assert result["status"] == 503
    print(f"   OK -> {result}")

    print("\nAll offline checks passed.")


# --------------------------------------------------------------------------
# STEP 3 — LIVE AGENT over three failure shapes
# --------------------------------------------------------------------------

GET_ORDER_TOOL = {
    "name": "get_order_status",
    "description": (
        "Retrieve the status of an EXISTING customer order by its order "
        "ID (shipping status, items, tracking). Use this whenever the "
        "customer gives an order number. Pass the order id EXACTLY as the "
        "customer typed it — do not reformat, correct, or guess at it "
        "yourself; the tool will report if it is invalid."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "order_id": {
                "type": "string",
                "description": "The order id exactly as given by the customer.",
            }
        },
        "required": ["order_id"],
    },
}

SYSTEM_PROMPT = (
    "You are a NorthPeak Outfitters customer-support agent. When a "
    "customer references an order number, look it up with "
    "get_order_status using the order id exactly as they typed it. If "
    "the tool result is an error: when the order was not found, tell the "
    "customer clearly; when the id format was invalid, ask them to "
    "double-check and resend it in the format NP-XXXXXX. Do not attempt "
    "the tool call again yourself — any retrying already happened before "
    "you saw the result. Keep your reply short and professional."
)


def run_support_ticket(user_message):
    """A minimal agentic loop: one tool (get_order_status), retried via
    run_with_retry, fed back as a tool_result with is_error set."""
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=400,
            system=SYSTEM_PROMPT,
            tools=[GET_ORDER_TOOL],
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            final_text = "".join(
                block.text for block in response.content if block.type == "text"
            )
            print(f"  Agent's final reply:\n  {final_text}")
            return

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use" and block.name == "get_order_status":
                    order_id = block.input.get("order_id")
                    print(f"  -> Agent looked up order_id='{order_id}'")
                    result = run_with_retry(order_id)
                    print(f"  <- Structured result: {result}")
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result),
                            "is_error": bool(result.get("isError")),
                        }
                    )
            messages.append({"role": "user", "content": tool_results})
            continue

        print(f"  Unhandled stop_reason '{response.stop_reason}', stopping.")
        return


def run_live_demo():
    print("=" * 70)
    print("LIVE AGENT — three failure shapes")
    print("=" * 70)

    print("\n--- Case A: transient failure (504 -> retry -> success) ---")
    run_support_ticket("Where is my order NP-100245?")

    print("\n--- Case B: permanent failure, not found (404) ---")
    run_support_ticket("Where is my order NP-999999?")

    print("\n--- Case C: permanent failure, malformed id (400) ---")
    run_support_ticket("Can you check my order? The order number is 100245.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        run_offline_checks()
    else:
        run_live_demo()
