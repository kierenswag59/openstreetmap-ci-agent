# Sources opened

All accessed on 2026-10-31 (UTC+8) unless noted. "API" means a read-only `gh api` GET against
the public REST API. Nothing was posted to upstream.

## Evidence dump

* `Assignment 3.md` (repository root): ASSIGNMENT, PROMPT, evidence sections A1-A5, B1-B21,
  C1-C42, CASE-01..18, E1-E4, G0-G4 (collected 30 Oct 2026 by the student).

## gh-aw documentation (evidence section C, plus the CLI)

* C1 github-agentic-workflows.md, C2 syntax-core.md, C3 syntax-engine.md, C4 syntax-tools-imports.md,
  C5 triggers.md, C6-C9 safe-outputs*.md, C10 network.md, C11 skills.md, C12 workflow-patterns.md,
  C13 configure-agentic-engine.md, C30 reference/rate-limiting, C32 reference/engines,
  C33 reference/auth, C35 reference/fork-support, C37 governance guide, C39/G4a cli-commands.md,
  C41 GitHub docs "Disabling and enabling a workflow", G4b Claude Code skills docs.
* `gh aw` v1.0.1 CLI (`gh extension install github/gh-aw`): `gh aw --help`, `gh aw models`,
  `gh aw compile --strict`, and the JSON schema embedded in the binary (to confirm the
  `checkout.sparse-checkout`, `tools.edit`, `user-rate-limit.events` keys and their allowed values).

## Upstream data (API, read-only)

* Runs and jobs: `/repos/openstreetmap/openstreetmap-website/actions/runs/{id}` and `/jobs` for
  40753633422, 40757514945, 40746377705, 40761769826, 36330556125, 35760389282, 35636239291,
  35875254785, 33694039489, 37705152851, 33391131716, 32283669556 (and `/attempts/1..3`),
  38562633179, 40916734387, 35933394011, 40762407177; seeds 40713973741, 35634504477,
  32247269027, 32282177239; master runs 37736780038, 32315126673.
* Job logs: `/actions/jobs/{id}/logs` for every failed job of those runs (stored in `input/logs/`).
* PRs: `/pulls/{n}`, `/pulls/{n}/commits`, `/pulls/{n}/reviews`, `/issues/{n}/comments` for #7546,
  #7547, #7545, #7432, #7398, #7399, #7410, #7355, #7480, #7350, #7328, #7490, #7421, #7357.
* Diffs: `/compare/{tested_base}...{head}` (diff media type) for each case.
* Same-SHA runs: `/actions/runs?head_sha={sha}` for each case (ground truth: re-runs, sibling workflows).
* Master history: `/actions/runs?branch=master&event=push&created=...` for the case windows and
  2026-07-25..2026-10-29 (metrics); commits 8524e874, b2abf8b5, 535999ca, 1e509829, 1ee2cc49 and
  `/compare/1ab80766...1ee2cc49`.
* Issues: `/issues/7544`; search `repo:openstreetmap/openstreetmap-website test_search_adds_viewbox_param_to_Nominatim_link`
  and `nominatim viewbox test is:issue` (to check for a pre-existing flaky-test issue: none found).
* Metrics: `/actions/runs?event=pull_request&created=2026-08-01..2026-10-29` (three monthly queries).

## Sandbox (API and Actions UI)

* `https://github.com/kierenswag59/openstreetmap-ci-agent`: repository settings, workflows,
  runs, PRs and artifacts created by this evaluation (listed per case in `actual.md`).
