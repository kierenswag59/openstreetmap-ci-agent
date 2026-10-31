#!/usr/bin/env python3
"""Find open issues and earlier agent comments that already describe a failure.

Input:
  --issues    JSON list of open issues: [{"number", "title", "body", "html_url"}]
  --comments  JSON list of earlier comments by this workflow:
              [{"html_url", "body", "created_at", "pr_number"}]
  --signature the signature from extract_failure.py
  --keywords  distinctive tokens from extract_failure.py (repeatable)

An earlier agent comment matches when it records the same signature (every
comment carries a "signature: <hash>" line). An issue matches when its title
or body contains the signature, or at least --min-keywords of the keywords
(case-insensitive). Issues are reported with the keywords that matched so a
human can check the reasoning.

Standard library only. Output is JSON on stdout.
"""

import argparse
import json
import re
import sys


def _norm(s):
    return (s or "").lower()


def issue_matches(issues, signature, keywords, min_keywords=2):
    out = []
    kws = [k for k in keywords if len(k) >= 5]
    for issue in issues:
        text = _norm(issue.get("title")) + "\n" + _norm(issue.get("body"))
        if signature and signature.lower() in text:
            out.append({"number": issue["number"], "title": issue.get("title", ""),
                        "html_url": issue.get("html_url", ""), "reason": "signature", "matched": [signature]})
            continue
        hit = [k for k in kws if k.lower() in text]
        # Structure-check failures quote column definitions; treat the
        # normalised CONSTRAINT pattern as matching any quoted named constraint.
        if "CONSTRAINT <name> NOT NULL" in keywords and re.search(r"constraint \w+ not null", text):
            hit.append("CONSTRAINT <name> NOT NULL")
        if len(set(hit)) >= min_keywords:
            out.append({"number": issue["number"], "title": issue.get("title", ""),
                        "html_url": issue.get("html_url", ""), "reason": "keywords", "matched": sorted(set(hit))})
    return out


def comment_matches(comments, signature):
    rx = re.compile(r"signature:\s*`?([0-9a-f]{12})`?", re.I)
    out = []
    for c in comments:
        found = rx.findall(c.get("body", ""))
        if signature and signature in found:
            out.append({"html_url": c.get("html_url", ""), "created_at": c.get("created_at", ""),
                        "pr_number": c.get("pr_number")})
    return out


def dedupe(issues, comments, signature, keywords, min_keywords=2):
    issues_hit = issue_matches(issues, signature, keywords, min_keywords)
    comments_hit = comment_matches(comments, signature)
    return {
        "duplicate": bool(issues_hit or comments_hit),
        "issues": issues_hit[:5],
        "earlier_agent_comments": comments_hit[:5],
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--issues", required=True, help="JSON file of open issues")
    ap.add_argument("--comments", help="JSON file of earlier agent comments")
    ap.add_argument("--signature", required=True)
    ap.add_argument("--keywords", action="append", default=[], help="keyword (repeatable)")
    ap.add_argument("--min-keywords", type=int, default=2)
    args = ap.parse_args(argv)
    issues = json.load(open(args.issues, encoding="utf-8"))
    comments = json.load(open(args.comments, encoding="utf-8")) if args.comments else []
    json.dump(dedupe(issues, comments, args.signature, args.keywords, args.min_keywords), sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
