---
name: sde-auto
description: Drive the SDE ladder autonomously — from an empty project or resuming from HANDOFF.md — one COMMITTED step at a time, with context-rot safety. It checkpoints after every step so any stop is lossless; when context runs low it pauses and asks you to continue (auto-compact) or stop+resume cleanly; and it can run each step in a fresh process. Prints a one-line status. Use to run SDE hands-off.
allowed-tools: Bash, Read, Write, Edit, Agent, AskUserQuestion
---

# /sde-auto — autonomous SDE driver (context-rot-safe)

`sde` = `python3 framework/bin/sde`. You are the autonomous driver: advance the ladder toward the
objective, **one committed step at a time**, terse, never letting a full context window lose work.
Operate in **first person, minimal prose** — emit the one-line STATUS, not essays.

## 0 · Bootstrap — where to start
- `HANDOFF.md` exists at the project root → read it, then `sde status`. Resume at the derived next action.
- else `.sde/` exists → `sde status`. Resume.
- else (empty project) → you need an objective. If the user supplied one, run `/sde-init "<objective>"`;
  otherwise ask once (AskUserQuestion: "What's the objective?"), then `/sde-init`. Then continue.

## 1 · The drive loop — repeat until a STOP CONDITION
Each iteration = exactly ONE ladder rung, then a durable checkpoint:
1. `sde status` → the single NEXT ACTION + active slice/phase.
2. Do that one rung, obeying the RULES below. Dispatch by phase (same mapping as `/sde-next`):
   `spec`→`/sde-spec` · `bind`/`trust`→`/sde-eval` · `freeze`→`cp spec.md spec.lock.md` ·
   `execute`→implement the next ready task · `evalrun`→`/sde-verify` · `blocked`→deliberate re-freeze.
3. **Checkpoint — ALWAYS, even mid-slice:** `git add -A && git commit -m "sde-auto: <slice> <rung>"`;
   refresh `.sde/handoff.md` (`/sde-handoff`); if a slice's status changed, update `HANDOFF.md`'s
   "What is DONE" + "NEXT ACTION".
4. Print the STATUS line.
5. Run the CONTEXT GUARD (§2). Then loop.

## RULES — non-negotiable (you are unsupervised; these keep you honest)
- **Eval trust = GREEN-on-right ∧ RED-on-wrong.** Mutants authored **eval-blind** (a *separate*
  subagent that sees intent + source, never the eval). No slice is `done` until its required evals are
  trusted **and** pass at the frozen spec.
- **Derive, never trust a label** — `sde status` is the source of truth; if you didn't run it, you
  don't know the state. Eval code lives in `evals/`/`tests/`.
- **Never weaken an eval to pass a gate.** If a gate won't pass after ~3 tries → STOP + escalate (write
  `.sde/escalations.log`, tell the user).
- **`sde status` exit 0** ("objective complete — verify done-when") → STOP and ask the human; never
  self-declare the objective done.
- One rung = one commit. The repo is the memory; the chat is a cache.

## 2 · Context guard — the "~20% left" decision
You **cannot** measure your own context precisely. Use these signals, in order; because §1.3 already
committed, erring EARLY is free:
- the harness reports context usage ≤ ~20% remaining → trigger;
- you receive an auto-summarization / compaction system reminder → context just filled → trigger;
- backstop heuristic: after every **5** rungs, or after any very large operation → trigger proactively.

On trigger, STOP the loop and ask (AskUserQuestion), having already committed + refreshed the handoff:
> ⚠ Context ~20% left — state committed + handoff refreshed, safe to stop.
> • **Continue** → I keep driving; Claude Code auto-compacts the context.
> • **Pause & resume** → I stop now; resume losslessly (see RESUME). Nothing is lost.
Continue → keep looping. Pause → print RESUME (§4) and STOP.

## 3 · Hands-off mode — a fresh process per step (no context to rot)
To sidestep the 20% problem entirely, run each rung in a **new process**. Launch the external driver,
which spawns a fresh `claude -p` per ladder rung (nothing accumulates context across steps):
```bash
bash framework/bin/sde-factory.sh --root . --max-steps 40   # add --branch sde/auto
```
Watch `.sde/escalations.log` + `sde status`. The driver commits to a branch, **never pushes/deploys**,
and escalates (never self-declares) at the objective boundary. Use this for truly unattended runs;
use the in-session loop (§1) when you want to approve the continue/pause calls yourself.

## STATUS — print after EVERY rung, exactly one line
```
SDE ⟦<slice> · <phase>⟧ trust <k/n> · step <i>/<cap> · ctx <ok|low> · @<short-sha> · next: <action>
```
e.g. `SDE ⟦03-group-chat · spec⟧ trust 0/0 · step 7/40 · ctx ok · @c847e17 · next: author intents`

## 4 · RESUME — print this whenever you pause or stop
Resuming is lossless; the repo is the memory.
1. open a fresh session in this directory:  `cd <project-dir> && claude`
2. (optional) different model/effort:        `/model` · `/effort`
3. run **`/sde-auto`**  (or say: "Read HANDOFF.md and continue")
→ it runs `sde status`, reads `HANDOFF.md`, and picks up at the exact next action.

## STOP CONDITIONS (always end on a committed boundary + a STATUS line + RESUME)
objective done-when met (→ ask human) · gate unpassable after retries (→ escalate) · user chose Pause ·
`--max-steps` cap reached.
