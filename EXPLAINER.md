# EXPLAINER: what every file does, in plain language (not graded)

## The idea in one paragraph

When CI fails on a pull request, a contributor sees "Process completed with exit code 1" and has
to dig through a 5,000-line log. This repository adds a bot that, after a failed run, reads the
failed job's log, the PR's diff and description, checks whether master is failing the same way
and whether an issue already tracks it, and posts **one** comment: what kind of failure it is,
whether this PR probably caused it (yes / no / unclear), the log lines that prove it, and one next
step. It cannot do anything else: no merging, closing, pushing, re-running or arbitrary labels.

## How a run flows

1. A CI workflow (Tests, Lint, Docker, or the evaluation's "Replay CI failure") finishes.
2. GitHub fires `workflow_run`; `ci-failure-analyst.lock.yml` (compiled from the `.md`) starts.
3. **pre_activation** job: the `if:` guard checks the kill-switch variable `CI_ANALYST_ENABLED`,
   that the run was a `pull_request` run, and that it failed/timed out/needed approval; it also
   checks `stop-after` and the dispatch rate limit. If any check fails, nothing else runs.
4. **activation** job: checks the API key secret exists, checks the lock file matches the `.md`,
   renders the prompt.
5. **agent** job (read-only token): sparse checkout (only `.claude/` and root files, so the
   expected answers in `evals/` are not on disk); `collect_context.py` gathers the data with plain
   API calls (no model) and runs the deterministic checks; then Claude Code runs inside the AWF
   firewall with a narrow tool list and writes its intended output to the safe-outputs channel.
6. **detection** job: a second model pass scans the intended output for injection or secret leaks;
   failure blocks everything after it.
7. **safe_outputs** job (the only job with write permission): posts at most one comment and one
   allow-listed label, exactly as configured.

## Files

| File | What it is | Why it exists |
|---|---|---|
| `.github/workflows/ci-failure-analyst.md` | gh-aw source: frontmatter (trigger, permissions, engine, tools, network, safe outputs, limits) + the prompt | where the hard restrictions are enforced |
| `.github/workflows/ci-failure-analyst.lock.yml` | compiled GitHub Actions YAML from `gh aw compile --strict` | what GitHub actually runs; never hand-edited |
| `.github/workflows/replay-failure.yml` | plain workflow that re-prints a stored historical log and exits with its status | lets the analyst trigger on a realistic failure in the sandbox |
| `.github/workflows/ci-context-capture.yml` | runs the same collector and uploads the bundle | evaluation-only, because the sandbox has no model key |
| `.github/CODEOWNERS` | owner review for agent config | human approval control |
| `AGENTS.md` / `CLAUDE.md` | repository facts; `CLAUDE.md` is just `@AGENTS.md` so Claude Code loads it | facts live in one file |
| `.claude/skills/ci-failure-triage/SKILL.md` | the procedure: when to stay silent, taxonomy, how to decide "caused by", template, self-check | procedure lives in the skill |
| `scripts/extract_failure.py` | finds the failed step, the decisive lines and a stable 12-hex signature | deterministic, testable |
| `scripts/map_to_diff.py` | matches `file:line` in the log to lines the PR changed | the main "caused by this PR" evidence |
| `scripts/check_master.py` | did the same signature fail on master recently (broken / seen / clean)? | "already broken on master" |
| `scripts/dedupe.py` | open issues or earlier bot comments with the same signature or keywords | duplicates |
| `scripts/validate_output.py` | checks the draft comment (sections, <= 15 quoted lines, footer marker, no secrets, no "LGTM", label allow-list) | self-check before output |
| `scripts/collect_context.py` | runs all of the above before the model starts and writes `context.md` | the model starts from facts |
| `evals/golden/` | 16 real cases, rubric, scorer, seeds, results | evaluation |
| `evals/adversarial/` | 5 constructed attacks | safeguard tests |
| `docs/RUNBOOK.md` | setup, kill switch, budgets, owners | operations |

## Frontmatter keys, one line each

`on.workflow_run` (react to CI), `workflows/types/branches` (which runs; branches is required by
the compiler's CTR-021 check), `workflow_dispatch.run_id` (manual re-analysis), `stop-after`
(pilot end date), `user-rate-limit` (dispatch cap), `if` (kill switch + event gate), `permissions`
(read-only), `strict` (compiler refuses unsafe settings), `engine`/`model`/`max-turns`/`timeout-minutes`
(which model, how long), `concurrency` (one run per head SHA), `checkout.sparse-checkout`
(keep answers off disk), `network.allowed` (firewall), `tools.github.allowed` (four read tools),
`tools.edit: false` (no file editing), `tools.bash` (three scripts), `steps` (deterministic
collection), `safe-outputs.*` (the only writes, with limits), `threat-detection` (scan before
writing), `messages.footer` (AI-generated notice).

## Likely grader questions

* *Why not let the agent fetch logs itself?* It can (four MCP read tools), but collecting first
  makes the inputs auditable (artifact), cheaper, and identical between live and dry runs.
* *Why `target: "*"` on add-comment?* `workflow_run` and `workflow_dispatch` events have no
  "triggering PR" in gh-aw's sense; the PR number comes from `context.json`. `issues: false`
  keeps it to PRs, and `max: 1` bounds the damage of a wrong target. This is a known residual risk.
* *How do you know the skill was used?* The marker `triage-skill: ci-failure-triage v1` and the
  signature line exist only in SKILL.md, not in the prompt; every output must carry them, and
  the run's tool log shows `Read .claude/skills/ci-failure-triage/SKILL.md` or a `Skill` call.
* *Was the agent ever run live?* Yes, on 1 Nov 2026 once a key existed: 19 agent runs posted
  18 comments and 17 labels in the sandbox (18 of 21 cases PASS, `evals/golden/results.md`).
  Before that, judgement was tested in a dry run (20 of 21, `results-dryrun.md`); the live run
  found six configuration faults the dry run could not (`evals/golden/ANALYSIS.md`).
