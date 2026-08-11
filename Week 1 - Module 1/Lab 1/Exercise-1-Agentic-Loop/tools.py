"""
Exercise 1 — Step 1: the "tool" Claude will call.

This simulates a ticket classification engine. In a real system this
function would call a trained model or a rules engine. For this lab we
just pick a random value for each requested field so we can focus on the
mechanics of the agentic loop (Exercise 1's real subject) instead of on
classification accuracy.
"""

import random

PRODUCT_AREAS = ["Billing", "Platform", "Integrations", "Security", "Onboarding"]
SEVERITIES = ["P1-Critical", "P2-High", "P3-Medium", "P4-Low"]
INTENTS = ["Bug", "Question", "Feature Request", "Billing Dispute"]

# Maps each supported field name to the list of values it can take.
_FIELD_VOCABULARY = {
    "product_area": PRODUCT_AREAS,
    "severity": SEVERITIES,
    "intent": INTENTS,
}


def classify_ticket(ticket_text: str, fields_needed: list) -> dict:
    """
    Return a dict containing a value for every field named in fields_needed.

    Args:
        ticket_text: the raw text of the support ticket.
        fields_needed: which of "product_area", "severity", "intent" to fill in.

    Returns:
        A dict with exactly the requested keys, each mapped to one value
        drawn from that field's vocabulary above.
    """
    # ticket_text isn't used for real classification here (it's simulated),
    # but a real implementation would inspect it to choose values.
    _ = ticket_text

    result = {}
    for field in fields_needed:
        choices = _FIELD_VOCABULARY.get(field)
        if choices is None:
            raise ValueError(
                f"Unknown field '{field}'. Expected one of {list(_FIELD_VOCABULARY)}."
            )
        result[field] = random.choice(choices)
    return result
