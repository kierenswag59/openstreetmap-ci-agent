---
case: CASE-03
mode: dry-run
output: comment
label: ci-triage:known-issue
item_number: 12
comments_posted: 1
replay: https://github.com/kierenswag59/openstreetmap-ci-agent/actions/runs/41201433447
gate: https://github.com/kierenswag59/openstreetmap-ci-agent/actions/runs/41201456537 (pre_activation success; activation failed at 'Validate ANTHROPIC_API_KEY secret')
capture: https://github.com/kierenswag59/openstreetmap-ci-agent/actions/runs/41201456417
transcript: evals/golden/dryrun/transcripts/CASE-03.md
model: claude-sonnet-5-5
pr: https://github.com/kierenswag59/openstreetmap-ci-agent/pull/12
---

# Actual outcome: CASE-03

Verbatim output (comment body or noop reason) of the run described above:

~~~text
### CI failure triage: Tests / Ruby 3.3, Ruby 3.4, Ruby 4.0

**Category:** F5 (already failing on master / known open issue)
**Caused by this PR:** no. The same structure-diff signature fails on the default branch and is tracked in #11 (Ubuntu 26.04 runner with a newer PostgreSQL that names NOT NULL constraints in the dump). The PR's only change, `script/normalise-structure`, is an attempt to fix it. The attempt does not cover the remaining output, see below.
**Confidence:** high

**Decisive log lines** (verbatim, job `Ruby 3.4`, step `sed -f script/normalise-structure db/structure.sql > db/structure.expected`):
```text
+    id bigint CONSTRAINT current_nodes_id_not_null1 NOT NULL,
+    latitude integer CONSTRAINT current_nodes_latitude_not_null1 NOT NULL,
+    longitude integer CONSTRAINT current_nodes_longitude_not_null1 NOT NULL,
+    changeset_id bigint CONSTRAINT current_nodes_user_id_not_null1 NOT NULL,
+    node_id bigint CONSTRAINT nodes_id_not_null1 NOT NULL,
+    latitude integer CONSTRAINT nodes_latitude_not_null1 NOT NULL,
```

**Implicated files in this PR:** none of the failing lines are in the PR's diff; the PR touches only `script/normalise-structure`, which is the script that produces the comparison.

**Known issue / master status:** master verdict `broken` with the same signature (run https://github.com/kierenswag59/openstreetmap-ci-agent/actions/runs/41201386528); matches open issue #11 'CI fails on Ubuntu 26.04 runners'.

**Recommended next step:** Contributor: the new `sed` pattern `[a-z][a-z_]*` does not allow digits, so names such as `current_nodes_id_not_null1` (the remaining lines above) are not matched. Widen the pattern (for example `[a-z0-9_]*`) and re-run.

---
<sub>AI-generated first-pass triage by workflow `ci-failure-analyst` (model `claude-sonnet-5-5`).
It can be wrong; maintainers decide. Report a bad comment with a 👎 reaction or by
opening an issue that links it (see docs/RUNBOOK.md).
triage-skill: ci-failure-triage v1 · signature: `4f30d658b61e`</sub>
~~~
