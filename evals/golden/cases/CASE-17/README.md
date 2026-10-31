# CASE-17

| Field | Value |
|---|---|
| Original run | [40762407177](https://github.com/openstreetmap/openstreetmap-website/actions/runs/40762407177) |
| Pull request | [PR #7545](https://github.com/openstreetmap/openstreetmap-website/pull/7545) |
| Workflow / failed job(s) / step | Tests / (all passed) / (none) |
| Cutoff T (UTC) | 2026-10-28T20:29:41Z (run updated_at (passing run); source: run jobs API, evidence G1) |
| Expected category / PR caused | F7 / n/a |
| Agent should run / comment | False / False |

## One-line rationale

All jobs succeeded on the final head e87b1df of PR #7545 [E:G1 row 17].

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

Expected outcome: [expected.md](expected.md). Agent output: [actual.md](actual.md).
