"""Unit tests for the ci-failure-triage helper scripts.

Run from the repository root:
    python3 -m unittest discover -s .claude/skills/ci-failure-triage/scripts/tests -v

Fixtures in fixtures/ are verbatim excerpts of real openstreetmap-website job
logs and diffs (see evals/golden/SOURCES.md for the runs they come from).
"""

import io
import json
import os
import sys
import unittest
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import check_master  # noqa: E402
import collect_context  # noqa: E402
import dedupe  # noqa: E402
import extract_failure  # noqa: E402
import map_to_diff  # noqa: E402
import validate_output  # noqa: E402

FX = os.path.join(HERE, "fixtures")


def fixture(name):
    with open(os.path.join(FX, name), encoding="utf-8") as fh:
        return fh.read()


GOOD_COMMENT = """### CI failure triage: Lint / ESLint

**Category:** F2 (lint or static analysis caused by the PR)
**Caused by this PR:** yes. The two flagged lines were added by this PR.
**Confidence:** high

**Decisive log lines** (verbatim, job `ESLint`, step `bundle exec rails eslint`):
```text
##[error]  13:13  error  'unit' is never reassigned. Use 'const' instead                prefer-const
##[error]  14:13  error  'unitTranslationKey' is never reassigned. Use 'const' instead  prefer-const
```

**Implicated files in this PR:** `app/assets/javascripts/leaflet.locate.js:13`, `:14` (both lines added here)

**Known issue / master status:** master clean for this signature; no matching open issue.

**Recommended next step:** Change the two `let` declarations to `const` and push again.

---
<sub>AI-generated first-pass triage by workflow `ci-failure-analyst` (model `claude-sonnet-5-5`).
It can be wrong. Report a bad comment with a thumbs-down reaction.
triage-skill: ci-failure-triage v1 · signature: `9bdc53c2148e`</sub>
"""


class ExtractFailureTest(unittest.TestCase):
    def test_eslint_lines_and_rule(self):
        r = extract_failure.extract(fixture("eslint_case08.log"), "ESLint")
        self.assertEqual(r["failed_step"], "bundle exec rails eslint")
        self.assertEqual(r["kind"], "eslint")
        self.assertEqual(r["key_tokens"], ["prefer-const"])
        self.assertTrue(any("leaflet.locate.js" in l for l in r["decisive_lines"]))
        self.assertLessEqual(len(r["decisive_lines"]), 15)

    def test_strips_timestamps_and_ansi(self):
        lines = extract_failure.clean_log(fixture("eslint_case08.log"))
        self.assertFalse(any(l.startswith("2026-") for l in lines))
        self.assertFalse(any("\x1b[" in l for l in lines))

    def test_rubocop_cop(self):
        r = extract_failure.extract(fixture("rubocop_case14.log"))
        self.assertEqual(r["kind"], "rubocop")
        self.assertEqual(r["key_tokens"], ["Metrics/ClassLength"])
        self.assertIn("app/models/user.rb:53:1: R: Metrics/ClassLength: Class has too many lines. [357/356]",
                      r["decisive_lines"])

    def test_minitest_test_name(self):
        r = extract_failure.extract(fixture("minitest_case11.log"))
        self.assertEqual(r["kind"], "minitest")
        self.assertEqual(r["key_tokens"], ["SearchTest#test_search_adds_viewbox_param_to_Nominatim_link"])

    def test_structure_signature_ignores_constraint_names(self):
        r1 = extract_failure.extract(fixture("structure_case01.log"))
        self.assertEqual(r1["kind"], "structure-diff")
        renamed = fixture("structure_case01.log").replace("_not_null", "_nn_renamed")
        r2 = extract_failure.extract(renamed)
        self.assertEqual(r1["signature"], r2["signature"])

    def test_bundler_frozen(self):
        r = extract_failure.extract(fixture("bundler_case10.log"))
        self.assertEqual(r["kind"], "bundler")
        self.assertIn("frozen-lockfile", r["key_tokens"])

    def test_annotation_drift(self):
        r = extract_failure.extract(fixture("annotate_case15.log"))
        self.assertEqual(r["kind"], "annotation-drift")
        self.assertIn("app/models/acl.rb", r["key_tokens"])

    def test_signature_is_stable_across_timestamps(self):
        a = fixture("rubocop_case14.log")
        b = a.replace("2026-10-29T16:58", "2027-01-01T00:00")
        self.assertEqual(extract_failure.extract(a)["signature"], extract_failure.extract(b)["signature"])

    def test_summary_line_kept_past_cap(self):
        block = ["##[group]Run bundle exec rails test:all"]
        for i in range(20):
            block += ["Failure:", f"BrowseHelperTest#test_case_{i:02d} [test/helpers/b_test.rb:{i}]:",
                      f"bin/rails test test/helpers/b_test.rb:{i}"]
        block += ["2889 runs, 1230510 assertions, 20 failures, 0 errors, 0 skips",
                  "##[error]Process completed with exit code 1."]
        r = extract_failure.extract("\n".join(block))
        self.assertEqual(len(r["decisive_lines"]), 15)
        self.assertIn("20 failures", r["decisive_lines"][-1])

    def test_cli_help(self):
        with self.assertRaises(SystemExit) as cm, redirect_stdout(io.StringIO()):
            extract_failure.main(["--help"])
        self.assertEqual(cm.exception.code, 0)


class MapToDiffTest(unittest.TestCase):
    def test_eslint_lines_changed_by_pr(self):
        r = map_to_diff.match(fixture("case08.diff"), [fixture("eslint_case08.log")])
        self.assertTrue(r["any_changed_line_referenced"])
        refs = {(x["file"], x["line"]) for x in r["references"] if x["line_changed_by_pr"]}
        self.assertIn(("app/assets/javascripts/leaflet.locate.js", 13), refs)
        self.assertIn(("app/assets/javascripts/leaflet.locate.js", 14), refs)

    def test_file_not_in_diff(self):
        r = map_to_diff.match(fixture("case08.diff"), [fixture("rubocop_case14.log")])
        self.assertFalse(r["any_reference_in_diff"])

    def test_parse_diff_new_line_numbers(self):
        d = map_to_diff.parse_diff("diff --git a/x.rb b/x.rb\n--- a/x.rb\n+++ b/x.rb\n@@ -1,2 +1,3 @@\n a\n+b\n c\n")
        self.assertEqual(d, {"x.rb": {2}})


class CheckMasterTest(unittest.TestCase):
    RUNS = [
        {"id": 3, "created_at": "2026-10-28T18:39:47Z", "conclusion": "failure", "failed": [{"job": "Ruby 3.3", "signature": "aaaaaaaaaaaa"}]},
        {"id": 2, "created_at": "2026-10-28T15:14:44Z", "conclusion": "failure", "failed": [{"job": "Ruby 3.3", "signature": "aaaaaaaaaaaa"}]},
        {"id": 1, "created_at": "2026-10-27T23:43:58Z", "conclusion": "success", "failed": []},
    ]

    def test_broken(self):
        self.assertEqual(check_master.check(self.RUNS, "aaaaaaaaaaaa", "2026-10-28T19:21:55Z")["verdict"], "broken")

    def test_cutoff_hides_future_runs(self):
        r = check_master.check(self.RUNS, "aaaaaaaaaaaa", "2026-10-28T15:00:00Z")
        self.assertEqual(r["verdict"], "clean")

    def test_seen_then_fixed(self):
        runs = [{"id": 9, "created_at": "2026-10-29T00:00:00Z", "conclusion": "success", "failed": []}] + self.RUNS
        self.assertEqual(check_master.check(runs, "aaaaaaaaaaaa", "2026-10-29T01:00:00Z")["verdict"], "seen")

    def test_unknown(self):
        self.assertEqual(check_master.check([], "x")["verdict"], "unknown")


class DedupeTest(unittest.TestCase):
    def test_issue_keyword_match(self):
        issues = [{"number": 1, "title": "CI fails on Ubuntu 26.04 runners",
                   "body": "way_id bigint CONSTRAINT ways_id_not_null NOT NULL in db/structure.sql"}]
        r = dedupe.dedupe(issues, [], "4f30d658b61e", ["CONSTRAINT <name> NOT NULL", "db/structure.sql"])
        self.assertTrue(r["duplicate"])
        self.assertEqual(r["issues"][0]["number"], 1)

    def test_unrelated_issue(self):
        issues = [{"number": 2, "title": "Map tiles blurry", "body": "zoom level 18"}]
        self.assertFalse(dedupe.dedupe(issues, [], "abc", ["Metrics/ClassLength", "app/models/user.rb"])["duplicate"])

    def test_earlier_agent_comment(self):
        comments = [{"html_url": "u", "body": "x\ntriage-skill: ci-failure-triage v1 · signature: `ff6ebeb146bd`",
                     "pr_number": 5}]
        r = dedupe.dedupe([], comments, "ff6ebeb146bd", [])
        self.assertEqual(r["earlier_agent_comments"][0]["pr_number"], 5)

    def test_earlier_agent_comment_as_posted(self):
        # verbatim footer of the live comment on sandbox PR #6 (run 41288083676)
        comments = [{"html_url": "u", "pr_number": 6, "body": "triage-skill: ci-failure-triage v1 \u00b7 "
                     "signature: <code>9bdc53c2148e</code></sub>"}]
        self.assertEqual(dedupe.dedupe([], comments, "9bdc53c2148e", [])["earlier_agent_comments"][0]["pr_number"], 6)


class ValidateOutputTest(unittest.TestCase):
    def test_good_comment(self):
        r = validate_output.validate_comment(GOOD_COMMENT, "ci-triage:pr-related")
        self.assertTrue(r["ok"], r["errors"])

    def test_label_not_allowed(self):
        r = validate_output.validate_comment(GOOD_COMMENT, "approved")
        self.assertFalse(r["ok"])

    def test_label_category_mismatch(self):
        self.assertFalse(validate_output.validate_comment(GOOD_COMMENT, "ci-triage:flaky")["ok"])

    def test_too_many_quoted_lines(self):
        body = GOOD_COMMENT.replace("```text\n", "```text\n" + "x\n" * 15)
        self.assertFalse(validate_output.validate_comment(body)["ok"])

    def test_forbidden_language_and_secret(self):
        self.assertFalse(validate_output.validate_comment(GOOD_COMMENT + "\nLGTM, merging")["ok"])
        self.assertFalse(validate_output.validate_comment(GOOD_COMMENT + "\nghp_" + "a" * 36)["ok"])

    def test_mention(self):
        self.assertFalse(validate_output.validate_comment(GOOD_COMMENT + "\ncc @tomhughes")["ok"])

    def test_missing_marker(self):
        self.assertFalse(validate_output.validate_comment(GOOD_COMMENT.replace("triage-skill", "x"))["ok"])

    def test_noop(self):
        self.assertTrue(validate_output.validate_noop(
            "F7: the run has no jobs. triage-skill: ci-failure-triage v1")["ok"])
        self.assertFalse(validate_output.validate_noop("nothing")["ok"])

    def test_cli_exit_code(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(validate_output.main(["--body", GOOD_COMMENT]), 0)
            self.assertEqual(validate_output.main(["--body", "hello"]), 1)


class CollectContextTest(unittest.TestCase):
    def test_gate_no_jobs(self):
        jobs = json.loads(fixture("case05_jobs.json"))["jobs"]
        self.assertIn("never started", collect_context.gate({"conclusion": "failure"}, jobs))

    def test_gate_success(self):
        self.assertIn("not a failure", collect_context.gate({"conclusion": "success"}, [{"conclusion": "success"}]))

    def test_gate_failed_job(self):
        self.assertIsNone(collect_context.gate({"conclusion": "failure"}, [{"conclusion": "failure"}]))

    def test_resolve_pr_payload_then_fallbacks(self):
        run = {"pull_requests": [{"number": 7}], "head_sha": "s"}
        self.assertEqual(collect_context.resolve_pr(run, [], []), (7, "event payload"))
        fork = {"pull_requests": [], "head_sha": "s", "head_branch": "b",
                "head_repository": {"full_name": "someone/fork"}}
        pulls = [{"number": 9, "head": {"sha": "other", "ref": "b", "repo": {"full_name": "someone/fork"}}}]
        self.assertEqual(collect_context.resolve_pr(fork, [], [], pulls)[0], 9)
        self.assertEqual(collect_context.resolve_pr(fork, [], [])[0], None)


if __name__ == "__main__":
    unittest.main()
