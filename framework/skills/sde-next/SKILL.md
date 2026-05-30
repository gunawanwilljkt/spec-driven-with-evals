---
name: sde-next
description: Compute the single next action from disk (the ladder) and perform or dispatch it, then checkpoint. The main drive verb of SDE. Run it repeatedly to advance an objective one safe step at a time.
allowed-tools: Read, Write, Edit, Bash, Agent
---

# /sde-next — do the one derived next action, then checkpoint

`sde` = `python3 framework/bin/sde`. One invocation = one **safe, committed step**. This is the unit
of pre-emptive handoff: after it, the session can end and a fresh one resumes losslessly.

## Steps
1. **Derive.** Run `sde next`. It prints `[<slice>] <action>` for the lowest unsatisfied rung —
   a pure function of disk. (`sde status` for the fuller picture.)
2. **Dispatch by phase** (do exactly the one action; don't run ahead):
   | Phase | Action |
   |---|---|
   | spec | `/sde-spec` — author/refine the slice's intent statements |
   | bind / trust | `/sde-eval` — bind evals + establish trust (eval-hidden mutant barrier) |
   | freeze | `cp <slice>/spec.md <slice>/spec.lock.md` (deliberate freeze of a trusted spec) |
   | execute | implement the next ready task: write the code, run its target eval until GREEN |
   | evalrun | `/sde-verify` — run the suite + intent-audit |
   | blocked | spec drifted after freeze → re-derive trust for changed intents, then re-freeze |
   | done (all) | objective complete — verify `objective.md` "done when"; if gaps, add slice(s) |
3. **Record.** Write results to disk immediately (append-only logs; in-place only `spec.md`/`tasks.md`).
4. **Checkpoint.** `git add -A && git commit -m "sde: <slice> <action>"`. One action = one commit, so
   the tree is always clean at a boundary (this is what makes handoff safe — see FRAMEWORK.md §8).
5. **Refresh handoff.** `/sde-handoff` (re-stamps `derived_from: <HEAD>`).

## Stop here if context is getting long
You do **not** estimate your own token usage. Because step 4 left a clean committed boundary, it is
always safe to stop now and let a fresh `/sde-resume` continue. When in doubt, stop after one
action — re-deriving the next step from disk is cheap.

## If an action won't fit one window
That's the one real hazard (an indivisible step too big to finish before context degrades). Don't
push through it — split it: a task too big to fit a window is a spec smell. Add finer `tasks.md`
rows (or thinner intents) and commit that decomposition as the step.
