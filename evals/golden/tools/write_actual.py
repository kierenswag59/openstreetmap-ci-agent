#!/usr/bin/env python3
"""Write a case's actual.md from a dry-run result or a gate-only (not-run) observation.

  write_actual.py CASE-08 --dryrun result.json --replay URL --gate URL --capture URL \
      --transcript evals/golden/dryrun/transcripts/CASE-08.jsonl --model claude-sonnet-5-5
  write_actual.py CASE-17 --not-run "analyst not triggered: run conclusion success" --replay URL

result.json is the JSON object the dry-run session printed (type, item_number, label, body).
The body is copied verbatim; it is never edited.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def case_dir(cid):
    for p in (f"evals/golden/cases/{cid}", f"evals/adversarial/{cid}"):
        if os.path.isdir(os.path.join(ROOT, p)):
            return os.path.join(ROOT, p)
    raise SystemExit(f"unknown case {cid}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("case")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dryrun", help="JSON file with the dry-run output object")
    g.add_argument("--not-run", help="observation when the analyst's agent job did not start")
    for k in ("replay", "gate", "capture", "transcript", "model", "pr", "duration", "tokens", "note"):
        ap.add_argument("--" + k, default="")
    a = ap.parse_args(argv)
    meta = {"case": a.case}
    if a.dryrun:
        r = json.load(open(a.dryrun, encoding="utf-8"))
        kind = {"add_comment": "comment", "noop": "noop"}.get(r.get("type"), r.get("type"))
        meta.update(mode="dry-run", output=kind, label=r.get("label") or "none",
                    item_number=r.get("item_number"), comments_posted=1 if kind == "comment" else 0)
        text = r.get("body", "")
    else:
        meta.update(mode="live-gate", output="not-run", label="none", comments_posted=0)
        text = a.not_run
    for k in ("replay", "gate", "capture", "transcript", "model", "pr", "duration", "tokens", "note"):
        if getattr(a, k):
            meta[k] = getattr(a, k)
    lines = ["---"] + [f"{k}: {json.dumps(v) if not isinstance(v, str) else v}" for k, v in meta.items()] + ["---", ""]
    lines += [f"# Actual outcome: {a.case}", "",
              "Verbatim output (comment body or noop reason) of the run described above:", "",
              "~~~text", text.rstrip("\n"), "~~~", ""]
    open(os.path.join(case_dir(a.case), "actual.md"), "w", encoding="utf-8").write("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
