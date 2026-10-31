---
case: CASE-04
category: F7
category_acceptable: ["F7"]
pr_caused: n/a
pr_caused_acceptable: ["n/a"]
agent_should_run: false
should_comment: false
label: none
label_acceptable: [null]
must_mention: []
must_quote: []
must_not: [".+"]
recommended_action: "Agent must not run: the run is a push to master, not a pull_request run (if: gate)."
---

# Expected outcome: CASE-04

Written before any agent run (Phase 1). Regular expressions in `must_*` are matched
case-insensitively against the agent's comment (or noop reason) by `run_eval.py`.

## Justification

Push event on master (merge of upstream/pull/7542) [E:G1 row 04]; the workflow is gated to pull_request runs.

## Ground truth (after T, not given to the agent)

* Master stayed red on Tests until #7545 was merged (run 40781155430 passed at 22:35Z).
