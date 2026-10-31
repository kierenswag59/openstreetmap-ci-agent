#!/usr/bin/env python3
"""Find the failed step and decisive error lines in a GitHub Actions job log.

Reads a raw job log (as returned by GET /repos/{o}/{r}/actions/jobs/{id}/logs),
strips ANSI colour codes and the leading ISO timestamps, finds the step that
emitted the first real ##[error], picks out the decisive lines (at most 15) and
derives a stable error signature that does not depend on timestamps, line
numbers, hex ids or runner paths.

Standard library only. Output is JSON on stdout.
"""

import argparse
import hashlib
import json
import re
import sys

ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
TS_RE = re.compile(r"^﻿?\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z ?")
WORKSPACE_RE = re.compile(r"/home/runner/work/[^/\s]+/[^/\s]+/")
GENERIC_EXIT_RE = re.compile(r"^##\[error\]Process completed with exit code \d+\.?$")
MAX_LINES = 15

# Patterns that mark a decisive line, tried in order. The first matching
# family also names the failure "kind" used in the signature.
FAMILIES = [
    ("minitest", re.compile(r"^(Error|Failure):$|^[A-Z][A-Za-z0-9_:]*Test#test_\S+|^bin/rails test \S+:\d+"
                            r"|^\d+ runs, \d+ assertions, \d+ failures, \d+ errors")),
    ("eslint", re.compile(r"^##\[error\]\s+\d+:\d+\s+error\s+|^✖ \d+ problems?")),
    ("rubocop", re.compile(r"^\S+\.(rb|rake|erb|gemspec|ru):\d+:\d+: [CWEFR]: |^\d+ files? inspected, \d+ offenses? detected")),
    ("bundler", re.compile(r"frozen mode is set|lockfile can't be updated|Could not find gem|Bundler::GemNotFound"
                           r"|^##\[error\]The process '.*bundle' failed with exit code \d+")),
    ("load-error", re.compile(r"\b(LoadError|Bundler::GemRequireError|NameError|NoMethodError):")),
    ("structure-diff", re.compile(r"^[+-]\s+\S+ .*CONSTRAINT \S+ NOT NULL")),
    ("annotation-drift", re.compile(r"^diff --git a/app/models/|^[+-]#\s")),
    ("approval", re.compile(r"required approval but was not approved|was not approved before it expired")),
    ("generic", re.compile(r"^##\[error\](?!Process completed with exit code)|\b(error|failed|fatal)\b", re.I)),
]

NOISE_RE = re.compile(r"^(##\[(group|endgroup)\]|\[command\]|shell: |env:|  ruby: )")


def clean_line(line):
    line = ANSI_RE.sub("", line.rstrip("\r\n"))
    line = TS_RE.sub("", line)
    return line


def clean_log(text):
    return [clean_line(l) for l in text.splitlines()]


def find_failed_step(lines):
    """Return (step_command, start_index, error_index) for the first real error.

    A "real" error is any ##[error] line; the generic "Process completed with
    exit code" line counts too, but tool-specific ##[error] lines (eslint
    prints its findings with that prefix) are preferred when they come first.
    """
    current = None
    start = 0
    for i, line in enumerate(lines):
        if line.startswith("##[group]Run "):
            current = line[len("##[group]Run "):].strip()
            start = i
        if line.startswith("##[error]"):
            return current, start, i
    return current, start, len(lines) - 1 if lines else 0


def decisive_lines(block):
    found = []
    kind = None
    for fam, rx in FAMILIES:
        hits = [l for l in block if rx.search(l) and not NOISE_RE.match(l) and not GENERIC_EXIT_RE.match(l.strip())]
        if hits:
            kind = fam
            found = hits
            break
    if kind == "structure-diff":
        # Keep only the "+" side: that is what the runner produced.
        found = [l for l in found if l.startswith("+")] or found
    if kind == "annotation-drift":
        found = [l for l in found if l.startswith(("diff --git", "+#", "-#"))]
    if kind == "eslint":
        # eslint prints the file path on the line before its findings.
        with_paths = []
        for i, l in enumerate(block):
            if l in found and i > 0 and block[i - 1].startswith("/") and block[i - 1] not in with_paths:
                with_paths.append(block[i - 1])
            if l in found:
                with_paths.append(l)
        found = with_paths
    # De-duplicate while keeping order, then keep the first MAX_LINES.
    seen = set()
    out = []
    for l in found:
        if l not in seen:
            seen.add(l)
            out.append(l)
    return kind or "unknown", out[:MAX_LINES]


def normalise_for_signature(line):
    line = WORKSPACE_RE.sub("", line)
    line = re.sub(r"^##\[error\]\s*", "", line)
    line = re.sub(r"\b[0-9a-f]{7,40}\b", "<hex>", line)
    line = re.sub(r":\d+(:\d+)?", ":<n>", line)
    line = re.sub(r"\b\d+(\.\d+)*\b", "<n>", line)
    line = re.sub(r"CONSTRAINT \S+ NOT NULL", "CONSTRAINT <name> NOT NULL", line)
    line = re.sub(r"\?\S+", "?<query>", line)
    line = re.sub(r"\s+", " ", line).strip()
    return line


def key_tokens(kind, lines):
    """Kind-specific stable tokens: rule ids, cop names, test names, error classes."""
    toks = set()
    for l in lines:
        l = WORKSPACE_RE.sub("", l)
        if kind == "eslint":
            m = re.search(r"\s(@?[a-z][\w/-]*[\w])\s*$", l)
            if m and "error" in l:
                toks.add(m.group(1))
        elif kind == "rubocop":
            toks.update(re.findall(r": [CWEFR]: (?:\[Correctable\] )?([A-Z]\w+/\w+):", l))
        elif kind == "minitest":
            toks.update(re.findall(r"^([A-Z]\w*Test#test_\w+)", l))
        elif kind == "load-error":
            toks.update(re.findall(r"\b(LoadError|GemRequireError|NameError|NoMethodError)\b", l))
            toks.update(re.findall(r"undefined symbol: (\w+)", l))
        elif kind == "bundler":
            if "frozen mode" in l:
                toks.add("frozen-lockfile")
            toks.update(re.findall(r"Could not find gem '([^']+)'", l))
        elif kind == "structure-diff":
            toks.add("CONSTRAINT <name> NOT NULL")
        elif kind == "annotation-drift":
            toks.update(re.findall(r"^diff --git a/(\S+)", l))
        elif kind == "approval":
            toks.add("approval-expired")
    return sorted(toks)


def keywords(lines):
    """Distinctive tokens for duplicate search: identifiers, error classes, rule ids."""
    words = []
    for l in lines:
        l = WORKSPACE_RE.sub("", l)
        for tok in re.findall(r"[A-Za-z_@][A-Za-z0-9_:/.@-]{4,}", l):
            tok = tok.strip(".:")
            if re.search(r"[_/:]|[a-z][A-Z]", tok) or tok.endswith(("Error", "Exception")) or tok.isupper():
                if not re.match(r"^(home|runner|work|usr|opt|lib)\b", tok):
                    words.append(tok)
    seen, out = set(), []
    for w in words:
        if w not in seen:
            seen.add(w)
            out.append(w)
    return out[:20]


def failed_block(text):
    """Cleaned lines of the failed step, from its group header to just past the error."""
    lines = clean_log(text)
    _, start, err = find_failed_step(lines)
    end = err + 1
    while end < len(lines) and end < err + 40 and not lines[end].startswith("##[group]"):
        end += 1
    return lines[start:end]


def extract(text, job_name=""):
    lines = clean_log(text)
    step, start, err = find_failed_step(lines)
    # The block runs from the failed step's group header to a few lines past the
    # first ##[error] (eslint and setup-ruby print the detail on error lines).
    end = err + 1
    while end < len(lines) and end < err + 40 and not lines[end].startswith("##[group]"):
        end += 1
    block = lines[start:end]
    kind, decisive = decisive_lines(block)
    if not decisive:
        decisive = [l for l in block[-MAX_LINES:] if l.strip()]
    tokens = key_tokens(kind, decisive)
    if not tokens:
        tokens = sorted({normalise_for_signature(l) for l in decisive[:5]})
    sig_basis = "|".join([kind, normalise_for_signature(step or "")] + tokens)
    signature = hashlib.sha1(sig_basis.encode()).hexdigest()[:12]
    return {
        "job": job_name,
        "failed_step": step,
        "kind": kind,
        "decisive_lines": decisive,
        "signature": signature,
        "signature_basis": sig_basis,
        "key_tokens": tokens,
        "keywords": sorted(set(tokens) | set(keywords(decisive)))[:20],
        "total_lines": len(lines),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("log", help="path to a raw job log, or - for stdin")
    ap.add_argument("--job", default="", help="job name to record in the output")
    ap.add_argument("--block-out", help="also write the cleaned failed-step block to this file")
    args = ap.parse_args(argv)
    text = sys.stdin.read() if args.log == "-" else open(args.log, encoding="utf-8", errors="replace").read()
    if args.block_out:
        with open(args.block_out, "w", encoding="utf-8") as fh:
            fh.write("\n".join(failed_block(text)) + "\n")
    json.dump(extract(text, args.job), sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
