---
name: sde-auto
description: Drive the SDE ladder autonomously — from an empty project or resuming from HANDOFF.md — one COMMITTED step at a time, with context-rot safety. Two modes: interactive (you supervise; it pauses for your call near the context limit) and detached (a fresh process per rung, unattended). Checkpoints after every step so any stop is lossless. The eval-trust barrier is enforced structurally (an eval-blind worktree), and "objective complete" is checked against the full slice roster. Prints a one-line status.
allowed-tools: Bash, Read, Write, Edit, Agent, AskUserQuestion
---

# /sde-auto — autonomous SDE driver (context-rot-safe)

`sde` = `python3 framework/bin/sde`. Drive the ladder to the objective, one COMMITTED step at a time,
terse. **First pick a mode** — they differ in *who paces the loop* and *whether anyone can answer*:

## Modes — choose one up front
- **A · Interactive (supervised, this session).** You loop the rungs; a human is present. Near the
  context limit you ASK them (continue / pause). Use when you want to approve trust + the gate.
- **B · Detached (unattended, a fresh process per rung).** Launch the external driver — it runs a fresh
  `claude -p` per ladder rung, so **no process accumulates context** and there is **no human to ask**:
  ```bash
  bash framework/bin/sde-factory.sh --root . --max-steps 60 --branch sde/auto
  ```
  This is the real "trigger a new process per step." It enforces the eval-blind worktree, caps,
  escalation, and a kill-switch by construction; it commits to a branch and never pushes/deploys.
  **Use B for truly hands-off runs.** Watch `.sde/escalations.log` + `sde status`.

The rest of this skill is **Mode A** (the in-session loop). Mode B is the driver above.

## 0 · Bootstrap — where to start
`HANDOFF.md` at root → read it, then `sde status`, resume. Else `.sde/` exists → `sde status`, resume.
Else (empty) → get an objective (use the user's, or ask once), `/sde-init "<objective>"`, continue.

## 1 · The drive loop (Mode A) — repeat until a STOP CONDITION
1. `sde status` → the single NEXT ACTION + active slice/phase.
2. Do that one rung. Dispatch by phase: `spec`→`/sde-spec` · **`bind`/`trust`→ "Trust rung" below
   (NOT a bare `/sde-eval`)** · `freeze`→`cp spec.md spec.lock.md` · `execute`→implement the next ready
   task · `evalrun`→`/sde-verify` · `blocked`→deliberate re-freeze.
3. **Checkpoint — ALWAYS:** `git add -A && git commit`; `/sde-handoff`; update `HANDOFF.md` if a slice changed.
4. Print the STATUS line.
5. Context guard (§2).

## Trust rung — the eval-blind barrier MUST be structural
You authored the eval, so you already *know* it — a "spawn a subagent that won't look at the eval" rule
is a discipline you can leak, not a guarantee (especially at low effort). Enforce it with a **git
worktree the mutant author physically cannot see the eval in:**
```bash
git worktree add -q /tmp/sde-mutant HEAD
rm -rf /tmp/sde-mutant/evals /tmp/sde-mutant/tests          # the mutant author sees source + intent, NOT the evals
```
Spawn the mutant-author subagent scoped to `/tmp/sde-mutant` (intent + source only); take its diff;
apply it to the MAIN tree; run the bound eval (expect RED) + the others (expect green); revert;
`git worktree remove -f /tmp/sde-mutant`. Only then record trust. **If you cannot run the worktree
path, do NOT claim trust autonomously — hand the trust rung to Mode B (`sde-factory.sh`), which builds
the eval-blind worktree by construction.**

## RULES (unsupervised — these keep you honest)
- Eval trust = GREEN-on-right ∧ RED-on-wrong, mutant authored in the **eval-blind worktree** (above).
- Derive, never trust a label. **Never weaken an eval to pass a gate** → STOP + escalate.
- One rung = one commit. Eval code in `evals/`/`tests/`, referenced by project-root paths.

## Completion check — never trust `sde next` exit-0 alone (the autonomy keystone)
The deriver reports "objective complete" when all *scaffolded* slices are done — but it **cannot see
slices that were never scaffolded.** With a roster of 01–06 and only 01–02 scaffolded, it FALSELY says
complete. So when `sde next` reports "objective complete":
1. Read `objective.md`'s **Slices** roster (the planned slice ids).
2. For EACH roster id: does `.sde/slices/<id>/` exist AND derive `done`?
3. If any is **missing** → `mkdir -p .sde/slices/<id>` and **CONTINUE** (its next action is `/sde-spec`).
   If any is **not done** → CONTINUE. **Do not stop while any roster slice is unbuilt.**
4. Only when EVERY roster slice is `done` → the objective's "Done when" is a **human** call:
   - Mode A → ask the human to verify `objective.md`'s "Done when".
   - Mode B → append `.sde/escalations.log` ("roster complete — human verify Done-when") and EXIT.

## 2 · Context guard — Mode A ONLY
> Mode B has **no** context guard: each `claude -p` does one rung and exits, so nothing rots, and
> there is no human to ask — never call `AskUserQuestion` in a detached run.

You cannot measure context precisely. Trigger on: a compaction/summarization system reminder, or a
backstop of **every ~5 rungs** / any very large op. Because step 3 already committed + refreshed the
handoff, erring early is free. On trigger, ASK (AskUserQuestion):
> ⚠ Context ~20% left — state committed + handoff refreshed, safe to stop.
> • **Continue** → I keep driving; Claude Code auto-compacts. • **Pause** → I stop; resume per §4.

## STATUS — print after EVERY rung, one line
```
SDE ⟦<slice> · <phase>⟧ trust <k/n> · step <i>/<cap> · roster <done>/<total> · @<sha> · next: <action>
```

## §4 · RESUME — print on any pause/stop (resuming is lossless; the repo is the memory)
1. `cd <project> && claude`  ·  2. (optional) `/model` `/effort`  ·  3. `/sde-auto` (or "Read HANDOFF.md and continue").

## STOP CONDITIONS (always end on a committed boundary + STATUS + RESUME)
every roster slice `done` (→ §completion-check human verify) · gate unpassable after retries (→ escalate)
· Mode-A user chose Pause · `--max-steps`/`--cap` reached.
