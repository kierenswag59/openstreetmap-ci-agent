---
case: CASE-11
category: F6
category_acceptable: ["F6", "F5"]
pr_caused: no
pr_caused_acceptable: ["no"]
agent_should_run: true
should_comment: true
label: ci-triage:flaky
label_acceptable: ["ci-triage:flaky", "ci-triage:known-issue", null]
must_mention: ["SearchTest|Nominatim|search_test", "flaky|intermittent|only (one|Ruby 3\\.3)|re-?run"]
must_quote: ["SearchTest#test_search_adds_viewbox_param_to_Nominatim_link|NetConnectNotAllowedError"]
must_not: ["\\*\\*Caused by this PR:\\*\\*\\s*yes"]
recommended_action: "Treat as a flaky system test (real HTTP to Nominatim blocked by WebMock); a maintainer can re-run the Ruby 3.3 job."
---

# Expected outcome: CASE-11

Written before any agent run (Phase 1). Regular expressions in `must_*` are matched
case-insensitively against the agent's comment (or noop reason) by `run_eval.py`.

## Justification

One error, `SearchTest#test_search_adds_viewbox_param_to_Nominatim_link: WebMock::NetConnectNotAllowedError`, in Ruby 3.3 only [E:CASE-11 log]; the PR is a Translatewiki locale update [E:CASE-11 diff].

## Ground truth (after T, not given to the agent)

* The PR merged at 2026-08-31T16:22Z and master Tests passed on the merge (run 33413725883).
* The same test failed on master on 2026-08-19 (run 32247269027) and on PR #7328 (CASE-12).
