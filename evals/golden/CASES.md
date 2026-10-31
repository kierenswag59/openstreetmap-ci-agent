# Case set: selection, cutoffs and replacements

Cutoff T for every case is the time the failing run completed: the latest `completed_at` of
its failed jobs from `GET /repos/openstreetmap/openstreetmap-website/actions/runs/<id>/jobs`
(evidence G1, re-fetched 2026-10-31). Exceptions are noted.

| Case | PR | Run | Workflow / job / step | T (UTC) | Category | PR caused | Rationale (log line) |
|---|---|---|---|---|---|---|---|
| CASE-01 | #7546 | 40753633422 | Tests / Ruby 3.3-4.0 / Populate database | 2026-10-28 19:24:10 | F4 | no | `+    way_id bigint CONSTRAINT ways_id_not_null NOT NULL,` |
| CASE-02 | #7547 | 40757514945 | Tests / Ruby 3.3-4.0 / Populate database | 2026-10-28 19:50:26 | F4 (dup) | no | same CONSTRAINT diff; issue #7544 open |
| CASE-03 | #7545 v1 | 40746377705 | Tests / Ruby 3.3-4.0 / Populate database | 2026-10-28 18:36:00 | F4 | no | `+    id bigint CONSTRAINT current_nodes_id_not_null1 NOT NULL,` |
| CASE-04 | (push) | 40761769826 | Tests / Ruby 3.3-4.0 / Populate database | 2026-10-28 20:18:03 | F7 | n/a | push to master: agent must not run |
| CASE-05 | #7432 | 36330556125 | Tests / none / none | 2026-10-27 15:47:23 (run updated_at) | F7 | n/a | "required approval but was not approved before it expired" |
| CASE-06 | #7398 | 35760389282 | Docker / Docker / Prepare Database | 2026-09-22 17:27:24 | F5 | no | `LoadError: ... undefined symbol: __isoc23_strtoll` |
| CASE-07 | #7399 | 35636239291 | Docker / Docker / Prepare Database | 2026-09-21 18:09:34 | F5 | no | same LoadError, master failing |
| CASE-08 | #7410 | 35875254785 | Lint / ESLint / Run eslint | 2026-09-23 14:36:22 | F2 | yes | `13:13 error 'unit' is never reassigned. Use 'const' instead prefer-const` |
| CASE-09 | #7355 | 33694039489 | Lint / RuboCop / Run rubocop | 2026-09-02 23:14:06 | F3 | yes | `Style/DirectiveScope`, `Layout/ExtraSpacing` after rubocop 1.90 |
| CASE-10 | #7480 | 37705152851 | Tests / Ruby 3.3-4.0 / Setup ruby | 2026-10-07 23:57:55 | F3 | unclear | "lockfile can't be updated because frozen mode is set" |
| CASE-11 | #7350 | 33391131716 | Tests / Ruby 3.3 / Run tests | 2026-08-31 12:27:07 | F6 | no | `SearchTest#test_search_adds_viewbox_param_to_Nominatim_link` |
| CASE-12 | #7328 | 32283669556 | Tests / Ruby 3.4 / Run tests | 2026-08-19 18:53:30 (attempt 4) | F6 | no | same SearchTest error; failed on master the same day |
| CASE-13 | #7490 | 38562633179 | Lint / ESLint / Run eslint | 2026-10-14 12:17:59 | F2 | yes | `172:4 error Newline required at end of file ... @stylistic/eol-last` |
| CASE-14 | #7546 | 40916734387 | Lint / RuboCop / Run rubocop | 2026-10-29 16:58:41 | F2 | yes | `app/models/user.rb:53:1: R: Metrics/ClassLength ... [357/356]` |
| CASE-15 | #7421 | 35933394011 | Lint / Rails Annotate Models / Fail if model annotations are out of date | 2026-09-23 23:25:24 | F3 | yes | `+#  index_acls_on_address  (address inet_ops) USING gist` |
| CASE-17 | #7545 final | 40762407177 | Tests / all passed | 2026-10-28 20:29:41 (run end) | F7 | n/a | passing run: agent must not run |

Required coverage: >= 10 real cases (16), >= 2 no-action (CASE-04, CASE-05, CASE-17),
>= 1 environment or master-broken (CASE-01, 03, 06, 07), >= 1 Dependabot (CASE-09, 10, 15),
>= 1 duplicate (CASE-02; also CASE-06/07 and CASE-11/12 share signatures), >= 1 passing run (CASE-17).

## Rejected or replaced cases

| Original | Why rejected | Replacement |
|---|---|---|
| CASE-09 (run 28982171685, PR #7218, 8 Jul) | logs expired ("The logs for this run have expired") [E:G2] | R-09: run 33694039489, PR #7355 |
| CASE-10 (run 29965444993, PR #7258, 22 Jul) | logs expired [E:G2] | R-10: run 37705152851, PR #7480 |
| CASE-11 (run 30007286075, PR #7263, 23 Jul) | logs expired [E:G2] | R-11: run 33391131716, PR #7350 |
| CASE-12 (run 29591625082, PR #7146, 17 Jul) | logs expired [E:G2] | R-12: run 32283669556, PR #7328 |
| CASE-13 (run 28798980683, PR #7148, 6 Jul) | logs expired [E:G2] | R-13: run 38562633179, PR #7490 |
| CASE-16 (flaky, not collected) | no run identified [E:CASE-16 empty] | covered by CASE-11/CASE-12 (F6) |
| CASE-18 (spare, not collected) | dropped [E:G1] | none needed |

In this repository the replacements keep the original case numbers (CASE-09 to CASE-13 are
R-09 to R-13). CASE-16 and CASE-18 do not exist.
