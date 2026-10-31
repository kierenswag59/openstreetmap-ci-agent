#!/usr/bin/env bash
# Build the dry-run workspace and rendered prompt for one case from its downloaded bundle.
#   prepare_dryrun.sh <bundles-root> <work-root> <CASE-ID>
set -euo pipefail
b="$(ls -d "$1/$3"/ci-context-* | head -1)"; ws="$2/$3"
root="$(git rev-parse --show-toplevel)"
rm -rf "$ws"; "$root/evals/golden/tools/dryrun_workspace.sh" "$b" "$ws" >/dev/null
sed "s#{WS}#$ws#g" "$root/evals/golden/dryrun/PROMPT.md" | sed -n '/^---$/,$p' | tail -n +2 > "$2/$3.prompt.txt"
echo "$2/$3.prompt.txt"
