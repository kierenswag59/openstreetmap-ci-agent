#!/usr/bin/env python3
"""Report whether the same failure signature was already seen on the default branch.

Input is a JSON file produced by collect_context.py: a list of recent completed
runs of the same workflow on the default branch, newest first, each with the
signatures of its failed jobs:

  [{"id": 1, "created_at": "2026-10-28T15:14:44Z", "conclusion": "failure",
    "html_url": "...", "failed": [{"job": "Ruby 3.3", "signature": "4f30d658b61e"}]}]

Only runs created before --before (the triggering run's start time) count, so
a replay never sees "future" master runs.

Verdicts:
  broken    the newest master run with a matching signature is newer than the
            newest successful master run (master is currently failing the same way)
  seen      the signature failed on master in the window but master passed since
            (often a flaky test)
  clean     no master run in the window failed with this signature
  unknown   no master runs available

Standard library only. Output is JSON on stdout.
"""

import argparse
import datetime as dt
import json
import sys


def parse_time(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def check(runs, signature, before=None, window_hours=72):
    if before:
        cutoff = parse_time(before)
        runs = [r for r in runs if parse_time(r["created_at"]) < cutoff]
        lower = cutoff - dt.timedelta(hours=window_hours)
        runs = [r for r in runs if parse_time(r["created_at"]) >= lower]
    runs = sorted(runs, key=lambda r: r["created_at"], reverse=True)
    completed = [r for r in runs if r.get("conclusion") in ("success", "failure", "timed_out")]
    if not completed:
        return {"verdict": "unknown", "matching_runs": [], "latest_conclusion": None, "runs_considered": 0}
    matching = [r for r in completed
                if r.get("conclusion") != "success"
                and any(f.get("signature") == signature for f in r.get("failed", []))]
    successes = [r for r in completed if r.get("conclusion") == "success"]
    if not matching:
        verdict = "clean"
    elif not successes or matching[0]["created_at"] > successes[0]["created_at"]:
        verdict = "broken"
    else:
        verdict = "seen"
    return {
        "verdict": verdict,
        "matching_runs": [{"id": r["id"], "created_at": r["created_at"], "html_url": r.get("html_url", "")}
                          for r in matching[:5]],
        "latest_conclusion": completed[0]["conclusion"],
        "latest_success_at": successes[0]["created_at"] if successes else None,
        "runs_considered": len(completed),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", required=True, help="JSON file of recent default-branch runs")
    ap.add_argument("--signature", required=True, help="signature from extract_failure.py")
    ap.add_argument("--before", help="ISO time; ignore runs created at or after it")
    ap.add_argument("--window-hours", type=int, default=72, help="look-back window (default 72)")
    args = ap.parse_args(argv)
    runs = json.load(open(args.runs, encoding="utf-8"))
    json.dump(check(runs, args.signature, args.before, args.window_hours), sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
