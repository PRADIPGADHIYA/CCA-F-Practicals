"""
main.py — Lab 5.3: Trust & Traceability for a financial report reviewer.

Run with:
    python main.py

Offline check (no API key needed):
    python main.py --check

The script:
  1. Loads a small mock financial report.
  2. Runs TWO independent review passes with different prompts.
  3. Buckets the findings into auto_clear / human_review / contested.
  4. Prints every finding with its source line and quote (provenance).

The three lab TODOs are already filled in (you do not need to write Python):

  DEMO 1  ->  confidence.py : bucket() routes by CONFIDENCE_THRESHOLD
  DEMO 2  ->  reviewer.py   : tolerant JSON parse + local quote attachment
  DEMO 3  ->  main.py       : two independent passes, then bucket
"""

import os
import sys

from dotenv import load_dotenv

from sample_report import get_numbered_report, get_quote
from reviewer import _attach_quotes, _parse_json_array, review
from confidence import bucket, CONFIDENCE_THRESHOLD

# Windows consoles default to cp1252; force UTF-8 so the report's em-dashes
# and ellipses render instead of showing as "?" boxes.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()


def print_bucket(title: str, items: list[dict], show_disagreement: bool = False):
    print("\n" + title)
    print("-" * len(title))
    if not items:
        print("(none)")
        return
    for item in items:
        if show_disagreement:
            print(
                f"  line {item['line']:>2} : \"{item['quote']}\"\n"
                f"          pass A flag: {item['flag_pass_a']}\n"
                f"          pass B flag: {item['flag_pass_b']}"
            )
        else:
            print(
                f"  line {item['line']:>2} : \"{item['quote']}\"\n"
                f"          flag={item['flag']}  "
                f"confidence={item['confidence']}"
            )


def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit(
            "Set ANTHROPIC_API_KEY first (copy .env.example to .env).\n"
            "Or run without a key:  python main.py --check"
        )

    report_text = get_numbered_report()
    print("=" * 70)
    print("REPORT UNDER REVIEW")
    print("=" * 70)
    print(report_text)

    print("\nRunning pass A (strict reviewer)…")
    pass_a = review(report_text, mode="strict")
    print(f"  -> {len(pass_a)} finding(s)")
    print("Running pass B (general reviewer)…")
    pass_b = review(report_text, mode="general")
    print(f"  -> {len(pass_b)} finding(s)")
    buckets = bucket(pass_a, pass_b)

    print("\n" + "=" * 70)
    print(f"RESULTS  (confidence threshold = {CONFIDENCE_THRESHOLD})")
    print("=" * 70)
    print_bucket("AUTO-CLEAR (confirmed, high confidence)", buckets["auto_clear"])
    print_bucket("HUMAN REVIEW (low confidence)", buckets["human_review"])
    print_bucket("CONTESTED (the two passes disagreed)",
                 buckets["contested"], show_disagreement=True)

    print("\nDone. Every finding above includes its source line — that's the")
    print("provenance a human reviewer needs to verify in one click.")


def check_offline() -> None:
    """Verify Demo 1-3 logic without calling the Claude API."""
    print("=" * 70)
    print("OFFLINE CHECK (no API calls)")
    print("=" * 70)

    print("\nDemo 2 — parse fenced JSON and attach quotes from OUR report:\n")
    raw = """```json
[
  {"line": 4, "flag": "unusual_change_without_disclosure", "confidence": 0.92},
  {"line": 9, "flag": "missing_related_party_disclosure", "confidence": 0.60},
  {"line": 99, "flag": "hallucinated_line", "confidence": 0.99}
]
```"""
    parsed = _parse_json_array(raw)
    cleaned = _attach_quotes(parsed)
    assert len(parsed) == 3
    assert len(cleaned) == 2, cleaned
    assert all(item["quote"] == get_quote(item["line"]) for item in cleaned)
    assert 99 not in {item["line"] for item in cleaned}
    for item in cleaned:
        print(f"  line {item['line']:>2} | {item['flag']}")
        print(f"         quote: \"{item['quote']}\"")
    print("  dropped line 99 (out of range -> unverifiable)")
    assert _parse_json_array("not json at all") == []

    print("\nDemo 1+3 — bucket two passes (confirm / contest / threshold):\n")

    def finding(line: int, flag: str, conf: float) -> dict:
        return {
            "line": line,
            "quote": get_quote(line),
            "flag": flag,
            "confidence": conf,
        }

    pass_a = [
        finding(4, "unusual_change_without_disclosure", 0.92),
        finding(7, "vague_risk_language", 0.55),
        finding(9, "missing_related_party_disclosure", 0.80),
    ]
    pass_b = [
        finding(4, "unusual_change_without_disclosure", 0.90),
        finding(7, "vague_risk_language", 0.50),
    ]
    buckets = bucket(pass_a, pass_b)

    print_bucket("AUTO-CLEAR (confirmed, high confidence)", buckets["auto_clear"])
    print_bucket("HUMAN REVIEW (low confidence)", buckets["human_review"])
    print_bucket("CONTESTED (the two passes disagreed)",
                 buckets["contested"], show_disagreement=True)

    assert [item["line"] for item in buckets["auto_clear"]] == [4]
    assert buckets["auto_clear"][0]["confidence"] == 0.91
    assert [item["line"] for item in buckets["human_review"]] == [7]
    assert buckets["human_review"][0]["confidence"] == 0.53
    assert [item["line"] for item in buckets["contested"]] == [9]
    assert buckets["contested"][0]["flag_pass_a"] == "missing_related_party_disclosure"
    assert buckets["contested"][0]["flag_pass_b"] is None

    print("\nOffline check passed.")
    print("Next: copy .env.example to .env and run:  python main.py")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check_offline()
    else:
        main()
