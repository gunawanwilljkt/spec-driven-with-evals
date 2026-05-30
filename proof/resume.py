"""
RESUMABILITY check (SC-3), deterministic version.

A fresh agent/operator given ONLY the repo must be able to recover:
  (1) the OBJECTIVE        — read from the spec file,
  (2) the EVAL STATUS      — RECOMPUTED by re-running the eval suite (ground
                             truth, not a stored claim that can go stale),
  (3) the NEXT ACTION      — read from the on-disk task list.

This script reads those files and re-runs the eval, then prints the triple as
JSON. It exits 0 only if all three are recoverable. Encoded as an eval itself:
"the repo is self-describing to a cold reader."

Run: python3 resume.py   (from the repo root)
"""

import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return f.read()


def first_match(text, pattern, label):
    m = re.search(pattern, text, re.MULTILINE)
    if not m:
        sys.stderr.write(f"[resume] could not recover {label}\n")
        return None
    return m.group(1).strip()


def recompute_eval_status():
    """Ground truth: actually run the eval against the current impl."""
    proc = subprocess.run(
        [sys.executable, "eval_contract.py"],
        cwd=ROOT, capture_output=True, text=True, env={**os.environ, "IMPL": "correct"},
    )
    return "GREEN" if proc.returncode == 0 else "RED"


def main():
    spec = read("SPEC.md")
    tasks = read("TASKS.md")

    objective = first_match(spec, r"^- OBJECTIVE:\s*(.+)$", "objective")
    next_action = first_match(tasks, r"^- \[ \]\s*(.+)$", "next action")  # first unchecked
    eval_status = recompute_eval_status()

    triple = {
        "objective": objective,
        "eval_status": eval_status,
        "next_action": next_action,
    }
    print(json.dumps(triple, indent=2))
    ok = all(triple.values())
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
