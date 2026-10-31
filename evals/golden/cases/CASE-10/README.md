# CASE-10

| Field | Value |
|---|---|
| Original run | [37705152851](https://github.com/openstreetmap/openstreetmap-website/actions/runs/37705152851) |
| Pull request | [PR #7480](https://github.com/openstreetmap/openstreetmap-website/pull/7480) |
| Workflow / failed job(s) / step | Tests / Ruby 3.3, Ruby 3.4, Ruby 4.0 / Setup ruby |
| Cutoff T (UTC) | 2026-10-07T23:57:55Z (last failed job completed_at; source: run jobs API, evidence G1) |
| Expected category / PR caused | F3 / unclear |
| Agent should run / comment | True / True |

## One-line rationale

All Ruby jobs fail in Setup ruby: 'The dependencies in your gemfile changed, but the lockfile can't be updated because frozen mode is set' and bundle exits 16 [E:CASE-10 log]. The PR changes only Gemfile.lock [E:CASE-10 diff] and its merge base is master commit 8524e874 'Pin dartsass-sprockets', which changed the Gemfile 14 minutes earlier.

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
