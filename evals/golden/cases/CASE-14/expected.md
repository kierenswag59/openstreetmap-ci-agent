---
case: CASE-14
category: F2
category_acceptable: ["F2"]
pr_caused: yes
pr_caused_acceptable: ["yes"]
agent_should_run: true
should_comment: true
label: ci-triage:pr-related
label_acceptable: ["ci-triage:pr-related", null]
must_mention: ["app/models/user\\.rb", "ClassLength"]
must_quote: ["Metrics/ClassLength"]
must_not: []
recommended_action: "Shorten the User class by one line or, if maintainers agree, raise Metrics/ClassLength Max in .rubocop_todo.yml (the PR already sets 356; it needs 357)."
---

# Expected outcome: CASE-14

Written before any agent run (Phase 1). Regular expressions in `must_*` are matched
case-insensitively against the agent's comment (or noop reason) by `run_eval.py`.

## Justification

`app/models/user.rb:53:1: R: Metrics/ClassLength: Class has too many lines. [357/356]` [E:CASE-14 log]; the PR edits app/models/user.rb and raises the todo limit from 353 to 356 [E:CASE-14 diff].

## Ground truth (after T, not given to the agent)

* Nine minutes after T the author pushed fb533497, whose .rubocop_todo.yml sets Max: 357.
* Tests passed on the same head SHA (run 40916734226).
