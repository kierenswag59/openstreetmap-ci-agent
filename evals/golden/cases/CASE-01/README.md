# CASE-01

| Field | Value |
|---|---|
| Original run | [40753633422](https://github.com/openstreetmap/openstreetmap-website/actions/runs/40753633422) |
| Pull request | [PR #7546](https://github.com/openstreetmap/openstreetmap-website/pull/7546) |
| Workflow / failed job(s) / step | Tests / Ruby 3.3, Ruby 3.4, Ruby 4.0 / Populate database |
| Cutoff T (UTC) | 2026-10-28T19:24:10Z (last failed job completed_at; source: run jobs API, evidence G1) |
| Expected category / PR caused | F4 / no |
| Agent should run / comment | True / True |

## One-line rationale

All three Ruby jobs fail the db/structure.sql diff with lines like `+    way_id bigint CONSTRAINT ways_id_not_null NOT NULL,` [E:CASE-01 log]; the PR touches avatars only [E:CASE-01 diff].

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
