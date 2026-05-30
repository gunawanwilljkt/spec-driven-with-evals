---
name: sde-init
description: Scaffold .sde/ in the current project from the SDE templates and capture the objective. Run once at the start of an objective.
allowed-tools: Bash, Read, Write
---

# /sde-init "&lt;objective&gt;"

1. Copy the template tree into the project: `cp -r <framework>/templates/.sde ./.sde`
   (objective.md, decisions.md, RESUME.md, runs.log, and a sample slice).
2. Write `.sde/objective.md`: the north-star paragraph + the "Done when" success criteria from the
   argument; list the first slice(s) in the roster.
3. Rename `slices/01-EXAMPLE-SLICE` → `slices/01-<slug>` for your first feature and clear the
   template intents (you'll author them with `/sde-spec`).
4. `git init` if the project isn't a repo yet — SDE checkpoints with real commits, and the handoff
   fingerprint is `git rev-parse HEAD`. Commit the scaffold.
5. Print `python3 <framework>/bin/sde status --root .` (everything at rung 0/spec) and tell the user
   the next action is `/sde-spec`.

Eval code lives in the project's normal structure (`evals/`, `tests/`), referenced from `spec.md`
by paths relative to the project root — not inside `.sde/`.
