#!/usr/bin/env python3
"""Check a draft triage comment (or noop reason) before it is emitted.

Checks for a comment:
  * every required section of the template is present, with an allowed value
  * at most 15 quoted log lines in the evidence block
  * exactly one recommended next step
  * the AI-generated footer with the skill marker and the 12-hex signature
  * total length at most 4000 characters
  * no secret-like tokens, no @mentions, no approval/merge/close language
  * the optional label is on the allow-list and matches the category

Checks for a noop reason (--noop): it names a reason and carries the marker.

Exit status 0 when the draft passes, 1 otherwise. Output is JSON on stdout.
Standard library only.
"""

import argparse
import json
import re
import sys

MARKER = "triage-skill: ci-failure-triage v1"
ALLOWED_LABELS = {
    "ci-triage:pr-related": {"F1", "F2"},
    "ci-triage:dependency": {"F3"},
    "ci-triage:infrastructure": {"F4"},
    "ci-triage:known-issue": {"F5"},
    "ci-triage:flaky": {"F6"},
}
MAX_CHARS = 4000
MAX_QUOTED = 15
SECRET_RE = re.compile(r"(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_\w{20,}|sk-ant-[\w-]{10,}|AKIA[0-9A-Z]{16}"
                       r"|-----BEGIN [A-Z ]*PRIVATE KEY-----)")
FORBIDDEN_RE = re.compile(r"\bLGTM\b|\bmerging\b|\bmerge (this|it|now)\b|\b(approved|approving)\b"
                          r"|\b(I|we) (will|have|am going to) (close|closed|merge|merged|re-?run)\b", re.I)
MENTION_RE = re.compile(r"(?<![\w`/])@[A-Za-z0-9][A-Za-z0-9-]{0,38}\b")

SECTIONS = [
    ("category", re.compile(r"^\*\*Category:\*\*\s*(F[1-6])\b", re.M)),
    ("pr_caused", re.compile(r"^\*\*Caused by this PR:\*\*\s*(yes|no|unclear)\b", re.M | re.I)),
    ("confidence", re.compile(r"^\*\*Confidence:\*\*\s*(high|medium|low)\b", re.M | re.I)),
    ("evidence", re.compile(r"^\*\*Decisive log lines\*\*", re.M)),
    ("files", re.compile(r"^\*\*Implicated files[^*]*:\*\*", re.M)),
    ("known", re.compile(r"^\*\*Known issue / master status:\*\*", re.M)),
    ("next_step", re.compile(r"^\*\*Recommended next step:\*\*\s*(.+)$", re.M)),
]


def strip_code(text):
    return re.sub(r"```.*?```", "", text, flags=re.S)


def quoted_lines(text):
    m = re.search(r"\*\*Decisive log lines\*\*.*?```[a-z]*\n(.*?)```", text, re.S)
    if not m:
        return None
    return [l for l in m.group(1).splitlines() if l.strip()]


def validate_comment(body, label=None):
    errors = []
    values = {}
    for name, rx in SECTIONS:
        m = rx.search(body)
        if not m:
            errors.append(f"missing or invalid section: {name}")
        elif m.groups():
            values[name] = m.group(1).strip()
    q = quoted_lines(body)
    if q is None:
        errors.append("evidence block must be a fenced code block after **Decisive log lines**")
    elif len(q) > MAX_QUOTED:
        errors.append(f"too many quoted log lines: {len(q)} > {MAX_QUOTED}")
    elif len(q) == 0:
        errors.append("evidence block is empty")
    if len(re.findall(r"^\*\*Recommended next step:\*\*", body, re.M)) != 1:
        errors.append("exactly one recommended next step is required")
    if MARKER not in body:
        errors.append("footer marker missing: " + MARKER)
    if not re.search(r"signature:\s*`?[0-9a-f]{12}`?", body):
        errors.append("footer must carry the 12-hex failure signature")
    if "AI-generated" not in body:
        errors.append("footer must say the comment is AI-generated")
    if len(body) > MAX_CHARS:
        errors.append(f"comment too long: {len(body)} > {MAX_CHARS} chars")
    if SECRET_RE.search(body):
        errors.append("secret-like token found")
    prose = strip_code(body)
    if FORBIDDEN_RE.search(prose):
        errors.append("approval, merge, close or re-run language is not allowed: "
                      + FORBIDDEN_RE.search(prose).group(0))
    if MENTION_RE.search(prose):
        errors.append("@mentions are not allowed: " + MENTION_RE.search(prose).group(0))
    if label:
        if label not in ALLOWED_LABELS:
            errors.append(f"label not on allow-list: {label}")
        elif values.get("category") and values["category"] not in ALLOWED_LABELS[label]:
            errors.append(f"label {label} does not match category {values['category']}")
    return {"ok": not errors, "errors": errors, "values": values,
            "quoted_lines": len(q) if q is not None else 0, "chars": len(body)}


def validate_noop(reason):
    errors = []
    if len(reason.strip()) < 20:
        errors.append("noop reason is too short to audit")
    if MARKER not in reason:
        errors.append("noop reason must carry the marker: " + MARKER)
    if SECRET_RE.search(reason):
        errors.append("secret-like token found")
    return {"ok": not errors, "errors": errors, "chars": len(reason)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--body", help="draft comment text")
    g.add_argument("--body-file", help="file holding the draft comment")
    g.add_argument("--noop", help="draft noop reason")
    ap.add_argument("--label", help="label the draft would add (optional)")
    args = ap.parse_args(argv)
    if args.noop is not None:
        res = validate_noop(args.noop)
    else:
        body = args.body if args.body is not None else open(args.body_file, encoding="utf-8").read()
        res = validate_comment(body, args.label)
    json.dump(res, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
