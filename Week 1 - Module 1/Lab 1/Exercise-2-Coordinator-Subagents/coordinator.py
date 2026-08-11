"""
Exercise 2 — Step 2: the coordinator.

Calls the four subagents in strict sequence — Classifier -> CRM Enricher
-> Drafter -> Validator — and prints each output. The coordinator owns
all state: it explicitly passes the output of each step into the next
step that needs it. Subagents never share memory with each other.

Run this file directly:
    python coordinator.py
"""

from subagents import run_classifier, run_crm_enricher, run_drafter, run_validator

TEST_TICKET = (
    "From: sarah.chen@globalcorp.com\n"
    "Subject: Cannot access SSO login — entire team locked out\n\n"
    "Our team of 40 has been unable to log in via SSO since 09:00 this "
    "morning. We have a client demo in 3 hours. This is completely "
    "blocking us."
)
CUSTOMER_EMAIL = "sarah.chen@globalcorp.com"


def main():
    print("=== Step 1: Classifier ===")
    classification = run_classifier(TEST_TICKET)
    print(classification)

    print("\n=== Step 2: CRM Enricher ===")
    crm_data = run_crm_enricher(CUSTOMER_EMAIL, classification)
    print(crm_data)

    print("\n=== Step 3: Drafter ===")
    draft = run_drafter(TEST_TICKET, classification, crm_data)
    print(draft)

    print("\n=== Step 4: Validator ===")
    verdict = run_validator(draft, classification, crm_data)
    print(verdict)


if __name__ == "__main__":
    main()
