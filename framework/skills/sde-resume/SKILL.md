---
name: sde-resume
description: Fresh-session entry point. Recover the full state from disk alone (zero chat history) and continue from the derived next action.
allowed-tools: Bash, Read, Write, Edit, Agent
---

# /sde-resume

You are resuming with **no memory** of prior sessions. The repo is the truth; do not guess — derive.

1. `cat .sde/objective.md` (north star + "done when") and `tail -n 20 .sde/decisions.md` (recent
   decisions you must not re-litigate).
2. `python3 framework/bin/sde status --root .` — the derived state + the single NEXT action (the
   ladder, computed from disk).
3. Optionally read `.sde/handoff.md` as a hint — but verify its `derived_from` equals
   `git rev-parse HEAD`. If it differs, the dossier is **stale → ignore it** and trust step 2.
4. Continue with `/sde-next`. The full ladder and the three "derive, don't trust labels" rules are in
   `.sde/RESUME.md`.

This works because every prior step ended at a committed, clean boundary. If the last session died
mid-action, `git status` shows the dirt; `git checkout -- <file>` returns to the last clean state and
`sde next` re-derives what to redo.
