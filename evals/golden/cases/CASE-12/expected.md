---
case: CASE-12
category: F6
category_acceptable: ["F6", "F5"]
pr_caused: no
pr_caused_acceptable: ["no", "unclear"]
agent_should_run: true
should_comment: true
label: ci-triage:flaky
label_acceptable: ["ci-triage:flaky", "ci-triage:known-issue", null]
must_mention: ["SearchTest|Nominatim|search_test", "master|flaky|intermittent"]
must_quote: ["SearchTest#test_search_adds_viewbox_param_to_Nominatim_link|NetConnectNotAllowedError"]
must_not: ["\\*\\*Caused by this PR:\\*\\*\\s*yes"]
recommended_action: "Say the same test failed on master earlier the same day; flaky, not caused by the OAuth change."
---

# Expected outcome: CASE-12

Written before any agent run (Phase 1). Regular expressions in `must_*` are matched
case-insensitively against the agent's comment (or noop reason) by `run_eval.py`.

## Justification

Same SearchTest error as CASE-11, Ruby 3.4 only [E:CASE-12 log]; the PR changes OAuth scope views and a helper [E:CASE-12 diff].

## Ground truth (after T, not given to the agent)

* Master Tests failed with the same test at 2026-08-19T11:22Z (run 32247269027) and passed at 17:32Z (run 32282177239).
* A maintainer approved ('Looks good to me, thanks.' 18:43Z) and merged at 18:44Z, before attempt 4 finished; the run had been re-run three times.
