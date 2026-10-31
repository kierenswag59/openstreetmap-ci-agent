---
case: CASE-02
mode: dry-run
output: comment
label: ci-triage:known-issue
item_number: 14
comments_posted: 1
replay: https://github.com/kierenswag59/openstreetmap-ci-agent/actions/runs/41201706631
gate: https://github.com/kierenswag59/openstreetmap-ci-agent/actions/runs/41201729045 (pre_activation success; activation failed at 'Validate ANTHROPIC_API_KEY secret')
capture: https://github.com/kierenswag59/openstreetmap-ci-agent/actions/runs/41201729018
transcript: evals/golden/dryrun/transcripts/CASE-02.md
model: claude-sonnet-5-5
pr: https://github.com/kierenswag59/openstreetmap-ci-agent/pull/14
---

# Actual outcome: CASE-02

Verbatim output (comment body or noop reason) of the run described above:

~~~text
### CI failure triage: Tests / Ruby 3.3, Ruby 3.4, Ruby 4.0

**Category:** F5 (already failing on master / known open issue)
**Caused by this PR:** no. All three jobs fail in "Populate database" with the same `db/structure.sql` diff, and master fails with the same signature. The PR only touches `config/initializers/sentry.rb`, which cannot affect the schema dump.
**Confidence:** high

**Decisive log lines** (verbatim, job `Ruby 3.3`, step `sed -f script/normalise-structure db/structure.sql > db/structure.expected`):
```text
+    changeset_id bigint CONSTRAINT changeset_tags_id_not_null NOT NULL,
+    node_id bigint CONSTRAINT current_node_tags_id_not_null NOT NULL,
+    id bigint CONSTRAINT current_nodes_id_not_null1 NOT NULL,
+    latitude integer CONSTRAINT current_nodes_latitude_not_null1 NOT NULL,
+    way_id bigint CONSTRAINT current_way_nodes_id_not_null NOT NULL,
+    to_user_visible boolean DEFAULT true CONSTRAINT messages_visible_not_null NOT NULL,
```

**Implicated files in this PR:** none: the failing files are not in this PR's diff

**Known issue / master status:** master is `broken` with the same signature ([run](https://github.com/kierenswag59/openstreetmap-ci-agent/actions/runs/41201386528)), and open issue #11 "CI fails on Ubuntu 26.04 runners" describes it: the newer PostgreSQL on `ubuntu-latest` dumps named `CONSTRAINT ..._not_null` clauses that the structure check does not tolerate.

**Recommended next step:** A maintainer should resolve #11 (pin PostgreSQL or make the structure check tolerate the new constraint naming); no change is needed in this PR, and the jobs can be re-run after the fix.

---
<sub>AI-generated first-pass triage by workflow `ci-failure-analyst` (model `claude-sonnet-5-5`).
It can be wrong; maintainers decide. Report a bad comment with a 👎 reaction or by
opening an issue that links it (see docs/RUNBOOK.md).
triage-skill: ci-failure-triage v1 · signature: `4f30d658b61e`</sub>
~~~
