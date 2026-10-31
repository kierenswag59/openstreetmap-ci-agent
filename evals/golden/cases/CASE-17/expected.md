---
case: CASE-17
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
recommended_action: "Agent must not run: the run succeeded (if: gate on conclusion)."
---

# Expected outcome: CASE-17

Written before any agent run (Phase 1). Regular expressions in `must_*` are matched
case-insensitively against the agent's comment (or noop reason) by `run_eval.py`.

## Justification

All jobs succeeded on the final head e87b1df of PR #7545 [E:G1 row 17].

## Ground truth (after T, not given to the agent)

* Merged 2026-10-28T22:35:34Z.
