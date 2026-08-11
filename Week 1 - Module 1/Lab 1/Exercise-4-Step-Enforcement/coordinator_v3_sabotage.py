"""
Exercise 4 — Step 3: prove the gate actually blocks execution.

Identical to coordinator_v3.py, except immediately after the Classifier
writes its results into ctx, we deliberately wipe ctx.severity back to
None. This should cause Gate 1 to raise PipelineGateError right away,
naming "severity" as the missing field, and steps 2-4 must never run.

Run this file directly:
    python coordinator_v3_sabotage.py
"""

from context import TicketContext
from gates import PipelineGateError, gate_classification, gate_draft, gate_enrichment
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

    try:
        print("=== Step 1: Classifier ===")
        classification = run_classifier(ctx.raw_ticket)
        ctx.product_area = classification["product_area"]
        ctx.severity = classification["severity"]
        ctx.intent = classification["intent"]
        print(classification)

        # --- SABOTAGE: deliberately blank out a required field ---
        ctx.severity = None
        print("(sabotage) ctx.severity manually reset to None")

        gate_classification(ctx)  # this must raise PipelineGateError
        print("Gate 1 passed: classification complete.")

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

        gate_enrichment(ctx)
        print("Gate 2 passed: enrichment complete.")

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

        gate_draft(ctx)
        print("Gate 3 passed: draft complete.")

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

    except PipelineGateError as exc:
        print(f"\n[PIPELINE BLOCKED] {exc}")


if __name__ == "__main__":
    main()
