"""
Exercise 2 — fixed vs. adaptive task decomposition.

FIXED: the morning threat-intel digest always runs the same three steps,
in the same order, regardless of input — the task's shape is certain.

ADAPTIVE: alert triage classifies the input first, then routes to
whichever specialist playbook matches. The branch SET is still fixed in
code (you decide which playbooks exist) — what's adaptive is WHICH one
runs for this specific input.
"""

import json
import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def ask_claude(system, user, max_tokens, model="claude-haiku-4-5-20251001"):
    """One-shot wrapper around a single Claude call. Used by both styles below."""
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return response.content[0].text.strip()


def _parse_json_array(text):
    """Defensively parse a JSON array, stripping markdown fences if present."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        first_newline = cleaned.find("\n")
        cleaned = cleaned[first_newline + 1 :] if first_newline != -1 else cleaned
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
    cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return []


# --------------------------------------------------------------------------
# FIXED DECOMPOSITION — three hard-coded steps, run in order, every time.
# --------------------------------------------------------------------------

def run_fixed_intel_digest(overnight_feed, asset_inventory):
    """Extract IoCs -> match against NorthGate's assets -> write an exec brief."""
    iocs_raw = ask_claude(
        system=(
            "Extract every indicator of compromise as a JSON list of "
            "{type, value, context} objects where type is one of "
            "ip/hash/domain/cve. Return ONLY the JSON array."
        ),
        user=overnight_feed,
        max_tokens=600,
    )
    iocs = _parse_json_array(iocs_raw)

    matches = ask_claude(
        system=(
            "You are given a list of indicators of compromise and an "
            "asset inventory. List every IoC that matches something "
            "NorthGate owns or uses. One bullet per match. If nothing "
            "matches, say 'No matches against current inventory.'"
        ),
        user=(
            f"IoCs:\n{json.dumps(iocs, indent=2)}\n\n"
            f"Asset inventory:\n{asset_inventory}"
        ),
        max_tokens=400,
    )

    exec_brief = ask_claude(
        system=(
            "Write a three-bullet executive brief for the SOC manager's "
            "08:00 standup. Each bullet must name the asset and the "
            "recommended next action."
        ),
        user=f"IoCs:\n{json.dumps(iocs, indent=2)}\n\nMatches:\n{matches}",
        max_tokens=400,
    )

    return {"iocs": iocs, "matches": matches, "exec_brief": exec_brief}


# --------------------------------------------------------------------------
# ADAPTIVE DECOMPOSITION — classify first, then branch to the right playbook.
# --------------------------------------------------------------------------

TRIAGE_BRANCHES = {
    "phishing": (
        "You are a phishing-response analyst. Playbook: quarantine the "
        "reported email, extract sender/link IoCs, check if other "
        "mailboxes received the same message, and escalate to user "
        "awareness training if a user clicked the link."
    ),
    "malware": (
        "You are a malware-response analyst. Playbook: isolate the "
        "infected host, capture a memory image before remediation, "
        "identify the malware family via hash lookup, and escalate to "
        "Tier-2 if it has command-and-control capability."
    ),
    "lateral_movement": (
        "You are a lateral-movement response analyst. Playbook: map "
        "every host the compromised credential touched, force a "
        "credential reset on all affected accounts, and escalate to the "
        "incident commander if more than 3 hosts are touched."
    ),
    "data_exfiltration": (
        "You are a data-exfiltration response analyst. Playbook: "
        "quantify the volume and destination of the transfer, quarantine "
        "the source host, identify what data classification was "
        "involved, and escalate to legal/compliance if PII or MNPI is "
        "suspected."
    ),
    "brute_force": (
        "You are a brute-force response analyst. Playbook: identify the "
        "targeted account(s) and source IP(s), block the source IP, "
        "force a password reset on any account with successful logins, "
        "and escalate if the account has elevated privileges."
    ),
    "false_positive": (
        "You are a triage analyst closing out a false positive. "
        "Playbook: document why the alert does not represent a real "
        "threat, note any tuning needed to reduce future noise, and "
        "close the ticket."
    ),
}


def classify_alert(alert_text):
    """Classify an alert into exactly one of TRIAGE_BRANCHES' keys."""
    label = ask_claude(
        system=(
            "Classify this security alert into exactly ONE of these "
            "labels: phishing, malware, lateral_movement, "
            "data_exfiltration, brute_force, false_positive. Reply with "
            "ONLY the label, lowercase, nothing else."
        ),
        user=alert_text,
        max_tokens=20,
    ).strip().lower()

    if label not in TRIAGE_BRANCHES:
        label = "false_positive"  # safe default
    return label


def run_adaptive_triage(alert_text):
    """Classify the alert, then run the matching specialist playbook."""
    branch = classify_alert(alert_text)
    answer = ask_claude(
        system=TRIAGE_BRANCHES[branch],
        user=alert_text,
        max_tokens=400,
    )
    return {"branch": branch, "answer": answer}


if __name__ == "__main__":
    print("=" * 70)
    print("FIXED DECOMPOSITION — Morning Threat-Intel Digest")
    print("=" * 70)

    overnight_feed = (
        "Overnight feed summary: New CVE-2027-1188 affects Ivanti VPN "
        "appliances (NorthGate uses Ivanti Connect Secure at the DR "
        "site). Malicious domain update-cdn-delivery[.]net observed "
        "serving a credential-harvesting page impersonating Microsoft "
        "365 login. IP 203.0.113.47 (Singapore, AS65000) flagged by "
        "threat intel as linked to a known data-exfiltration campaign "
        "against financial firms — this matches last night's alert "
        "NG-2027-1142. Hash "
        "d41d8cd98f00b204e9800998ecf8427e observed in a phishing "
        "attachment targeting asset-management firms."
    )
    asset_inventory = (
        "NorthGate asset inventory (partial): Ivanti Connect Secure VPN "
        "appliance at DR site (asset ID VPN-DR-01); Microsoft 365 "
        "tenant for all staff email; external IP allowlist does NOT "
        "include 203.0.113.47; endpoint fleet includes "
        "research-analyst-laptop-04 (Maya Iyer)."
    )

    digest = run_fixed_intel_digest(overnight_feed, asset_inventory)
    print("\n--- Step 1: IoCs ---")
    print(json.dumps(digest["iocs"], indent=2))
    print("\n--- Step 2: Matches against NorthGate assets ---")
    print(digest["matches"])
    print("\n--- Step 3: Executive brief ---")
    print(digest["exec_brief"])

    print("\n" + "=" * 70)
    print("ADAPTIVE DECOMPOSITION — Alert Triage Router")
    print("=" * 70)

    alerts = {
        "NG-2027-1142 (live test alert, data exfiltration)": (
            "Alert ID: NG-2027-1142. Severity: HIGH. Source: EDR "
            "(CrowdStrike Falcon). Asset: research-analyst-laptop-04 "
            "(owner Maya Iyer). Event: outbound transfer of 8.3 GB to "
            "external IP 203.0.113.47 (Singapore, AS65000). Context: "
            "transfer outside business hours, no active VPN session, "
            "owner's badge shows she left the office hours earlier."
        ),
        "phishing report": (
            "Alert: A user on the trading desk reported a suspicious "
            "email claiming to be from IT Support asking them to reset "
            "their Microsoft 365 password via a link to "
            "update-cdn-delivery[.]net. The user did not click the link "
            "but forwarded it to the SOC mailbox."
        ),
        "brute-force password spray": (
            "Alert: SIEM detected 480 failed login attempts against 12 "
            "different VPN accounts from source IP 198.51.100.200 over "
            "the last 20 minutes, followed by one successful login to "
            "the account 'jsmith'."
        ),
    }

    for label, alert_text in alerts.items():
        result = run_adaptive_triage(alert_text)
        print(f"\n--- {label} ---")
        print(f"Routed to branch: {result['branch']}")
        print(f"Specialist response:\n{result['answer']}")
