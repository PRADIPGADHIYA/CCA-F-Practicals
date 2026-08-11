"""
Exercise 3 — Step 1: the TicketContext dataclass.

A typed context object that travels through the whole pipeline. It is
self-documenting, enforces required fields at construction time (a
missing required field raises TypeError immediately — a loud Python-level
failure instead of a silent, wrong Claude answer), and exposes helper
methods that make partial-completion state explicit.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class TicketContext:
    # --- Required at intake: no defaults, must be provided at construction ---
    ticket_id: str
    raw_ticket: str
    customer_email: str

    # --- Populated by Classifier ---
    product_area: Optional[str] = None
    severity: Optional[str] = None
    intent: Optional[str] = None

    # --- Populated by CRM Enricher ---
    account_tier: Optional[str] = None
    sla_tier: Optional[str] = None
    account_manager: Optional[str] = None

    # --- Populated by Drafter and Validator ---
    draft_response: Optional[str] = None
    validation_result: Optional[str] = None

    def classification_complete(self) -> bool:
        """True only if product_area, severity, and intent are all set."""
        return all(
            value is not None
            for value in (self.product_area, self.severity, self.intent)
        )

    def enrichment_complete(self) -> bool:
        """True only if account_tier and sla_tier are both set."""
        return self.account_tier is not None and self.sla_tier is not None

    def draft_complete(self) -> bool:
        """True only if draft_response has been set."""
        return self.draft_response is not None


if __name__ == "__main__":
    # Quick manual proof that missing required fields fail loudly.
    try:
        TicketContext(ticket_id="TCK-1")  # missing raw_ticket, customer_email
    except TypeError as exc:
        print("Constructing with missing required fields failed as expected:")
        print(f"  TypeError: {exc}")
