---
case: CASE-05
category: F7
category_acceptable: ["F7"]
pr_caused: n/a
pr_caused_acceptable: ["n/a"]
agent_should_run: true
should_comment: false
label: none
label_acceptable: [null]
must_mention: ["F7|approval|never (ran|started)|no jobs"]
must_quote: []
must_not: []
recommended_action: "noop: the run never executed (approval required, expired)."
---

# Expected outcome: CASE-05

Written before any agent run (Phase 1). Regular expressions in `must_*` are matched
case-insensitively against the agent's comment (or noop reason) by `run_eval.py`.

## Justification

The run has 0 jobs and its annotation says 'This workflow run required approval but was not approved before it expired.' [E:CASE-05 run page][E:G1 row 05].

## Ground truth (after T, not given to the agent)

* All five workflows on head 1897639 show the same expired-approval state; there is no code failure to analyse.
