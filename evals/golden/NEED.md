# Need for automation: what was measured

All numbers come from the public GitHub Actions REST API of
`openstreetmap/openstreetmap-website`, fetched on 2026-10-31 (see SOURCES.md), plus the
Actions list pages pasted in evidence section A [E:A1-A5].

## Measurement

* **Filter:** `GET /repos/openstreetmap/openstreetmap-website/actions/runs?event=pull_request&created=<month>`
  for 2026-08-01..08-31, 09-01..09-30 and 10-01..10-29 (each under the API's 1,000-result cap),
  keeping the four PR-triggered CI workflows Tests, Lint, Docker and Development Container.
  Master history: `...?branch=master&event=push&created=2026-07-25..2026-10-29`.
* **Period:** 2026-08-01 to 2026-10-29 UTC, 12.86 weeks. July is excluded because its logs
  had expired (G2: "The logs for this run have expired"), so July failures cannot be analysed.
* **UI cross-check:** the Actions list filtered `is:failure event:pull_request` showed
  "1064 workflow run results" across all time [E:A1, page 1 header].

## Raw numbers and derived rates

| Metric | Value |
|---|---|
| PR-triggered runs (4 workflows) | 1,748 |
| Failed PR-triggered runs | 317 (Tests 97, Docker 90, Lint 75, Development Container 55) |
| Failed PR runs per week | 24.7 |
| Distinct PR branches (head repo + branch) | 179 |
| ... with at least one failed run | 75 (42%) |
| Failed PR runs where the same workflow also failed on master in the previous 24 h | 72 (23%) |
| Failed runs followed by a new push to the same branch | 216 of 317 |
| Median time from a failed run to the next push | 1.2 h (IQR 0.1 h to 23.6 h) |
| Failed runs from Dependabot | 63 (20%) |

Script: the computation is reproduced in `evals/golden/tools/need_metrics.py`.

## Limitations

1. The Actions UI caps totals (all PR runs show "2500+") and pages back only ~42 pages [P:4];
   the API counts here avoid the UI cap but each monthly query is capped at 1,000 results.
2. Re-runs and each workflow count separately, so one push can produce four failed runs [P:4].
3. Dependabot runs and runs that never started (approval required/expired) are included [P:4].
4. Late October is inflated by the Ubuntu 26.04 runner change (#7544) [P:4].
5. "Also failed on master within 24 h" is a proxy: it does not check that the error matched.
6. "Time to next push" measures contributor reaction, not time to understand the failure; a
   push may be unrelated to the failure, and 101 failures had no later push at all.
7. PR branches are keyed by head repository and branch name, because `pull_requests` is
   empty for fork PRs in the runs API; a reused branch name merges two PRs.
8. Sampling bias in the case set: cases were picked to cover every category (not at random),
   July cases were replaced because logs expired, and two PRs (#7545, #7546) appear twice.
