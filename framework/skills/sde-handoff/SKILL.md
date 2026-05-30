---
name: sde-handoff
description: Materialize the derived handoff dossier and stamp it with the current git HEAD, so a fresh session resumes losslessly. Run at the end of each step or session.
allowed-tools: Bash, Read, Write
---

# /sde-handoff

1. **Never hand off a dirty tree.** `git add -A && git commit` any pending step first (one action =
   one commit). If there's nothing to commit, fine.
2. Derive the dossier from `sde status` + the tail of the logs, into `.sde/handoff.md`, following
   `templates/handoff.md` (objective · where-we-are · the single next action · recent · blockers).
   Keep it ≤120 lines.
3. Stamp the **first line**: `derived_from: $(git rev-parse HEAD)`. This is load-bearing —
   `/sde-resume` ignores the dossier if this ≠ current HEAD and re-derives from disk.
4. The dossier is a **hint**; the disk is authoritative. You are not summarizing the conversation —
   you are pointing the next agent at the derived state + the one next action.
