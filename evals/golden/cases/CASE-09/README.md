# CASE-09

| Field | Value |
|---|---|
| Original run | [33694039489](https://github.com/openstreetmap/openstreetmap-website/actions/runs/33694039489) |
| Pull request | [PR #7355](https://github.com/openstreetmap/openstreetmap-website/pull/7355) |
| Workflow / failed job(s) / step | Lint / RuboCop / Run rubocop |
| Cutoff T (UTC) | 2026-09-02T23:14:06Z (last failed job completed_at; source: run jobs API, evidence G1) |
| Expected category / PR caused | F3 / yes |
| Agent should run / comment | True / True |

## One-line rationale

Dependabot bump of rubocop 1.89.0 to 1.90.0 [E:G3 R-09]; RuboCop reports 6 new autocorrectable offences (Style/DirectiveScope, Layout/ExtraSpacing) in files the PR does not touch [E:CASE-09 log][E:CASE-09 diff].

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

Expected outcome: [expected.md](expected.md). Agent output: live [actual.md](actual.md); dry run [actual-dryrun.md](actual-dryrun.md).
