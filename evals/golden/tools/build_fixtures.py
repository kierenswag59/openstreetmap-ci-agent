#!/usr/bin/env python3
"""Build evals/golden/cases/*/input/ and evals/golden/seeds/*/input/ from upstream.

Read-only: it only GETs public data from openstreetmap/openstreetmap-website via
the gh CLI. It respects the temporal cutoff T of each case: PR comments and
reviews created after T are dropped, the diff is taken at the exact head SHA
against the base SHA the run actually tested (from the checkout step's
"Merge <head> into <base>" line), and nothing after T is written to input/.

Usage: python3 evals/golden/tools/build_fixtures.py [CASE-01 ...]
"""

import json
import os
import re
import subprocess
import sys

UP = "openstreetmap/openstreetmap-website"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# case id -> (run id, PR number or None, cutoff T in UTC, how T was established)
CASES = {
    "CASE-01": (40753633422, 7546, "2026-10-28T19:24:10Z", "last failed job completed_at"),
    "CASE-02": (40757514945, 7547, "2026-10-28T19:50:26Z", "last failed job completed_at"),
    "CASE-03": (40746377705, 7545, "2026-10-28T18:36:00Z", "last failed job completed_at"),
    "CASE-04": (40761769826, None, "2026-10-28T20:18:03Z", "last failed job completed_at"),
    "CASE-05": (36330556125, 7432, "2026-10-27T15:47:23Z", "run updated_at (run had no jobs; approval expired)"),
    "CASE-06": (35760389282, 7398, "2026-09-22T17:27:24Z", "last failed job completed_at"),
    "CASE-07": (35636239291, 7399, "2026-09-21T18:09:34Z", "last failed job completed_at"),
    "CASE-08": (35875254785, 7410, "2026-09-23T14:36:22Z", "last failed job completed_at"),
    "CASE-09": (33694039489, 7355, "2026-09-02T23:14:06Z", "last failed job completed_at"),
    "CASE-10": (37705152851, 7480, "2026-10-07T23:57:55Z", "last failed job completed_at"),
    "CASE-11": (33391131716, 7350, "2026-08-31T12:27:07Z", "last failed job completed_at"),
    "CASE-12": (32283669556, 7328, "2026-08-19T18:53:30Z", "last failed job completed_at (attempt 4)"),
    "CASE-13": (38562633179, 7490, "2026-10-14T12:17:59Z", "last failed job completed_at"),
    "CASE-14": (40916734387, 7546, "2026-10-29T16:58:41Z", "last failed job completed_at"),
    "CASE-15": (35933394011, 7421, "2026-09-23T23:25:24Z", "last failed job completed_at"),
    "CASE-17": (40762407177, 7545, "2026-10-28T20:29:41Z", "run updated_at (passing run)"),
}
# default-branch state seeds: (run id, note)
SEEDS = {
    "SEED-M1": (40713973741, "master Tests failure 2026-10-28 15:14 UTC (structure check), before CASE-01..03"),
    "SEED-M2": (35634504477, "master Docker failure 2026-09-21 17:50 UTC (mini_racer LoadError), before CASE-06/07"),
    "SEED-M3": (32247269027, "master Tests failure 2026-08-19 11:22 UTC (SearchTest Nominatim), before CASE-12"),
    "SEED-P": (32282177239, "master Tests success 2026-08-19 17:32 UTC, after SEED-M3 and before CASE-12"),
}


def gh(path, accept=None, raw=False):
    cmd = ["gh", "api"]
    if raw:
        cmd.append("--allow-escape-sequences")
    if accept:
        cmd += ["-H", f"Accept: {accept}"]
    cmd.append(path)
    res = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    if res.returncode != 0:
        raise RuntimeError(f"{path}: {res.stderr[:200]}")
    return res.stdout


def gj(path):
    return json.loads(gh(path))


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(data if isinstance(data, str) else json.dumps(data, indent=2) + "\n")


def job_entries(run_id, out_dir):
    run = gj(f"repos/{UP}/actions/runs/{run_id}")
    jobs = gj(f"repos/{UP}/actions/runs/{run_id}/jobs?per_page=100")["jobs"]
    entries, base = [], None
    for j in jobs:
        failed_steps = [s["name"] for s in j["steps"] if s.get("conclusion") == "failure"]
        if j["conclusion"] not in ("failure", "success") or j["name"] == "Finalise":
            continue
        log = gh(f"repos/{UP}/actions/jobs/{j['id']}/logs", raw=True)
        m = re.search(r"Merge ([0-9a-f]{40}) into ([0-9a-f]{40})", log)
        if m:
            base = m.group(2)
        if j["conclusion"] == "success":
            # Passing sibling jobs are replayed for realism, but only their last
            # 200 lines are kept to limit repository size.
            lines = log.splitlines()
            log = "\n".join(["[fixture note: passing job, last 200 lines of the original log kept]"]
                            + lines[-200:]) + "\n" if len(lines) > 200 else log
        name = f"job-{j['id']}.log"
        write(os.path.join(out_dir, "logs", name), log)
        entries.append({"name": j["name"], "step": failed_steps[0] if failed_steps else "Run tests",
                        "log": f"logs/{name}", "exit_code": 1 if j["conclusion"] == "failure" else 0,
                        "original_job_id": j["id"], "original_conclusion": j["conclusion"]})
    summary = [{"id": j["id"], "name": j["name"], "conclusion": j["conclusion"],
                "completed_at": j["completed_at"],
                "failed_steps": [s["name"] for s in j["steps"] if s.get("conclusion") == "failure"]} for j in jobs]
    return run, summary, entries, base


def build_case(cid):
    run_id, pr_no, T, how = CASES[cid]
    d = os.path.join(ROOT, "cases", cid, "input")
    import shutil
    shutil.rmtree(os.path.join(d, "logs"), ignore_errors=True)
    run, jobs, entries, base = job_entries(run_id, d)
    keep = ("id", "name", "event", "status", "conclusion", "head_sha", "head_branch", "html_url",
            "run_attempt", "created_at", "run_started_at", "updated_at", "display_title")
    write(os.path.join(d, "run.json"), {k: run.get(k) for k in keep})
    write(os.path.join(d, "jobs.json"), jobs)
    spec = {"case": cid, "workflow": run["name"], "original_run": run["html_url"], "cutoff_T": T,
            "cutoff_source": how, "jobs": entries}
    if not jobs:
        spec = {"case": cid, "workflow": run["name"], "original_run": run["html_url"], "cutoff_T": T,
                "cutoff_source": how, "no_jobs": True,
                "annotation": "This workflow run required approval but was not approved before it expired.",
                "jobs": []}
    write(os.path.join(d, "replay.json"), spec)
    if pr_no:
        pr = gj(f"repos/{UP}/pulls/{pr_no}")
        write(os.path.join(d, "pr.json"), {
            "number": pr_no, "title": pr["title"], "body": pr["body"] or "", "author": pr["user"]["login"],
            "author_association": pr["author_association"], "created_at": pr["created_at"],
            "head_repo": (pr["head"]["repo"] or {}).get("full_name"), "head_ref": pr["head"]["ref"],
            "tested_head_sha": run["head_sha"], "tested_base_sha": base, "html_url": pr["html_url"],
            "note": "title and body are as fetched on 2026-10-31; they may have been edited after T"})
        if base:
            write(os.path.join(d, "pr.diff"),
                  gh(f"repos/{UP}/compare/{base}...{run['head_sha']}", accept="application/vnd.github.diff"))
            mb = gj(f"repos/{UP}/compare/{base}...{run['head_sha']}")["merge_base_commit"]["sha"]
            spec["merge_base_sha"] = mb
            write(os.path.join(d, "replay.json"), spec)
        comments = gj(f"repos/{UP}/issues/{pr_no}/comments?per_page=100")
        reviews = gj(f"repos/{UP}/pulls/{pr_no}/reviews?per_page=100")
        before = [{"author": c["user"]["login"], "created_at": c["created_at"], "body": c["body"]}
                  for c in comments if c["created_at"] < T]
        before += [{"author": r["user"]["login"], "created_at": r["submitted_at"], "body": r["body"],
                    "review_state": r["state"]} for r in reviews if r.get("submitted_at") and r["submitted_at"] < T]
        write(os.path.join(d, "comments-before-T.json"), before)
    print(cid, run["name"], run["conclusion"], len(spec["jobs"]), "jobs", "base", (base or "-")[:8])


def build_seed(sid):
    run_id, note = SEEDS[sid]
    d = os.path.join(ROOT, "seeds", sid, "input")
    import shutil
    shutil.rmtree(os.path.join(d, "logs"), ignore_errors=True)
    run, jobs, entries, _ = job_entries(run_id, d)
    failed = [e for e in entries if e["original_conclusion"] == "failure"]
    keep = failed[:1] if failed else entries[:1]
    for e in entries:
        if e not in keep:
            os.remove(os.path.join(d, e["log"]))
    spec = {"case": sid, "workflow": run["name"], "original_run": run["html_url"], "note": note, "jobs": keep}
    write(os.path.join(d, "replay.json"), spec)
    print(sid, run["name"], run["conclusion"])


def main(argv):
    names = argv[1:] or list(CASES) + list(SEEDS)
    for n in names:
        (build_seed if n in SEEDS else build_case)(n)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
