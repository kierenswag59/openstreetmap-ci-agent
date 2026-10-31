---
case: CASE-09
category: F3
category_acceptable: ["F3"]
pr_caused: yes
pr_caused_acceptable: ["yes", "unclear"]
agent_should_run: true
should_comment: true
label: ci-triage:dependency
label_acceptable: ["ci-triage:dependency", null]
must_mention: ["rubocop|RuboCop", "DirectiveScope|ExtraSpacing|new cop|1\\.90"]
must_quote: ["Style/DirectiveScope|Layout/ExtraSpacing"]
must_not: []
recommended_action: "Fix the 6 autocorrectable offences (`bundle exec rubocop -a`) in a commit on top of the bump before merging."
---

# Expected outcome: CASE-09

Written before any agent run (Phase 1). Regular expressions in `must_*` are matched
case-insensitively against the agent's comment (or noop reason) by `run_eval.py`.

## Justification

Dependabot bump of rubocop 1.89.0 to 1.90.0 [E:G3 R-09]; RuboCop reports 6 new autocorrectable offences (Style/DirectiveScope, Layout/ExtraSpacing) in files the PR does not touch [E:CASE-09 log][E:CASE-09 diff].

## Ground truth (after T, not given to the agent)

* A maintainer merged the PR at 23:38Z and pushed 'Fix new rubocop warnings' (f572e01b) at 23:40Z; master Lint then passed (run 33696462449).
