#!/usr/bin/env python3
"""Turn a case's input/replay.json into the job matrix for replay-failure.yml.

Usage: python3 evals/replay_plan.py <CASE-ID | eval/CASE-ID | adv/ADV-ID>

Prints "matrix=<json>" for $GITHUB_OUTPUT. A case whose replay.json has
"no_jobs": true (the original run never started) makes this planning job fail
with the original run's annotation instead, because a sandbox run cannot have
zero jobs.
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def find_case(ref):
    name = ref.split("/")[-1]
    for group in ("golden/cases", "adversarial", "golden/seeds"):
        path = os.path.join(ROOT, group, name, "input", "replay.json")
        if os.path.exists(path):
            return name, path
    raise SystemExit(f"no replay.json for {ref!r}")


def main(argv):
    if len(argv) != 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0 if len(argv) == 2 else 2
    name, path = find_case(argv[1])
    spec = json.load(open(path, encoding="utf-8"))
    if spec.get("no_jobs"):
        print(f"::error::{spec.get('annotation', 'The original run had no jobs.')}", file=sys.stderr)
        print("matrix=[]")
        sys.exit(1)
    matrix = []
    for job in spec["jobs"]:
        log = os.path.join("evals", os.path.relpath(os.path.dirname(path), ROOT), job["log"])
        matrix.append({"name": job["name"], "step": job["step"], "log": log,
                       "exit_code": job.get("exit_code", 1)})
    print("matrix=" + json.dumps(matrix))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
