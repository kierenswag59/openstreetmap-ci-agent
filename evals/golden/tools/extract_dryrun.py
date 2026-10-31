#!/usr/bin/env python3
"""Turn a dry-run session transcript (JSONL) into a reviewable digest and a result file.

  extract_dryrun.py <transcript.jsonl> <CASE-ID>

Writes evals/golden/dryrun/results/<CASE-ID>.json (the JSON object the session emitted) and
evals/golden/dryrun/transcripts/<CASE-ID>.md: every tool call the session made (tool name and
full input) with the first 400 characters of each result, then the final message. System
context of the session (environment, account details) is deliberately not copied.
"""
import json, os, re, sys

src, cid = sys.argv[1], sys.argv[2]
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
out_dir = os.path.join(root, "evals/golden/dryrun")
events = [json.loads(l) for l in open(src, encoding="utf-8") if l.strip().startswith("{")]
calls, results, final, model = [], {}, "", None
for ev in events:
    msg = ev.get("message")
    if not isinstance(msg, dict) or not isinstance(msg.get("content"), list):
        continue
    if msg.get("role") == "assistant":
        model = msg.get("model") or model
        for c in msg["content"]:
            if c.get("type") == "tool_use":
                if c["name"] == "SubagentHandback":
                    final = (c.get("input") or {}).get("message", "")
                else:
                    calls.append((c["id"], c["name"], c.get("input")))
            elif c.get("type") == "text" and "```json" in c.get("text", ""):
                final = c["text"]
    elif msg.get("role") == "user":
        for c in msg["content"]:
            if c.get("type") == "tool_result":
                body = c.get("content")
                if isinstance(body, list):
                    body = "\n".join(x.get("text", "") for x in body if isinstance(x, dict))
                results[c.get("tool_use_id")] = str(body)
m = list(re.finditer(r"```json\s*(\{.*?\})\s*```", final, re.S))
if not m:
    sys.exit("no json block in final message")
obj = json.loads(m[-1].group(1))
os.makedirs(os.path.join(out_dir, "results"), exist_ok=True)
os.makedirs(os.path.join(out_dir, "transcripts"), exist_ok=True)
json.dump(obj, open(os.path.join(out_dir, "results", cid + ".json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
L = [f"# Dry-run transcript digest: {cid}", "", f"Model reported by the session: `{model}`.",
     f"Prompt: `evals/golden/dryrun/PROMPT.md` with the case workspace substituted.", "",
     f"## Tool calls ({len(calls)})", ""]
for i, (tid, name, inp) in enumerate(calls, 1):
    L += [f"### {i}. {name}", "", "```json", json.dumps(inp, indent=1, ensure_ascii=False), "```", "",
          "Result (first 400 chars):", "", "```text", results.get(tid, "")[:400], "```", ""]
L += ["## Final message", "", final, ""]
open(os.path.join(out_dir, "transcripts", cid + ".md"), "w", encoding="utf-8").write("\n".join(L))
print(cid, obj.get("type"), obj.get("label"), "calls:", len(calls), "model:", model)
for _, name, inp in calls:
    print("  ", name, json.dumps(inp)[:200])
