# CASE-15

| Field | Value |
|---|---|
| Original run | [35933394011](https://github.com/openstreetmap/openstreetmap-website/actions/runs/35933394011) |
| Pull request | [PR #7421](https://github.com/openstreetmap/openstreetmap-website/pull/7421) |
| Workflow / failed job(s) / step | Lint / Rails Annotate Models / Fail if model annotations are out of date |
| Cutoff T (UTC) | 2026-09-23T23:25:24Z (last failed job completed_at; source: run jobs API, evidence G1) |
| Expected category / PR caused | F3 / yes |
| Agent should run / comment | True / True |

## One-line rationale

`git diff --exit-code` shows annotations now include `inet_ops` in app/models/acl.rb and app/models/user.rb [E:CASE-15 log]; the PR bumps annotaterb 4.24.0 to 4.25.0 in Gemfile.lock [E:CASE-15 diff].

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
