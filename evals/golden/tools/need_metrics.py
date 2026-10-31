#!/usr/bin/env python3
"""Recompute the need-for-automation metrics in evals/golden/NEED.md (read-only API calls).

Usage: python3 evals/golden/tools/need_metrics.py [--out DIR]
Writes pr_runs.tsv and master_runs.tsv to DIR (default: a temp dir) and prints the metrics.
"""
import argparse, collections, csv, datetime as dt, json, os, statistics, subprocess, tempfile

R = "repos/openstreetmap/openstreetmap-website"
W = {"Tests", "Lint", "Docker", "Development Container"}
P = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def runs(query):
    out = subprocess.run(["gh", "api", "--paginate", f"{R}/actions/runs?{query}&per_page=100", "--jq",
                          ".workflow_runs[]|[.id,.name,.conclusion,.created_at,.updated_at,.head_sha,.head_branch,"
                          "(.pull_requests|map(.number)|join(\",\")),.actor.login,.head_repository.full_name]|@tsv"],
                         capture_output=True, text=True, check=True).stdout
    return [l.split("\t") for l in out.splitlines() if l]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=tempfile.mkdtemp())
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    pr = []
    for d in ("2026-08-01..2026-08-31", "2026-09-01..2026-09-30", "2026-10-01..2026-10-29"):
        pr += runs(f"event=pull_request&created={d}")
    master = runs("branch=master&event=push&created=2026-07-25..2026-10-29")
    for name, rows in (("pr_runs.tsv", pr), ("master_runs.tsv", master)):
        with open(os.path.join(a.out, name), "w") as fh:
            csv.writer(fh, delimiter="\t").writerows(rows)
    pr = [r for r in pr if r[1] in W]
    weeks = (P("2026-10-30T00:00:00Z") - P("2026-08-01T00:00:00Z")).days / 7
    fail = [r for r in pr if r[2] == "failure"]
    print(f"weeks={weeks:.2f} runs={len(pr)} failed={len(fail)} per_week={len(fail)/weeks:.1f}")
    for w in sorted(W):
        print(f"  {w}: runs={sum(r[1]==w for r in pr)} failed={sum(r[1]==w for r in fail)}")
    key = lambda r: (r[9], r[6])
    prs, fprs = {key(r) for r in pr}, {key(r) for r in fail}
    print(f"branches={len(prs)} with_failure={len(fprs)} share={100*len(fprs)/len(prs):.0f}%")
    mf = [(m[1], P(m[4])) for m in master if m[2] == "failure"]
    also = sum(any(w == r[1] and P(r[4]) - dt.timedelta(hours=24) <= t <= P(r[4]) for w, t in mf) for r in fail)
    print(f"also_failed_on_master_24h={also} share={100*also/len(fail):.0f}%")
    by = collections.defaultdict(list)
    for r in pr:
        by[key(r)].append((P(r[3]), r[5]))
    d = []
    for r in fail:
        later = [c for c, s in by[key(r)] if c > P(r[4]) and s != r[5]]
        if later:
            d.append((min(later) - P(r[4])).total_seconds() / 3600)
    q = statistics.quantiles(d, n=4)
    print(f"followed_by_push={len(d)} median_h={statistics.median(d):.1f} iqr={q[0]:.1f}-{q[2]:.1f}")
    print(f"dependabot_failed={sum(r[8]=='dependabot[bot]' for r in fail)}")


if __name__ == "__main__":
    main()
