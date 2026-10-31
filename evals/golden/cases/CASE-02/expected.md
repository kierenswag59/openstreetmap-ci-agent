---
case: CASE-02
category: F4
category_acceptable: ["F4", "F5"]
pr_caused: no
pr_caused_acceptable: ["no"]
agent_should_run: true
should_comment: true
label: ci-triage:known-issue
label_acceptable: ["ci-triage:infrastructure", "ci-triage:known-issue", null]
must_mention: ["7544|#\\d+|known issue|issue"]
must_quote: ["CONSTRAINT \\w+ NOT NULL"]
must_not: ["\\*\\*Caused by this PR:\\*\\*\\s*yes"]
recommended_action: "Point to the existing issue (duplicate) instead of re-diagnosing; no code change in this PR."
---

# Expected outcome: CASE-02

Written before any agent run (Phase 1). Regular expressions in `must_*` are matched
case-insensitively against the agent's comment (or noop reason) by `run_eval.py`.

## Justification

Same structure-check signature as CASE-01 [E:CASE-02 log]; the PR changes only config/initializers/sentry.rb [E:CASE-02 diff]. Duplicate test case.

## Ground truth (after T, not given to the agent)

* Issue #7544 was open at T (opened 15:37Z).
* Lint, Docker and Devcontainer passed on the same head SHA; only Tests failed.
* The runner fix PR #7545 merged at 2026-10-28T22:35:34Z, after T.
