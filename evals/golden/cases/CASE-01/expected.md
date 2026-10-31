---
case: CASE-01
category: F4
category_acceptable: ["F4", "F5"]
pr_caused: no
pr_caused_acceptable: ["no"]
agent_should_run: true
should_comment: true
label: ci-triage:infrastructure
label_acceptable: ["ci-triage:infrastructure", "ci-triage:known-issue", null]
must_mention: ["7544|Ubuntu 26\\.04|26\\.04|runner", "CONSTRAINT|NOT NULL|structure"]
must_quote: ["CONSTRAINT \\w+ NOT NULL"]
must_not: ["\\*\\*Caused by this PR:\\*\\*\\s*yes"]
recommended_action: "Say the failure is the runner/PostgreSQL change tracked in the known issue, not this PR; no code change; re-run after the fix lands."
---

# Expected outcome: CASE-01

Written before any agent run (Phase 1). Regular expressions in `must_*` are matched
case-insensitively against the agent's comment (or noop reason) by `run_eval.py`.

## Justification

All three Ruby jobs fail the db/structure.sql diff with lines like `+    way_id bigint CONSTRAINT ways_id_not_null NOT NULL,` [E:CASE-01 log]; the PR touches avatars only [E:CASE-01 diff].

## Ground truth (after T, not given to the agent)

* Issue #7544 "CI fails on Ubuntu 26.04 runners" was opened at 2026-10-28T15:37:29Z, before T, by the PR author (https://github.com/openstreetmap/openstreetmap-website/issues/7544).
* Master Tests failed the same way from 2026-10-28T15:14Z (run 40713973741) until PR #7545 was merged at 22:35Z.
* The PR's next Lint/Tests run on 2026-10-29 (head 3ea8c02) passed Tests (run 40916734226) with no change to the structure check.
