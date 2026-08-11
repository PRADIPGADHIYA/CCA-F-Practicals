"""
Exercise 1 — Step 1: the hook engine.

Pure Python, no API key required — this module runs entirely on its own.
A hook is just a function with signature (tool_name, tool_input) ->
(allowed: bool, reason: str). Hooks run BETWEEN the model's decision (a
tool_use block) and the actual side-effect. If any hook returns
allowed=False, the real tool never runs.
"""

import ipaddress

# Hostnames that must never be quarantined (or have accounts disabled)
# without dual approval: trading servers, market-data relays, exec laptops.
PROTECTED_HOSTS = [
    "trading-prod-01",
    "trading-prod-02",
    "market-data-relay-01",
    "market-data-relay-02",
    "ceo-laptop-01",
    "cfo-laptop-01",
]

# IP addresses that must never be added to the firewall deny-list.
PROTECTED_IPS = [
    "198.51.100.10",  # Reuters market-data feed
    "198.51.100.11",  # Bloomberg terminal
    "192.0.2.55",  # prime-broker API
    "192.0.2.56",  # clearing-house webhook
]


def logging_hook(tool_name, tool_input):
    """LOG: observes every call, never blocks."""
    print(f"  [LOG] tool='{tool_name}' args={list(tool_input.keys())}")
    return True, ""


def arg_validation_hook(tool_name, tool_input):
    """VALIDATE: rejects malformed arguments before they reach the tool."""
    if tool_name == "block_ip":
        ip = tool_input.get("ip")
        if not ip:
            return False, "block_ip requires an 'ip' argument"
        try:
            ipaddress.IPv4Address(ip)
        except ValueError:
            return False, f"'{ip}' is not a valid IPv4 address"
        return True, ""

    if tool_name == "quarantine_host":
        if not tool_input.get("hostname"):
            return False, "quarantine_host requires a 'hostname' argument"
        return True, ""

    if tool_name == "disable_user":
        if not tool_input.get("username"):
            return False, "disable_user requires a 'username' argument"
        return True, ""

    return True, ""


def protected_asset_hook(tool_name, tool_input):
    """BLOCK: enforces policy on NorthGate's protected assets."""
    if tool_name == "quarantine_host":
        hostname = tool_input.get("hostname", "")
        for protected in PROTECTED_HOSTS:
            if protected in hostname:
                return (
                    False,
                    f"'{hostname}' matches PROTECTED_HOSTS entry '{protected}' "
                    "— quarantine forbidden without dual approval",
                )
        return True, ""

    if tool_name == "block_ip":
        ip = tool_input.get("ip", "")
        if ip in PROTECTED_IPS:
            return (
                False,
                f"'{ip}' is in PROTECTED_IPS — this feed/API must never be blocked",
            )
        return True, ""

    if tool_name == "disable_user":
        username = tool_input.get("username", "").lower()
        exec_accounts = {"ceo", "cfo", "ciso"}
        if username in exec_accounts or username.endswith("@northgate-exec"):
            return (
                False,
                f"'{username}' is an executive account — disabling requires dual approval",
            )
        return True, ""

    return True, ""


def _sim_block_ip(tool_input):
    return f"[Firewall] IP {tool_input.get('ip')} added to deny-list (simulated)"


def _sim_quarantine_host(tool_input):
    return f"[EDR] Host {tool_input.get('hostname')} isolated from network (simulated)"


def _sim_disable_user(tool_input):
    return f"[IAM] User {tool_input.get('username')} disabled (simulated)"


def _sim_query_siem(tool_input):
    return f"[SIEM] Query '{tool_input.get('query')}' returned 3 matching events (simulated)"


# Maps tool names to the (simulated) function that performs the real
# side-effect. In production these would call real EDR / firewall / IAM /
# SIEM APIs.
DEMO_TOOLS = {
    "block_ip": _sim_block_ip,
    "quarantine_host": _sim_quarantine_host,
    "disable_user": _sim_disable_user,
    "query_siem": _sim_query_siem,
}


def run_tool(tool_name, tool_input, tool_fn, hooks, audit_log):
    """
    Route a tool call through every hook, in order, BEFORE the real tool
    ever runs.

    On the first hook that returns allowed=False: append a BLOCKED entry
    to audit_log, print the block, and return a "BLOCKED by policy: ..."
    string — the real tool function is never called.

    If every hook passes: append an 'allowed' entry to audit_log and
    return tool_fn(tool_input).
    """
    for hook in hooks:
        allowed, reason = hook(tool_name, tool_input)
        if not allowed:
            audit_log.append(
                {
                    "tool": tool_name,
                    "input": tool_input,
                    "status": "BLOCKED",
                    "reason": reason,
                }
            )
            print(f"  [BLOCK] {tool_name}({tool_input}) -> {reason}")
            return f"BLOCKED by policy: {reason}"

    audit_log.append(
        {
            "tool": tool_name,
            "input": tool_input,
            "status": "allowed",
            "reason": "",
        }
    )
    return tool_fn(tool_input)


def print_audit_log(audit_log):
    """Print a numbered trace of every attempt — the SOX / SOC2 record."""
    print("\n=== AUDIT LOG (SOX / SOC2 record) ===")
    for i, entry in enumerate(audit_log, start=1):
        status = entry["status"]
        reason = f" — {entry['reason']}" if entry["reason"] else ""
        print(f"{i}. [{status}] {entry['tool']}({entry['input']}){reason}")


if __name__ == "__main__":
    hooks = [logging_hook, arg_validation_hook, protected_asset_hook]
    audit_log = []

    attempts = [
        # ALLOWED: quarantine the suspicious analyst laptop from the live test alert.
        ("quarantine_host", {"hostname": "research-analyst-laptop-04"}),
        # POLICY BLOCK: an attacker-pivot precaution on a protected trading server.
        ("quarantine_host", {"hostname": "trading-prod-01"}),
        # ARG-VALIDATION BLOCK: a malformed IP address.
        ("block_ip", {"ip": "not-an-ip"}),
        # ARG-VALIDATION BLOCK: an empty username.
        ("disable_user", {"username": ""}),
        # EXEC-ACCOUNT BLOCK: disabling the CEO requires dual approval.
        ("disable_user", {"username": "ceo"}),
        # ALLOWED: a normal SIEM query.
        ("query_siem", {"query": "outbound transfer > 5GB last 24h"}),
    ]

    for tool_name, tool_input in attempts:
        print(f"\nAttempting: {tool_name}({tool_input})")
        result = run_tool(tool_name, tool_input, DEMO_TOOLS[tool_name], hooks, audit_log)
        print(f"  -> result: {result}")

    print_audit_log(audit_log)
