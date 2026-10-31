---
case: CASE-10
category: F3
category_acceptable: ["F3"]
pr_caused: unclear
pr_caused_acceptable: ["unclear", "yes"]
agent_should_run: true
should_comment: true
label: ci-triage:dependency
label_acceptable: ["ci-triage:dependency", null]
must_mention: ["Gemfile\\.lock|lockfile", "frozen"]
must_quote: ["frozen mode|lockfile can't be updated"]
must_not: []
recommended_action: "Ask Dependabot to rebase or recreate the PR so Gemfile.lock matches the Gemfile on master."
---

# Expected outcome: CASE-10

Written before any agent run (Phase 1). Regular expressions in `must_*` are matched
case-insensitively against the agent's comment (or noop reason) by `run_eval.py`.

## Justification

All Ruby jobs fail in Setup ruby: 'The dependencies in your gemfile changed, but the lockfile can't be updated because frozen mode is set' and bundle exits 16 [E:CASE-10 log]. The PR changes only Gemfile.lock [E:CASE-10 diff] and its merge base is master commit 8524e874 'Pin dartsass-sprockets', which changed the Gemfile 14 minutes earlier.

## Ground truth (after T, not given to the agent)

* Master's own runs after 8524e874 were cancelled, so master was not visibly red at T.
* Next morning a maintainer commented '@dependabot rebase' (06:17Z, 06:19Z); Dependabot closed the PR as no longer needed (06:28Z).
* Master itself hit the same bundler exit code 16 at 06:17Z on 2026-10-08 ('Pin google-protobuf', run 37736780038, evidence E4) and was fixed by 'Update lockfile' at 06:19Z.
* So the lockfile in the PR was incompatible with the Gemfile it was tested against; whether Dependabot or the master pin is 'at fault' is genuinely unclear.
