"""
Exercise 3 — Step 2: coordinator refactored to use TicketContext.

Same Classifier -> CRM Enricher -> Drafter -> Validator sequence as
Exercise 2, but now all pipeline state lives on a single typed
TicketContext object. Each subagent still only receives the specific
fields it needs — never the whole ctx object — keeping the hub-and-spoke
memory isolation from Exercise 2 intact.

Run this file directly:
    python coordinator_v2.py
"""

from context import TicketContext
from subagents import run_classifier, run_crm_enricher, run_drafter, run_validator

TEST_TICKET = (
    "From: sarah.chen@globalcorp.com\n"
    "Subject: Cannot access SSO login — entire team locked out\n\n"
    "Our team of 40 has been unable to log in via SSO since 09:00 this "
    "morning. We have a client demo in 3 hours. This is completely "
    "blocking us."
)


def main():
    ctx = TicketContext(
        ticket_id="TCK-1001",
        raw_ticket=TEST_TICKET,
        customer_email="sarah.chen@globalcorp.com",
    )

    print("=== Step 1: Classifier ===")
    classification = run_classifier(ctx.raw_ticket)
    ctx.product_area = classification["product_area"]
    ctx.severity = classification["severity"]
    ctx.intent = classification["intent"]
    print(classification)

    print("\n=== Step 2: CRM Enricher ===")
    crm_data = run_crm_enricher(
        ctx.customer_email,
        {
            "product_area": ctx.product_area,
            "severity": ctx.severity,
            "intent": ctx.intent,
        },
    )
    ctx.account_tier = crm_data["account_tier"]
    ctx.sla_tier = crm_data["sla_tier"]
    ctx.account_manager = crm_data["account_manager"]
    print(crm_data)

    print("\n=== Step 3: Drafter ===")
    draft = run_drafter(
        ctx.raw_ticket,
        {
            "product_area": ctx.product_area,
            "severity": ctx.severity,
            "intent": ctx.intent,
        },
        {
            "account_tier": ctx.account_tier,
            "sla_tier": ctx.sla_tier,
            "account_manager": ctx.account_manager,
        },
    )
    ctx.draft_response = draft
    print(draft)

    print("\n=== Step 4: Validator ===")
    verdict = run_validator(
        ctx.draft_response,
        {
            "product_area": ctx.product_area,
            "severity": ctx.severity,
            "intent": ctx.intent,
        },
        {"account_tier": ctx.account_tier, "sla_tier": ctx.sla_tier},
    )
    ctx.validation_result = verdict
    print(verdict)

    print("\n=== Final TicketContext ===")
    print(ctx)


if __name__ == "__main__":
    main()
