#!/usr/bin/env bash
# Build a dry-run workspace that mirrors what the analyst's agent sees:
# the sparse checkout (root files incl. CLAUDE.md and AGENTS.md, plus .claude/) and the
# context bundle collected by collect_context.py (downloaded from ci-context-capture.yml).
#   evals/golden/tools/dryrun_workspace.sh <bundle-dir> <workspace-dir>
set -euo pipefail
bundle="${1:?bundle dir}"; ws="${2:?workspace dir}"
root="$(git rev-parse --show-toplevel)"
mkdir -p "$ws/repo" "$ws/ci-context"
cp "$root/CLAUDE.md" "$root/AGENTS.md" "$ws/repo/"
cp -R "$root/.claude" "$ws/repo/"
mkdir -p "$ws/repo/.github/workflows" && cp "$root/.github/workflows/ci-failure-analyst.md" "$ws/repo/.github/workflows/"
cp -R "$bundle"/. "$ws/ci-context/"
# The bundle's context.md refers to its original location /tmp/gh-aw/ci-context or ci-context/.
grep -rl 'ci-context' "$ws/ci-context" | xargs sed -i.bak "s#\(/home/runner/work/[^ ]*/\)\{0,1\}ci-context/#$ws/ci-context/#g"
find "$ws" -name '*.bak' -delete
echo "$ws"
