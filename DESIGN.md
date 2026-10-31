# DESIGN: first-pass CI-failure analyst for openstreetmap-website

Sandbox `kierenswag59/openstreetmap-ci-agent`, upstream pinned at `729cdc3d`. Engine: Claude
through GitHub Agentic Workflows (gh-aw v1.0.1). Detail: `docs/GOVERNANCE.md`, `docs/RUNBOOK.md`,
`evals/golden/README.md`, `evals/golden/ANALYSIS.md`.

## Why this workflow

From 1 Aug to 29 Oct 2026, 317 of 1,748 PR-triggered CI runs failed (24.7 per week); 42% of
PR branches hit at least one failure; 23% of failures coincided with the same workflow failing
on master within 24 h; 63 came from Dependabot; contributors pushed again a median 1.2 h after
a failure (`evals/golden/NEED.md`, with the API filters and limitations: re-runs counted
separately, the 26.04 runner change inflating October, a proxy for "same cause").
The Actions annotation says only "Process completed with exit code 1"; the real error sits in
a 1,000 to 6,000-line log. Danger already labels big PRs and lockfile slips cheaply and
deterministically, but it never reads logs. Triage needs judgement a regex lacks: is this
ESLint error on a line the PR added, a new cop flagging old code after a bump, a flaky test
that also failed on master, or a runner change everyone is hitting?

## Why the controls fit the risks

The agent reads untrusted text (PR body, diff, logs, issues) and its only useful output is a
comment, so the main risks are prompt injection, false blame of contributors, spam and cost.
Hence: read-only agent token and `strict: true`; writes only through two safe outputs with
`max: 1`; a 5-label allow-list; no file editing and a 4-tool GitHub MCP list; firewall to
default and GitHub domains; threat detection failing closed; deterministic data collection
before the model (`collect_context.py`), so the model starts from facts (failed step, signature,
diff mapping, master verdict, duplicates) and its inputs are archived; "unclear" over blame;
a sparse checkout so the agent cannot read the expected answers in `evals/`.

## Rejected alternative

A Danger/regex rule per known error (cheap, deterministic, no hallucination). Rejected as the
main mechanism because the hard part is attribution across logs, diffs and master history,
and failures change form (26.04 constraint names, a glibc symbol, new RuboCop cops). The
regex idea survives where it is enough: `extract_failure.py`, `map_to_diff.py`,
`check_master.py` and `dedupe.py` are deterministic and unit-tested (33 tests).
Also rejected: an agent that pushes fixes; it needs write access and turns a wrong guess into a commit.

## Deliberately prevented

None of the dangerous safe outputs is enabled: no close-issue, close-pull-request,
merge-pull-request, push-to-pull-request-branch, create-pull-request, approve-workflow-run,
dispatch-workflow, hide-comment or remove-labels (`ci-failure-analyst.md:97-117`). The agent
cannot push, edit code (`edit: false`), comment on issues (`issues: false`), add labels outside
the list, fetch URLs (WebFetch/WebSearch disallowed, firewall) or see the GitHub token.

## What the tests revealed

16 real cases (14 failures, a push run, a passing run) and 5 adversarial PRs were replayed in
the sandbox through the real trigger: 21 PRs, 25 replays, 21 analyst runs, 20 collector runs.
The gates worked for real: CASE-04 (non-PR event) and CASE-17 (passing run) were skipped, and
the kill switch skipped, cancelled and blocked runs (`evals/golden/logs/killswitch.log`).
The agent job never started: the sandbox has no `ANTHROPIC_API_KEY`, so activation stopped at
"Validate ANTHROPIC_API_KEY secret" every time. Judgement was therefore a dry run: 19 fresh
`claude-sonnet-5-5` sessions given the same prompt, sparse-checkout files and the real bundles.
Result: 20 of 21 PASS, category 18/18, cause acceptable 18/18, evidence 18/18, false blame 0,
safety violations 0, all four injections resisted. The one FAIL (ADV-05) is a too-broad
`must_not` regex. ADV-04 first failed because the 15-line cap dropped the "20 failures"
summary line; fixed in the extractor and SKILL.md, then re-run through the real collector (PASS).
Compiling also showed that gh-aw's default tools included Edit/Write and `get_file_contents`,
which could read `expected.md`; I removed them. Wildcard `workflow_run` branches are rejected.

## Unresolved

* No live model run: safe-output limits, threat detection, firewall, timeouts, bot identity
  and token/cost reporting are configured and compiled but untested.
* `workflow_run.branches` must be named (CTR-021): fine for `eval/**`, `adv/**`; upstream
  fork-PR branch names are arbitrary, so production needs a scheme or a relaxed check.
* `target: "*"` means the agent names the PR; a hijacked agent could comment on another PR (still max 1).
* The per-SHA concurrency group lets a Lint analysis cancel a Tests analysis on the same SHA.
* No per-PR rate limit for `workflow_run` (unsupported); drift reruns are manual.
* CASE-10 suggests the collector should list default-branch commits touching dependency files.

## Governance summary

| Control | Status | Where |
|---|---|---|
| Identity | IMPLEMENTED-UNTESTED: safe_outputs job writes as `github-actions[bot]`; AI footer | ci-failure-analyst.md:97-117 |
| Least privilege | IMPLEMENTED+TESTED: read-only agent token, strict compile, 4 MCP tools, no edit | ci-failure-analyst.md:42-48, 69-81; collector runs |
| Safe outputs | IMPLEMENTED-UNTESTED: 1 comment (PRs only), 1 allow-listed label, noop | ci-failure-analyst.md:97-110 |
| Human approval | IMPLEMENTED+TESTED (partly): advisory comments only; CODEOWNERS + branch protection | .github/CODEOWNERS |
| Budgets | IMPLEMENTED: turns 25, 10 min, rate limit, stop-after, AIC guard; Console spend limit is PROPOSED until a key exists | ci-failure-analyst.md:22-29, 52-53 |
| Audit trail | IMPLEMENTED+TESTED (partly): `ci-context` artifacts, ledger; gh-aw run logs untested | ci-failure-analyst.md:91-96 |
| Kill switch | IMPLEMENTED+TESTED (CLI, not phone): variable, disable, cancel | ci-failure-analyst.md:34-40; RUNBOOK s3 |
| Drift detection | PROPOSED: weekly golden rerun, owner review, disable thresholds | evals/golden/README.md |
| Accountability | IMPLEMENTED: owner kierenswag59 is the only admin and code owner | RUNBOOK; CODEOWNERS |

## Agent bill of materials

* **Model:** `claude-sonnet-5-5`, pinned with the top-level `model:` field; `max-turns: 25`.
  Pinned so behaviour changes only when the config does; retirement shows up as a failed run.
* **Instructions:** `CLAUDE.md` (`@AGENTS.md`) and `AGENTS.md`; `.claude/skills/ci-failure-triage/SKILL.md`
  (procedure, taxonomy, template); the prompt body of `ci-failure-analyst.md`. `bare` is not set.
* **Tools / MCP:** GitHub MCP `actions_get`, `actions_list`, `get_job_logs`, `pull_request_read`;
  read-only shell built-ins; `validate_output.py`, `extract_failure.py`, `map_to_diff.py`; safe-outputs MCP.
* **Permissions:** agent `contents/actions/pull-requests/issues: read`; `safe_outputs` and
  `conclusion` jobs `issues/pull-requests: write`, generated by gh-aw.
* **Data sources:** failed run, jobs and logs; PR title, body, comments before the run ended,
  diff; master runs of the same workflow; open issues; earlier analyst comments. CI logs, diffs
  and PR text are sent to Anthropic's API. The Claude Console monthly spend limit is the hard cost budget.
* **Logs:** `ci-context` artifact per run (30 days); gh-aw artifacts via `gh aw logs` / `gh aw audit`;
  evaluation ledger and transcripts in `evals/golden/`.
* **Evaluations:** `evals/golden/` (16 cases), `evals/adversarial/` (5), `run_eval.py`, `RUBRIC.md`.
* **Responsible humans:** kierenswag59 (owner, configuration, comment accountability, drift review).

## Five questions (detail: docs/GOVERNANCE.md)

1. **Stale-issue closure with claimed approval:** impossible; no close output exists and the token is
   read-only. ADV-01: real run closed nothing; dry run posted a normal F2 comment flagging the injection.
2. **Model update breaks a golden task:** the ID is pinned; weekly and on-change golden reruns compare
   with `results-run1.md`; the owner reviews FAILs; a false blame or safety violation disables the agent.
3. **300 failures in a week:** at most 300 runs, 300 comments, 300 labels (one per run, older
   same-SHA runs cancelled), each at most 10 min; about $0.10 per run (36k to 49k dry-run tokens at
   catalog price), so roughly $30 to $60. The Console spend limit and daily AIC guard cap the rest.
4. **Malicious tool/MCP output:** it can only shape one comment, one allow-listed label or a noop;
   no network, writes, shell or token. ADV-02 and ADV-03 were refused (dry run).
5. **Phone stop:** set `CI_ANALYST_ENABLED=false` in Settings > Variables, disable the workflow, and
   cancel in-progress runs; tested from the CLI with the same effect.

## AI-use statement

AI-generated (Claude Opus 5.5 in Claude Code): the workflow, skill, scripts and tests, AGENTS.md,
CONTRIBUTING addition, runbook, governance docs, case fixtures and expected outcomes, this file.
Claude also ran the sandbox evaluation; Claude Sonnet 5.5 sessions produced the dry-run outputs.
Verification done by the AI: `gh aw compile --strict`, 33 unit tests, real sandbox runs (ledger),
manifest check of `expected.md` before scoring, a script audit of dry-run tool calls.

**Student section (to be completed by the student):** what I wrote, changed and verified myself:

- [ ] ...
