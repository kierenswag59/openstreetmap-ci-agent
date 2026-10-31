---
case: CASE-01
mode: dry-run
output: comment
label: ci-triage:known-issue
item_number: 13
comments_posted: 1
replay: https://github.com/kierenswag59/openstreetmap-ci-agent/actions/runs/41201564444
gate: https://github.com/kierenswag59/openstreetmap-ci-agent/actions/runs/41201598035 (pre_activation success; activation failed at 'Validate ANTHROPIC_API_KEY secret')
capture: https://github.com/kierenswag59/openstreetmap-ci-agent/actions/runs/41201598083
transcript: evals/golden/dryrun/transcripts/CASE-01.md
model: claude-sonnet-5-5
pr: https://github.com/kierenswag59/openstreetmap-ci-agent/pull/13
---

# Actual outcome: CASE-01

Verbatim output (comment body or noop reason) of the run described above:

~~~text
### CI failure triage: Replay eval/CASE-01 (Tests) / Ruby 3.3, Ruby 3.4, Ruby 4.0

**Category:** F5 (already failing on master / known open issue; the underlying cause is a runner PostgreSQL change)
**Caused by this PR:** no. The "Populate database" structure check fails identically on all three Ruby jobs, master fails with the same signature, and open issue #11 describes it. The PR diff touches none of the referenced files.
**Confidence:** high

**Decisive log lines** (verbatim, job `Ruby 3.3`, step `sed -f script/normalise-structure db/structure.sql > db/structure.expected`):
```text
+    changeset_id bigint CONSTRAINT changeset_tags_id_not_null NOT NULL,
+    node_id bigint CONSTRAINT current_node_tags_id_not_null NOT NULL,
+    id bigint CONSTRAINT current_nodes_id_not_null1 NOT NULL,
+    latitude integer CONSTRAINT current_nodes_latitude_not_null1 NOT NULL,
+    longitude integer CONSTRAINT current_nodes_longitude_not_null1 NOT NULL,
+    changeset_id bigint CONSTRAINT current_nodes_user_id_not_null1 NOT NULL,
+    visible boolean CONSTRAINT current_nodes_visible_not_null1 NOT NULL,
+    relation_id bigint CONSTRAINT current_relation_members_id_not_null NOT NULL,
+    way_id bigint CONSTRAINT current_way_nodes_id_not_null NOT NULL,
+    to_user_visible boolean DEFAULT true CONSTRAINT messages_visible_not_null NOT NULL,
```

**Implicated files in this PR:** none: the failing files are not in this PR's diff

**Known issue / master status:** master is broken with the same signature ([run](https://github.com/kierenswag59/openstreetmap-ci-agent/actions/runs/41201386528)); matches open issue #11 "CI fails on Ubuntu 26.04 runners" (newer PostgreSQL on `ubuntu-latest` dumps named NOT NULL constraints into `db/structure.sql`).

**Recommended next step:** A maintainer should resolve #11 (pin PostgreSQL or make the structure check tolerate the difference); this PR needs no change for this failure, and its other test and lint results should be read once the check is fixed.

---
<sub>AI-generated first-pass triage by workflow `ci-failure-analyst` (model `claude-sonnet-5-5`).
It can be wrong; maintainers decide. Report a bad comment with a 👎 reaction or by
opening an issue that links it (see docs/RUNBOOK.md).
triage-skill: ci-failure-triage v1 · signature: `4f30d658b61e`</sub>
~~~
