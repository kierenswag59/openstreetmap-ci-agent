---
case: CASE-13
category: F2
category_acceptable: ["F2"]
pr_caused: yes
pr_caused_acceptable: ["yes"]
agent_should_run: true
should_comment: true
label: ci-triage:pr-related
label_acceptable: ["ci-triage:pr-related", null]
must_mention: ["moderation_zone\\.js", "eol-last|newline"]
must_quote: ["eol-last"]
must_not: []
recommended_action: "Add a trailing newline at the end of app/assets/javascripts/moderation_zone.js (or run `bundle exec rails eslint:fix`)."
---

# Expected outcome: CASE-13

Written before any agent run (Phase 1). Regular expressions in `must_*` are matched
case-insensitively against the agent's comment (or noop reason) by `run_eval.py`.

## Justification

`172:4 error Newline required at end of file but not found @stylistic/eol-last` in app/assets/javascripts/moderation_zone.js [E:CASE-13 log]; the PR rewrites that file including line 172 [E:CASE-13 diff].

## Ground truth (after T, not given to the agent)

* Tests and Docker passed on the same head SHA. The PR was later closed without merge on 2026-10-16 after a messy rebase.
