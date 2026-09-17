"""
main.py - Lab 5.2: Resilient Claims Processing Pipeline.

The coordinator walks each claim through three subagents:

    intake  ->  validation  ->  adjudication

What this demonstrates:
  * Errors propagate cleanly - every stage returns a StageResult and the
    coordinator decides how to react. No silent drops.
  * A scratchpad records every finding for audit + crash recovery.
  * Re-running skips claims already in `done` or `failed` state.

Run with:
    python main.py

Offline check (no API key needed):
    python main.py --check

To see crash recovery: press Ctrl+C mid-run, then run again.
To reset: delete `scratchpad.json` and run again.

The three lab TODOs are already filled in (you do not need to write Python):

  DEMO 1  ->  agents.py     : three subagents return StageResult, never raise
  DEMO 2  ->  scratchpad.py : log / mark_done / mark_failed / _flush
  DEMO 3  ->  main.py       : process_claim() + skip done/failed claims
"""

import json
import os
import sys
from pathlib import Path

# Windows consoles default to cp1252, which crashes on characters the model
# may emit. Force UTF-8 so the lab runs everywhere.
sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

from agents import StageResult, run_intake, run_validation, run_adjudication
from sample_claims import CLAIMS
from scratchpad import Scratchpad

load_dotenv()


def process_claim(claim: dict, pad: Scratchpad) -> str:
    """
    Walk one claim through all three stages.

    Returns the final status string: 'done' or 'failed'.
    The coordinator is the only place that knows how to react to a
    StageResult.ok == False - subagents themselves never raise.
    """
    claim_id = claim["claim_id"]
    stages = [
        ("intake", run_intake),
        ("validation", run_validation),
        ("adjudication", run_adjudication),
    ]

    print(f"[CLAIM {claim_id}] ", end="", flush=True)

    for stage_name, fn in stages:
        result = fn(claim)
        pad.log(claim_id, stage_name, result.to_dict())

        if result.ok:
            print(f"{stage_name}...ok  ", end="", flush=True)
        else:
            # Error PROPAGATES here - the coordinator logs the exact reason,
            # marks the claim failed, and stops processing further stages.
            print(f"{stage_name}...FAIL ({result.error})")
            pad.mark_failed(claim_id, f"{stage_name}: {result.error}")
            return "failed"

    print()  # newline after all stages succeed
    pad.mark_done(claim_id)
    return "done"


def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit(
            "Set ANTHROPIC_API_KEY first (copy .env.example to .env).\n"
            "Or run without a key:  python main.py --check"
        )

    pad = Scratchpad("scratchpad.json")
    print("Pipeline starting. State file: scratchpad.json\n")

    done_count = 0
    failed_count = 0
    skipped_count = 0

    for claim in CLAIMS:
        status = pad.status(claim["claim_id"])

        # Crash recovery: skip claims already finished.
        if status in ("done", "failed"):
            print(f"[CLAIM {claim['claim_id']}] (already {status}, skipping)")
            skipped_count += 1
            continue

        final = process_claim(claim, pad)
        if final == "done":
            done_count += 1
        else:
            failed_count += 1

    print("\n" + "-" * 60)
    print(f"SUMMARY  done: {done_count}   failed: {failed_count}   "
          f"skipped: {skipped_count}")
    print("Open scratchpad.json to inspect every finding.")
    print("-" * 60)


def check_offline() -> None:
    """Verify Demo 1-3 logic without calling the Claude API."""
    print("=" * 70)
    print("OFFLINE CHECK (no API calls — intake is stubbed)")
    print("=" * 70)

    print("\nDemo 1 — StageResult from validation + adjudication:\n")
    expected = {
        "CLM-001": ("ok", "approved"),
        "CLM-002": ("fail", "member_not_active"),
        "CLM-003": ("ok", "approved"),
    }
    for claim in CLAIMS:
        cid = claim["claim_id"]
        v = run_validation(claim)
        if v.ok:
            a = run_adjudication(claim)
            print(f"  {cid}  validation ok  adjudication={a.data['decision']}")
            assert expected[cid][0] == "ok"
            assert a.data["decision"] == expected[cid][1]
        else:
            print(f"  {cid}  validation FAIL ({v.error})  — adjudication skipped")
            assert expected[cid][0] == "fail"
            assert v.error == expected[cid][1]

    check_path = Path("scratchpad_check.json")
    if check_path.exists():
        check_path.unlink()

    pad = Scratchpad(str(check_path))

    def stub_intake(claim: dict) -> StageResult:
        return StageResult(
            stage="intake",
            ok=True,
            data={"claim_id": claim["claim_id"], "summary": "stub"},
        )

    print("\nDemo 2+3 — walk claims with stub intake, then restart skip:\n")
    original_intake = globals()["run_intake"]
    globals()["run_intake"] = stub_intake
    try:
        done_count = failed_count = 0
        for claim in CLAIMS:
            final = process_claim(claim, pad)
            if final == "done":
                done_count += 1
            else:
                failed_count += 1
    finally:
        globals()["run_intake"] = original_intake

    assert done_count == 2, done_count
    assert failed_count == 1, failed_count
    assert pad.status("CLM-001") == "done"
    assert pad.status("CLM-002") == "failed"
    assert pad.status("CLM-003") == "done"
    assert "member_not_active" in json.loads(check_path.read_text(encoding="utf-8"))["CLM-002"]["failure_reason"]

    print("\nSimulated restart (must skip all three):\n")
    pad2 = Scratchpad(str(check_path))
    skipped_count = 0
    for claim in CLAIMS:
        status = pad2.status(claim["claim_id"])
        if status in ("done", "failed"):
            print(f"  [CLAIM {claim['claim_id']}] (already {status}, skipping)")
            skipped_count += 1
    assert skipped_count == 3

    check_path.unlink()
    print("\nOffline check passed.")
    print("Next: copy .env.example to .env and run:  python main.py")
    print("Then run python main.py again — all three claims should skip.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check_offline()
    else:
        main()
