"""
Exercise 2 — Step 1: the four specialist subagents.

Each function below makes exactly ONE Claude API call and returns its
result. Subagents share NO memory with each other or with the
coordinator — each one only knows what is explicitly passed to it as
arguments. This is the "hub-and-spoke" pattern: the coordinator
(coordinator.py) owns all state and decides what each subagent sees.
"""

import json
import os
import random

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Subagents use a fast, cost-efficient model for focused, single-purpose
# tasks. The coordinator itself does not call the API in this exercise —
# it is plain Python orchestration (see coordinator.py).
MODEL = "claude-haiku-4-5-20251001"


def _strip_code_fences(text: str) -> str:
    """Remove ```/```json markdown fences that Claude sometimes wraps JSON in."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        first_newline = cleaned.find("\n")
        cleaned = cleaned[first_newline + 1 :] if first_newline != -1 else cleaned
        if cleaned.endswith("```"):
            cleaned = cleaned[: -3]
    return cleaned.strip()


def run_classifier(ticket: str) -> dict:
    """Classify a ticket into product_area, severity, and intent."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        system=(
            "You are a support ticket classifier. Classify the ticket into "
            "exactly these three fields:\n"
            "- product_area: one of Billing, Platform, Integrations, Security, Onboarding\n"
            "- severity: one of P1-Critical, P2-High, P3-Medium, P4-Low\n"
            "- intent: one of Bug, Question, Feature Request, Billing Dispute\n"
            "Respond ONLY with a JSON object with keys product_area, severity, "
            "intent. No markdown fences, no extra commentary."
        ),
        messages=[{"role": "user", "content": ticket}],
    )
    raw_text = "".join(block.text for block in response.content if block.type == "text")
    cleaned = _strip_code_fences(raw_text)
    return json.loads(cleaned)


def run_crm_enricher(customer_email: str, classification: dict) -> dict:
    """
    Simulate a CRM lookup for the customer's account.

    In production this would call a real CRM API, likely via an MCP tool.
    For this lab it returns a hardcoded/randomised dict so we can focus on
    how the coordinator wires subagent outputs together.
    """
    _ = classification  # not needed for the simulated lookup itself
    return {
        "account_tier": random.choice(["Enterprise", "Growth", "Starter"]),
        "sla_tier": random.choice(["Gold", "Silver", "Bronze"]),
        "account_manager": "Jordan Ellis",
        "contract_value": random.choice([25000, 60000, 120000, 250000]),
        "customer_email": customer_email,
    }


def run_drafter(ticket: str, classification: dict, crm: dict) -> str:
    """Draft a professional first-response email referencing the SLA tier."""
    context = (
        f"Ticket:\n{ticket}\n\n"
        f"Classification: {json.dumps(classification)}\n\n"
        f"CRM data: {json.dumps(crm)}"
    )
    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        system=(
            "You are a customer support drafter. Using the ticket, "
            "classification, and CRM data provided, write a professional, "
            "empathetic first-response email. It must reference the correct "
            "product area and the customer's SLA tier. Keep it concise and "
            "ready for a human reviewer to send or edit."
        ),
        messages=[{"role": "user", "content": context}],
    )
    return "".join(block.text for block in response.content if block.type == "text")


def run_validator(draft: str, classification: dict, crm: dict) -> str:
    """Check product area, SLA match, and tone. Reply APPROVED or list issues."""
    context = (
        f"Draft response:\n{draft}\n\n"
        f"Expected product area: {classification.get('product_area')}\n"
        f"Expected SLA tier: {crm.get('sla_tier')}\n"
        f"Expected account tier: {crm.get('account_tier')}"
    )
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        system=(
            "You are a quality validator for customer support responses. "
            "Confirm the draft references the correct product area, matches "
            "the customer's SLA tier, and has a professional tone suitable "
            "for the account tier given. Reply with exactly 'APPROVED' if "
            "everything checks out, otherwise list the specific issues "
            "found, one per line."
        ),
        messages=[{"role": "user", "content": context}],
    )
    return "".join(block.text for block in response.content if block.type == "text")
