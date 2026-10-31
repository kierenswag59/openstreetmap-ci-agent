# CASE-08

| Field | Value |
|---|---|
| Original run | [35875254785](https://github.com/openstreetmap/openstreetmap-website/actions/runs/35875254785) |
| Pull request | [PR #7410](https://github.com/openstreetmap/openstreetmap-website/pull/7410) |
| Workflow / failed job(s) / step | Lint / ESLint / Run eslint |
| Cutoff T (UTC) | 2026-09-23T14:36:22Z (last failed job completed_at; source: run jobs API, evidence G1) |
| Expected category / PR caused | F2 / yes |
| Agent should run / comment | True / True |

## One-line rationale

`13:13 error 'unit' is never reassigned. Use 'const' instead prefer-const` and the same for line 14 in app/assets/javascripts/leaflet.locate.js [E:CASE-08 log]; both lines are added by the PR [E:CASE-08 diff].

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
