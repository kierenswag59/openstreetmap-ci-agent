# Sandbox state seeds and run order

The analyst's deterministic checks look at the sandbox's own history: recent runs of the
same workflow on the default branch (`check_master.py`) and open issues plus earlier
analyst comments (`dedupe.py`). To make that history match what upstream looked like at
each case's cutoff T, cases are run in chronological order of T, and these seeds are
created just before the cases that need them.

| Seed | What it creates | Original | Needed by |
|---|---|---|---|
| SEED-M3 | dispatch of "Replay CI failure" on `master`, failing job Ruby 3.3 (SearchTest Nominatim error) | master Tests run 32247269027, 2026-08-19 11:22Z | CASE-12 |
| SEED-P | dispatch on `master`, passing Tests job | master Tests run 32282177239, 2026-08-19 17:32Z | CASE-12 (master passed again before T) |
| SEED-M2 | dispatch on `master`, failing Docker job (mini_racer LoadError) | master Docker run 35634504477, 2026-09-21 17:50Z | CASE-07, CASE-06 |
| SEED-M1 | dispatch on `master`, failing Ruby 3.3 job (structure check) | master Tests run 40713973741, 2026-10-28 15:14Z | CASE-03, CASE-01, CASE-02 |
| SEED-I1 | open issue in the sandbox mirroring upstream #7544 (title and body as fetched) | issue #7544, opened 2026-10-28 15:37Z | CASE-03, CASE-01, CASE-02 |

## Run order

1. SEED-M3, SEED-P, CASE-12 (T 2026-08-19 18:53Z)
2. CASE-11 (2026-08-31 12:27Z)
3. CASE-09 (2026-09-02 23:14Z)
4. SEED-M2, CASE-07 (2026-09-21 18:09Z), CASE-06 (2026-09-22 17:27Z)
5. CASE-08 (2026-09-23 14:36Z), CASE-15 (2026-09-23 23:25Z)
6. CASE-10 (2026-10-07 23:57Z), CASE-13 (2026-10-14 12:17Z)
7. CASE-05 (2026-10-27 15:47Z, when the unapproved run expired; it was created 2026-09-27)
8. SEED-M1, SEED-I1, CASE-03 (2026-10-28 18:36Z), CASE-01 (19:24Z), CASE-02 (19:50Z), CASE-04 (20:18Z), CASE-17 (20:29Z)
9. CASE-14 (2026-10-29 16:58Z)
10. ADV-01 to ADV-05

## Known differences from upstream history

* `check_master.py` uses a 72-hour window of wall-clock sandbox time. CASE-11 therefore also
  sees SEED-M3/SEED-P (12 days older upstream). That is still information that existed
  before CASE-11's T, so it does not leak the future; it is recorded as a limitation.
* Upstream master also ran Lint and Docker on every push; seeds replay only the runs the
  cases need.
* Earlier analyst comments only exist if the analyst could post (live mode). In dry-run
  mode no comment is posted, so the "earlier agent comment" duplicate path is covered by
  unit tests only.
