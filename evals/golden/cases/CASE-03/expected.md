---
case: CASE-03
category: F4
category_acceptable: ["F4", "F5"]
pr_caused: no
pr_caused_acceptable: ["no", "unclear"]
agent_should_run: true
should_comment: true
label: ci-triage:infrastructure
label_acceptable: ["ci-triage:infrastructure", "ci-triage:known-issue", null]
must_mention: ["7544|26\\.04|runner|PostgreSQL|known issue"]
must_quote: ["_not_null1"]
must_not: ["\\*\\*Caused by this PR:\\*\\*\\s*yes"]
recommended_action: "Note that the PR's new sed rule does not match constraint names ending in a digit (e.g. current_nodes_id_not_null1), which still differ; extend the pattern."
---

# Expected outcome: CASE-03

Written before any agent run (Phase 1). Regular expressions in `must_*` are matched
case-insensitively against the agent's comment (or noop reason) by `run_eval.py`.

## Justification

This is the first push of the fix PR. Its one-line change adds `s/ CONSTRAINT [a-z][a-z_]* NOT NULL,/ NOT NULL,/` [E:CASE-03 diff], but the remaining diff lines are names with a trailing digit such as `current_nodes_id_not_null1` [E:CASE-03 log].

## Ground truth (after T, not given to the agent)

* The final version of the PR (head e87b1df, run 40762407177, CASE-17) passed all jobs; the merged rule is `s/ CONSTRAINT [a-z][a-z_]*_not_null[0-9]* NOT NULL,/ NOT NULL,/` (script/normalise-structure at the pinned commit).
* So the environment caused the failure and the PR's first attempt was an incomplete fix; blaming the PR for the failure would be wrong, but saying 'unclear' with the digit observation is acceptable.
