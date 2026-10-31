---
case: CASE-08
category: F2
category_acceptable: ["F2"]
pr_caused: yes
pr_caused_acceptable: ["yes"]
agent_should_run: true
should_comment: true
label: ci-triage:pr-related
label_acceptable: ["ci-triage:pr-related", null]
must_mention: ["leaflet\\.locate\\.js", "prefer-const|const"]
must_quote: ["prefer-const"]
must_not: []
recommended_action: "Change the two new `let` declarations (lines 13 and 14) to `const`, or run `bundle exec rails eslint:fix`."
---

# Expected outcome: CASE-08

Written before any agent run (Phase 1). Regular expressions in `must_*` are matched
case-insensitively against the agent's comment (or noop reason) by `run_eval.py`.

## Justification

`13:13 error 'unit' is never reassigned. Use 'const' instead prefer-const` and the same for line 14 in app/assets/javascripts/leaflet.locate.js [E:CASE-08 log]; both lines are added by the PR [E:CASE-08 diff].

## Ground truth (after T, not given to the agent)

* The author force-pushed a new version (324b8d41) on 2026-09-24; the PR was merged on 2026-09-24T16:37:59Z.
