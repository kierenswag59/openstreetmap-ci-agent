# Runbook: CI failure analyst

Owner and accountable human: **kierenswag59** (sandbox owner, the student). Only users with
admin rights on `kierenswag59/openstreetmap-ci-agent` can change repository variables, secrets,
workflow enablement or branch protection; `.github/CODEOWNERS` requires the owner's review for
the agent's configuration files. The owner is responsible for every comment the agent posts.

## 1. One-time setup

1. Install tools: `gh` (2.x) and `gh extension install github/gh-aw` (tested with gh-aw v1.0.1).
2. Sandbox: a new repository you own, not a GitHub fork (so PRs can never default to upstream):
   ```bash
   git clone https://github.com/openstreetmap/openstreetmap-website.git openstreetmap-ci-agent
   cd openstreetmap-ci-agent
   git checkout 729cdc3d3a3d2fca55799b02eb5381b46080c88b -B master
   git remote rename origin upstream
   git remote set-url --push upstream DISABLED
   gh repo create kierenswag59/openstreetmap-ci-agent --public --source . --remote origin
   git push origin master
   gh repo edit kierenswag59/openstreetmap-ci-agent --default-branch master
   ```
3. Model key and hard budget: in the Claude Console create an API key for this project and set a
   monthly spend limit (Settings > Limits); that limit is the hard cost budget. Then
   `gh aw secrets set ANTHROPIC_API_KEY --repo kierenswag59/openstreetmap-ci-agent` or
   `gh secret set ANTHROPIC_API_KEY --repo kierenswag59/openstreetmap-ci-agent` (paste when prompted).
4. Variables: `gh variable set CI_ANALYST_ENABLED --body true --repo kierenswag59/openstreetmap-ci-agent`
   (anything other than `true` stops the agent; see section 3).
5. Labels on the allow-list:
   ```bash
   for l in pr-related dependency infrastructure known-issue flaky; do
     gh label create "ci-triage:$l" --repo kierenswag59/openstreetmap-ci-agent --color BFD4F2 --force; done
   ```
6. Disable upstream workflows that are not needed in the sandbox: they would comment (Danger,
   with GITHUB_TOKEN), burn minutes, and above all fail for reasons unrelated to the case
   (for example the structure check on Ubuntu 26.04) and trigger the analyst on unplanned failures.
   ```bash
   for w in tests.yml lint.yml docker.yml devcontainer.yml danger.yml; do
     gh workflow disable "$w" --repo kierenswag59/openstreetmap-ci-agent; done
   ```
   (Mode 2 of the evaluation re-enables `lint.yml` temporarily.)
   Dependabot version updates still open PRs here (its workflow cannot be disabled; remove
   `.github/dependabot.yml` in the sandbox or ignore them). Never publish text copied from
   upstream without wrapping `@` mentions and upstream issue links in code spans: it notifies
   real people (sandbox issue #24). `evals/golden/setup_case.sh` does this for PR bodies.
7. Compile and check: `gh aw compile ci-failure-analyst --strict` (add `--approve` after reviewing
   the one new secret, `ANTHROPIC_API_KEY`). In `.github/workflows/ci-failure-analyst.lock.yml`
   check: the agent job's `permissions` are all `read`; only `safe_outputs` and `conclusion`
   have `issues: write`/`pull-requests: write`; `--allowed-tools` lists only the read-only shell
   built-ins, the three skill scripts, `mcp__github__{actions_get,actions_list,get_job_logs,pull_request_read}`
   and `mcp__safeoutputs`; `--disallowed-tools` includes `WebFetch,WebSearch`; `GH_AW_ALLOWED_DOMAINS`
   contains only defaults and GitHub domains; the safe-output config has `add_comment` max 1,
   `add_labels` max 1 with the five labels, and no close/merge/push/PR/dispatch types.
8. Commit `expected.md` files and `evals/golden/MANIFEST.sha256` **before** any run; then push the
   compiled workflow to `master`.

## 2. Day-to-day

* The agent runs when Tests, Lint, Docker or "Replay CI failure" completes with failure,
  timed_out or action_required for a `pull_request` run on an `eval/**` or `adv/**` branch.
* Manual analysis of one run: `gh aw run ci-failure-analyst --repo kierenswag59/openstreetmap-ci-agent -F run_id=<id>`
  (or Actions > CI Failure Analyst > Run workflow). Limited to 10 dispatches per user per hour.
* Audit: `gh aw logs ci-failure-analyst --repo kierenswag59/openstreetmap-ci-agent` (downloads
  runs, prompts, tool calls, firewall and token reports) and `gh aw audit <run-id>`; the
  `ci-context` artifact keeps the exact inputs for 30 days.
* Bad comment reports: 👎 reactions and issues that link a comment are reviewed weekly with the
  drift run (evals/golden/README.md, "Drift detection").

## 3. Kill switch (works from a phone browser)

Stop new runs (fastest, no code change):
1. Open `https://github.com/kierenswag59/openstreetmap-ci-agent/settings/variables/actions` in
   the phone browser (signed in as an admin; "Desktop site" is not needed).
2. Tap `CI_ANALYST_ENABLED`, change the value to `false`, tap **Update variable**.
   New runs are skipped by the `if:` guard in the pre-activation job (no model call, no output).

Also disable the workflow (belt and braces):
3. Open `https://github.com/kierenswag59/openstreetmap-ci-agent/actions/workflows/ci-failure-analyst.lock.yml`,
   tap the **...** menu, then **Disable workflow**.

Stop runs already in progress:
4. Open `https://github.com/kierenswag59/openstreetmap-ci-agent/actions?query=workflow%3A%22CI+Failure+Analyst%22+is%3Ain_progress`,
   tap each run, then **Cancel workflow**. Cancelling before the `safe_outputs` job starts means
   nothing is posted; if `safe_outputs` already ran, delete the comment by hand (owner only).
   From a terminal: `gh run list --workflow ci-failure-analyst.lock.yml --status in_progress --json databaseId -q '.[].databaseId' | xargs -n1 gh run cancel`.

Last resort: delete the `ANTHROPIC_API_KEY` secret or revoke the key in the Claude Console;
activation then fails at "Validate ANTHROPIC_API_KEY secret".

Re-enable: set `CI_ANALYST_ENABLED=true`, re-enable the workflow, run the golden cases first.

## 4. Budgets

| Limit | Value | Where |
|---|---|---|
| Model spend (hard) | Claude Console balance or monthly spend limit (sandbox: $5 prepaid); about $0.21 per run live | Claude Console |
| Turns per run | 25 | `max-turns` in ci-failure-analyst.md |
| Agent step time | 10 min (agent job 60 min, detection 10 min, safe outputs 15 min, compiler defaults) | `timeout-minutes`; lock file |
| Outputs per run | 1 comment, 1 label | `safe-outputs` |
| Parallelism | 1 run per head SHA (older cancelled); gh-aw adds one agent job per engine at a time | `concurrency` |
| Manual dispatches | 10 per user per hour; gh-aw skips admin, maintain and write roles (logged live) | `user-rate-limit` |
| Lifetime | stops after 2027-01-31 23:59:59 unless recompiled | `on.stop-after` |
| Daily AI credits | gh-aw default guardrail 5000 AIC/day per workflow | compiled `daily_ai_credits_exceeded` check |

## 5. Re-running golden tasks

See `evals/golden/README.md`: weekly, and after any change to the model ID, workflow, SKILL.md,
AGENTS.md or scripts. The owner reviews results; thresholds for disabling are listed there.

## 6. Changing the configuration

1. Edit `.github/workflows/ci-failure-analyst.md`, then `gh aw compile ci-failure-analyst --strict`.
2. Never edit the `.lock.yml` by hand. Commit both files together; the activation job's lock-file
   check fails if they disagree.
3. Open a PR; CODEOWNERS review by the owner is required; rerun the golden tasks before merging.
