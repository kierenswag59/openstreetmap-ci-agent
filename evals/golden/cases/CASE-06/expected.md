---
case: CASE-06
category: F5
category_acceptable: ["F5", "F4"]
pr_caused: no
pr_caused_acceptable: ["no"]
agent_should_run: true
should_comment: true
label: ci-triage:known-issue
label_acceptable: ["ci-triage:known-issue", "ci-triage:infrastructure", null]
must_mention: ["master", "mini_racer|__isoc23_strtoll|LoadError"]
must_quote: ["__isoc23_strtoll|LoadError"]
must_not: ["\\*\\*Caused by this PR:\\*\\*\\s*yes"]
recommended_action: "Say Docker is already failing on master with the same LoadError; nothing to fix in this PR."
---

# Expected outcome: CASE-06

Written before any agent run (Phase 1). Regular expressions in `must_*` are matched
case-insensitively against the agent's comment (or noop reason) by `run_eval.py`.

## Justification

`LoadError: .../mini_racer_extension.so: undefined symbol: __isoc23_strtoll` while loading rtlcss in `rails db:migrate` [E:CASE-06 log]; the PR changes only config/initializers/sentry.rb [E:CASE-06 diff].

## Ground truth (after T, not given to the agent)

* Master Docker failed with this signature at 2026-09-21T08:32Z (run 35578428666, evidence E3) and 17:50Z (run 35634504477).
* Master Docker passed again after 'Merge pull request #7403 from tomhughes/docker' at 2026-09-22T17:43Z, after T.
* Tests, Lint and Devcontainer passed on the same head SHA; the PR merged on 2026-09-23.
