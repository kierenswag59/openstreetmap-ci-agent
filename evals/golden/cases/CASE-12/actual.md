---
case: CASE-12
mode: dry-run
output: comment
label: ci-triage:flaky
item_number: 1
comments_posted: 1
replay: https://github.com/kierenswag59/openstreetmap-ci-agent/actions/runs/41200034576
gate: https://github.com/kierenswag59/openstreetmap-ci-agent/actions/runs/41200057721 (pre_activation success; activation failed at 'Validate ANTHROPIC_API_KEY secret')
capture: https://github.com/kierenswag59/openstreetmap-ci-agent/actions/runs/41200057665
transcript: evals/golden/dryrun/transcripts/CASE-12.md
model: claude-sonnet-5-5
pr: https://github.com/kierenswag59/openstreetmap-ci-agent/pull/1
---

# Actual outcome: CASE-12

Verbatim output (comment body or noop reason) of the run described above:

~~~text
### CI failure triage: Replay eval/CASE-12 / Ruby 3.4

**Category:** F6 (flaky or infrastructure failure)
**Caused by this PR:** no. A single system test failed with a WebMock "Real HTTP connections are disabled" error for a Nominatim request. None of the referenced files (`app/controllers/searches/*`, `test/system/search_test.rb`) are in this PR's diff, which only touches OAuth scope rendering. The Ruby 3.3 and Ruby 4.0 jobs passed on the same commit.
**Confidence:** medium

**Decisive log lines** (verbatim, job `Ruby 3.4`, step `Run tests`):
```text
Error:
SearchTest#test_search_adds_viewbox_param_to_Nominatim_link:
WebMock::NetConnectNotAllowedError: Real HTTP connections are disabled. Unregistered request: GET https://nominatim.openstreetmap.org/search?accept-language=en&extratags=1&format=xml&q=paris&viewbox=-30.849609375000004,65.67638148211446,30.673828125000004,30.977609093348686 with headers {'Accept'=>'*/*', 'Accept-Encoding'=>'gzip;q=1.0,deflate;q=0.6,identity;q=0.3', 'User-Agent'=>'test.host'}
    app/controllers/searches/queries_controller.rb:12:in 'Searches::QueriesController#fetch_text'
    app/controllers/searches/nominatim_queries_controller.rb:9:in 'Searches::NominatimQueriesController#create'
bin/rails test test/system/search_test.rb:71
2885 runs, 1230510 assertions, 0 failures, 1 errors, 0 skips
```

**Implicated files in this PR:** none: the failing files are not in this PR's diff

**Known issue / master status:** master verdict "seen": the same signature failed once on the default branch (https://github.com/kierenswag59/openstreetmap-ci-agent/actions/runs/41199941841) and the latest master run succeeded. No matching open issue.

**Recommended next step:** A maintainer can re-run the failed Ruby 3.4 job; if the search test fails again, investigate the unstubbed Nominatim request in `test/system/search_test.rb:71` (probably an unstubbed request that depends on test ordering).

---
<sub>AI-generated first-pass triage by workflow `ci-failure-analyst` (model `claude-sonnet-5-5`).
It can be wrong; maintainers decide. Report a bad comment with a 👎 reaction or by
opening an issue that links it (see docs/RUNBOOK.md).
triage-skill: ci-failure-triage v1 · signature: `ff6ebeb146bd`</sub>
~~~
