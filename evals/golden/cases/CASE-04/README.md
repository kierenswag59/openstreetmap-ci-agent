# CASE-04

| Field | Value |
|---|---|
| Original run | [40761769826](https://github.com/openstreetmap/openstreetmap-website/actions/runs/40761769826) |
| Pull request | none (push to master) |
| Workflow / failed job(s) / step | Tests / Ruby 3.3, Ruby 3.4, Ruby 4.0 / Populate database |
| Cutoff T (UTC) | 2026-10-28T20:18:03Z (last failed job completed_at; source: run jobs API, evidence G1) |
| Expected category / PR caused | F7 / n/a |
| Agent should run / comment | False / False |

## One-line rationale

Push event on master (merge of upstream/pull/7542) [E:G1 row 04]; the workflow is gated to pull_request runs.

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
* The original event was a push to master. The replay is dispatched (workflow_dispatch) on a branch with no PR, which exercises the same gate (`workflow_run.event != pull_request`).

Expected outcome: [expected.md](expected.md). Agent output: [actual.md](actual.md).
