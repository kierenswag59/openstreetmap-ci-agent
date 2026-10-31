#!/usr/bin/env python3
"""Match file:line references in a CI log against a pull request diff.

Given a unified diff (git diff / the GitHub .diff media type) and one or more
job logs, report every file the log points at, whether that file is part of
the diff, and whether the referenced line was added or changed by the diff.

Recognised reference styles:
  * path:line[:col]           (RuboCop, Ruby backtraces, "bin/rails test x:71")
  * eslint blocks              (an absolute path line, then "  13:13  error ...")
  * "diff --git a/x b/x"       (annotaterb drift printed by git diff --exit-code)

Standard library only. Output is JSON on stdout.
"""

import argparse
import json
import re
import sys

WORKSPACE_RE = re.compile(r"/home/runner/work/[^/\s]+/[^/\s]+/")
TS_RE = re.compile(r"^﻿?\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z ?")
ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
REF_RE = re.compile(r"(?<![\w/.-])((?:app|lib|config|test|db|script|bin|vendor)/[\w./-]+\.\w+):(\d+)")
ESLINT_LINE_RE = re.compile(r"^(?:##\[error\])?\s+(\d+):(\d+)\s+(error|warning)\s+")
GITDIFF_RE = re.compile(r"^diff --git a/(\S+) b/\S+")
HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def parse_diff(text):
    """Return {path: set(new-side line numbers added or changed)}."""
    files = {}
    path = None
    new_line = 0
    for raw in text.splitlines():
        if raw.startswith("diff --git "):
            path = None
            continue
        if raw.startswith("+++ "):
            target = raw[4:].strip()
            path = None if target == "/dev/null" else re.sub(r"^b/", "", target)
            if path is not None:
                files.setdefault(path, set())
            continue
        if raw.startswith("--- "):
            continue
        m = HUNK_RE.match(raw)
        if m:
            new_line = int(m.group(1))
            continue
        if path is None:
            continue
        if raw.startswith("+"):
            files[path].add(new_line)
            new_line += 1
        elif raw.startswith("-"):
            continue
        elif raw.startswith("\\"):
            continue
        else:
            new_line += 1
    return files


def clean(line):
    return TS_RE.sub("", ANSI_RE.sub("", line.rstrip("\r\n")))


def log_refs(text):
    refs = []
    current_eslint_file = None
    for raw in text.splitlines():
        line = clean(raw)
        stripped = WORKSPACE_RE.sub("", line)
        if line.startswith("/home/runner/work/") and re.search(r"\.\w+$", line.strip()):
            current_eslint_file = WORKSPACE_RE.sub("", line.strip())
            continue
        m = ESLINT_LINE_RE.match(line)
        if m and current_eslint_file:
            refs.append((current_eslint_file, int(m.group(1)), "eslint"))
            continue
        if line.strip() == "":
            current_eslint_file = None
        m = GITDIFF_RE.match(stripped)
        if m:
            refs.append((m.group(1), None, "git-diff"))
            continue
        for p, n in REF_RE.findall(stripped):
            refs.append((p, int(n), "path:line"))
    # de-duplicate, keep order
    seen, out = set(), []
    for r in refs:
        if r not in seen:
            seen.add(r)
            out.append(r)
    return out


def match(diff_text, log_texts):
    diff = parse_diff(diff_text)
    results = []
    for text in log_texts:
        for path, line, style in log_refs(text):
            in_diff = path in diff
            results.append({
                "file": path,
                "line": line,
                "style": style,
                "file_in_diff": in_diff,
                "line_changed_by_pr": bool(in_diff and line is not None and line in diff[path]),
            })
    # Keep the list short and useful: references into the diff first.
    results.sort(key=lambda r: (not r["line_changed_by_pr"], not r["file_in_diff"]))
    return {
        "diff_files": sorted(diff),
        "references": results[:40],
        "any_reference_in_diff": any(r["file_in_diff"] for r in results),
        "any_changed_line_referenced": any(r["line_changed_by_pr"] for r in results),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--diff", required=True, help="path to the PR diff")
    ap.add_argument("logs", nargs="+", help="one or more job log files")
    args = ap.parse_args(argv)
    diff_text = open(args.diff, encoding="utf-8", errors="replace").read()
    logs = [open(p, encoding="utf-8", errors="replace").read() for p in args.logs]
    json.dump(match(diff_text, logs), sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
