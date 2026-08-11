"""
Exercise 3 — session state: save / resume / fork / summarize.

A session is a plain dict: {id, parent_id, messages, summary}. Every
operation below is a plain function, and sessions are stored as JSON
files under ./sessions/ so any analyst can open the file and read
exactly what the agent remembers.
"""

import json
import os
import uuid

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

MODEL = "claude-haiku-4-5-20251001"

# Absolute path so this works no matter which directory you run the
# script from.
SESSIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions")


def new_session():
    """Return a fresh session dict with a new short id."""
    return {
        "id": uuid.uuid4().hex[:6],
        "parent_id": None,
        "messages": [],
        "summary": "",
    }


def add_user(session, text):
    """Append a user turn to the session's running history."""
    session["messages"].append({"role": "user", "content": text})


def add_assistant(session, text):
    """Append an assistant turn to the session's running history."""
    session["messages"].append({"role": "assistant", "content": text})


def save_session(session):
    """Write the session as JSON to SESSIONS_DIR/<id>.json. Returns the path."""
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    path = os.path.join(SESSIONS_DIR, f"{session['id']}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(session, f, indent=2)
    print(
        f"Saved session '{session['id']}' "
        f"({len(session['messages'])} messages) -> {path}"
    )
    return path


def resume_session(session_id):
    """Load a session back from disk. Raises FileNotFoundError if missing."""
    path = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"No saved session with id '{session_id}' found at {path}. "
            "Check the id, or run save_session() first."
        )
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def fork_session(parent):
    """
    Return a new session that COPIES parent's messages — never a shared
    reference. Using parent['messages'] directly (instead of
    list(parent['messages'])) would make both branches alias the same
    list, silently merging them the moment either branch adds a message.
    """
    child = new_session()
    child["messages"] = list(parent["messages"])  # copy, never alias
    child["summary"] = parent["summary"]
    child["parent_id"] = parent["id"]
    return child


def summarize_session(session, keep_recent=2):
    """
    Compress older messages into a structured DECISIONS/FACTS/OPEN digest,
    keeping only the most recent `keep_recent` messages verbatim. Concrete
    values (IPs, hostnames, usernames, hashes, alert IDs, legal-hold IDs)
    must never be dropped — losing them is worse than not summarizing.
    """
    messages = session["messages"]
    if len(messages) <= keep_recent:
        return session  # nothing old enough to be worth summarizing

    older = messages[:-keep_recent]
    recent = messages[-keep_recent:]

    transcript = "\n".join(f"[{m['role'].upper()}] {m['content']}" for m in older)

    digest = client.messages.create(
        model=MODEL,
        max_tokens=500,
        system=(
            "You are summarizing a SOC investigation transcript. Output "
            "EXACTLY three sections, in this order: 'DECISIONS:', "
            "'FACTS:', 'OPEN:'. Under each, use short bullet points. "
            "Never drop concrete values — IP addresses, hostnames, "
            "usernames, file hashes, alert IDs, and legal-hold IDs must "
            "all be preserved verbatim in the digest."
        ),
        messages=[{"role": "user", "content": transcript}],
    ).content[0].text.strip()

    session["summary"] = digest
    session["messages"] = recent
    return session


if __name__ == "__main__":
    print("=" * 70)
    print("DEMO 1 — Save & Resume (shift change)")
    print("=" * 70)

    s = new_session()
    add_user(
        s,
        "Day 1, 02:47 EST — Alert NG-2027-1142 assigned to Sarah Chen "
        "(Tier-1, night shift). Host research-analyst-laptop-04 (owner "
        "Maya Iyer) transferred 8.3 GB to external IP 203.0.113.47 "
        "(Singapore, AS65000) outside business hours.",
    )
    add_assistant(
        s,
        "SIEM query result: no other hosts show outbound transfers to "
        "203.0.113.47. Badge swipe data: Maya Iyer left the office at "
        "18:22 EST, well before the 02:47 transfer. Leading hypotheses: "
        "(1) credential theft / external APT using a stolen session, "
        "(2) insider exfiltration via a scheduled/automated transfer.",
    )
    path = save_session(s)
    saved_id = s["id"]
    del s  # simulate the shift ending — nothing left in memory

    print(f"\n(shift change — session only exists on disk at {path})\n")

    resumed = resume_session(saved_id)
    print(f"Day 2, 08:00 EST — Mike Torres (Tier-2) resumes session '{resumed['id']}'")
    print(f"Messages recovered: {len(resumed['messages'])}")
    for m in resumed["messages"]:
        print(f"  [{m['role']}] {m['content'][:90]}...")

    print("\n" + "=" * 70)
    print("DEMO 2 — Fork (parallel hypotheses)")
    print("=" * 70)

    branch_insider = fork_session(resumed)
    add_user(
        branch_insider,
        "Branch A — insider-threat hypothesis: pulled HR records for "
        "Maya Iyer. Found a voluntary resignation notice filed 3 days "
        "before the transfer, effective in 2 weeks.",
    )
    save_session(branch_insider)

    branch_apt = fork_session(resumed)
    add_user(
        branch_apt,
        "Branch B — external-APT hypothesis: captured a memory image of "
        "research-analyst-laptop-04. Process tree shows a persistence "
        "mechanism (scheduled task 'WinUpdateCheck') created 2 days "
        "before the transfer, not present in the gold image.",
    )
    save_session(branch_apt)

    print(
        f"\nBranch A id={branch_insider['id']} parent_id={branch_insider['parent_id']} "
        f"messages={len(branch_insider['messages'])}"
    )
    print(
        f"Branch B id={branch_apt['id']} parent_id={branch_apt['parent_id']} "
        f"messages={len(branch_apt['messages'])}"
    )
    print(
        f"Both branches share parent_id '{resumed['id']}' but have "
        f"diverged: Branch A has {len(branch_insider['messages'])} "
        f"messages, Branch B has {len(branch_apt['messages'])} messages "
        "(each includes only its own new evidence, not the other "
        "branch's)."
    )

    print("\n" + "=" * 70)
    print("DEMO 3 — Summarize (bound the memory footprint)")
    print("=" * 70)

    long_session = new_session()
    evidence_turns = [
        "Memory image captured from research-analyst-laptop-04, SHA256 "
        "hash: 3b1f5c9e2a7d4e6f8b0c1a2d3e4f5061728394a5b6c7d8e9f0a1b2c3d4e5f60.",
        "Quarantine decision: host research-analyst-laptop-04 isolated "
        "from network at 08:14 EST per Tier-2 lead Mike Torres.",
        "Legal notified. Legal-hold ID L-2027-44 opened for all evidence "
        "related to alert NG-2027-1142.",
        "HR confirmed Maya Iyer's resignation notice, filed 3 days "
        "prior, case number HR-2027-0912.",
        "Network capture shows destination IP 203.0.113.47 resolves to "
        "ASN AS65000, geolocated Singapore, no prior NorthGate traffic "
        "to this range in the last 90 days.",
        "Process tree analysis: scheduled task 'WinUpdateCheck' created "
        "2 days before the transfer, executes powershell.exe with a "
        "base64-encoded payload.",
        "Credential audit: Maya Iyer's VPN credentials show no failed "
        "login attempts in the last 30 days — inconsistent with brute "
        "force, consistent with either insider access or a stolen "
        "session token.",
        "Case status update: escalated to the incident commander for a "
        "decision on law-enforcement notification given the legal hold.",
    ]
    for i, turn in enumerate(evidence_turns):
        if i % 2 == 0:
            add_user(long_session, turn)
        else:
            add_assistant(long_session, turn)

    print(f"Session built with {len(long_session['messages'])} messages.")
    summarize_session(long_session, keep_recent=2)

    print(
        f"\nAfter summarization: {len(long_session['messages'])} messages "
        "kept verbatim."
    )
    print("\n--- Digest (session['summary']) ---")
    print(long_session["summary"])

    print("\n--- Recent messages kept verbatim ---")
    for m in long_session["messages"]:
        print(f"  [{m['role']}] {m['content']}")
