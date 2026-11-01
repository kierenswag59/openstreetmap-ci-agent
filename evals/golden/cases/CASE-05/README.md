# CASE-05

| Field | Value |
|---|---|
| Original run | [36330556125](https://github.com/openstreetmap/openstreetmap-website/actions/runs/36330556125) |
| Pull request | [PR #7432](https://github.com/openstreetmap/openstreetmap-website/pull/7432) |
| Workflow / failed job(s) / step | Tests / (none) / (none) |
| Cutoff T (UTC) | 2026-10-27T15:47:23Z (run updated_at (run had no jobs; approval expired); source: run jobs API, evidence G1) |
| Expected category / PR caused | F7 / n/a |
| Agent should run / comment | True / False |

## One-line rationale

The run has 0 jobs and its annotation says 'This workflow run required approval but was not approved before it expired.' [E:CASE-05 run page][E:G1 row 05].

## Input fixture (`input/`), everything as of T

* `run.json`, `jobs.json`: the original run and its job list (job conclusions and failed steps).
* `logs/job-<id>.log`: raw original job logs (passing sibling jobs keep only their last 200 lines).
* `pr.json`: PR number, title, body, author and association; `tested_base_sha`/`tested_head_sha` come from
  the checkout step's `Merge <head> into <base>` line in the log.
* `pr.diff`: diff between the tested base and the tested head SHA (three-dot compare), i.e. what CI tested.
* `comments-before-T.json`: PR comments and reviews created before T.
* `replay.json`: how `replay-failure.yml` reproduces the run (job names, failed step names, logs, exit codes).

## Limitations

* The PR title and body were fetched on 2026-10-31 and may have been edited after T.
* Replayed logs are re-emitted by a new runner, so timestamps and the runner preamble differ from the original.
* A sandbox run cannot have zero jobs; the replay's 'Prepare replay' job fails with the original annotation text instead.

Expected outcome: [expected.md](expected.md). Agent output: live [actual.md](actual.md); dry run [actual-dryrun.md](actual-dryrun.md).
