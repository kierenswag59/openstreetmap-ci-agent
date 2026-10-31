# CASE-02

| Field | Value |
|---|---|
| Original run | [40757514945](https://github.com/openstreetmap/openstreetmap-website/actions/runs/40757514945) |
| Pull request | [PR #7547](https://github.com/openstreetmap/openstreetmap-website/pull/7547) |
| Workflow / failed job(s) / step | Tests / Ruby 3.3, Ruby 3.4, Ruby 4.0 / Populate database |
| Cutoff T (UTC) | 2026-10-28T19:50:26Z (last failed job completed_at; source: run jobs API, evidence G1) |
| Expected category / PR caused | F4 / no |
| Agent should run / comment | True / True |

## One-line rationale

Same structure-check signature as CASE-01 [E:CASE-02 log]; the PR changes only config/initializers/sentry.rb [E:CASE-02 diff]. Duplicate test case.

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
* Sandbox state at T is rebuilt by seeds: SEED-M1 (master Tests failure) and a mirror of issue #7544 (see evals/golden/SEEDS.md).

Expected outcome: [expected.md](expected.md). Agent output: [actual.md](actual.md).
