# 03 — Round 2: Pre-emptive Handoff (Q-C) and the Factory (Q-D)

> Round 2 ran two peers in parallel on the deferred Tier-2 questions, each of which ran its own
> advisor pass and self-corrected. This doc synthesizes them into the autonomous design + locked
> Round-2 decisions. Date: 2026-05-30. (Round 1 / core is in `02-peer-round-1-synthesis.md`.)

## Q-C — Pre-emptive context handoff (before rot, not after)

**Core finding: reject context-fraction triggers; make boundaries safe instead.**
- The model has **no reliable token gauge** it can introspect, and the Claude Code harness
  **auto-summarizes** long context — so "context full" never arrives as a discrete edge to fire on.
  A "hand off at X%" rule is both unmeasurable and aimed at a non-event. → demoted to an optional UI hint.
- The reframe that reorganizes everything: **if every step ends at a committed, clean boundary,
  the trigger is allowed to be sloppy.** Handing off "too early" costs only one cheap `sde next`
  re-derivation. So the goal is *safe boundaries + an outer loop*, not an accurate trigger.
- **Zero new primitives.** Durable resume state already exists: the committed git tree + `HEAD`
  (the fingerprint the derived dossier stamps). Pre-emption lives entirely in the orchestration layer.

**The four variants compose (they don't compete):** (b) size each task to one window *at authoring
time*; (c) end every step at a committed boundary (already mandated by RESUME §4); (d) an outer
driver runs one rung per fresh session. Only (a) context-fraction is discarded.

**Top failure mode (the one that actually breaks pre-emption):** *an indivisible ladder action that
won't fit one window* — the agent rots before reaching the next boundary, and no trigger can save it
because there's no safe interior boundary. Mitigations, all within the model: size tasks thin (a too-big
task is a spec smell — split it); use the finest existing interior boundary (the mutant-trust loop already
commits per attempt *k*); and the driver's **no-progress escalation** (below) catches a session that
produced no new commit. Corollary: *one commit per action ⇒ committed iff recorded*; never hand off a
dirty tree (a Stop-hook can enforce this), and because trust/runs are latest-wins keyed by
`(eval_hash, spec_fp)`, a duplicate re-append after resume is idempotent.

**Tiering:** Tier 1 = `/sde-handoff` + "one action then checkpoint", human chooses cadence by task
boundary (token introspection appears nowhere). Tier 2 = the external driver. A Stop-hook is an
optional guardrail that enforces the clean-boundary invariant mechanically.

## Q-D — The autonomous factory (smallest loop safe unattended)

**The loop = an external MECHANICAL shell driver (variant b).** It spawns a **fresh,
information-scoped `claude -p` per ladder rung**, keyed off the deriver's `phase=` token from
`sde status`. The dispatcher contains **no LLM creativity** — creativity lives inside the fresh
per-rung agents. Pseudocode lives in [`framework/bin/sde-factory.sh`](../../framework/bin/sde-factory.sh).

**Executor-in-harness (the sharp move).** Agents only **propose** artifacts (spec text, eval code,
a mutant diff, implementation code). Only the **driver** runs the evals/mutants and writes
`trust.log` / `runs.log`. A builder therefore cannot grade its own work — the verdict is produced by
the mechanical layer, from real runs, not by the agent that wrote the code.

**Anti-collusion = filesystem-enforced scoping, not etiquette:**
- **Mutant author → an eval-blind `git worktree`**: a checkout with the eval files *removed/ignored*,
  so the mutant author literally cannot see the assertion it must beat (the §D-3 information barrier,
  enforced by the filesystem).
- Spec author, builder, judge each get a fresh context with only the inputs their rung needs.
- **Different-model judge pinned at BOTH rung 2 and rung 5** for semantic/ux evals: rung 2 is the
  golden-pair trust run (judge must FAIL the bad fixture, PASS the good); rung 5 is grading real
  output. The pin guarantees a model never trust-validates *or* grades its own output.

**Bounded autonomy — the minimal safe set (one ceiling, not five):**
- **HEAD-based no-progress retry cap.** The no-progress signal is *"the same rung produced no new
  commit"* (`HEAD` unchanged), **not** rung-identity — a legitimate multi-iteration builder lands
  commits and resets the counter; only a rung that spins without advancing trips. Commit-spam can't
  defeat it (a cosmetic commit doesn't climb the rung), so `MAX_STEPS` remains the backstop.
- **`MAX_STEPS`** total budget · **`.sde/STOP`** kill-switch (checked each iteration) · a config-reread
  **steer** · an **escalation log**.
- **Hard stop = block the slice + escalate + (advance to an independent slice | stop)** — never
  auto-weaken a gate, never silently advance.
- **`sde next` exit-0 ESCALATES for human "done-when" review — it does not auto-succeed.** The deriver
  deliberately refuses to adjudicate the objective's "done when"; auto-succeeding there would invent
  the silent-ship decision. Fail-closed to a human.

**Scope (stated, narrow on purpose):** the factory operates on **human-seeded slices** (slice dirs
pre-exist; the ladder starts at `spec`). It does **not** author new slices to close an objective gap —
that's larger than "smallest safe loop" and would need a slice-seeding phase. This is why a separate
"total slices" cap is dropped: under the narrow read it's subsumed by `MAX_STEPS` + the fixed seeded count.

**The three damage modes, each closed by an EXISTING rule:**
1. *Agent weakens an eval to pass the gate* → editing the eval changes `eval_hash` ⇒ trust goes
   `stale` ⇒ rung 2 re-opens ⇒ a fresh eval-blind mutant must kill the weakened eval (it won't).
2. *Forged trust/run events* → the driver (not the agent) writes them, from real runs; agents lack
   write access to the logs in their scoped context.
3. *Loop "completes" a slice whose eval is vacuous* → a vacuous eval can't be `trusted` (it stays
   GREEN on the mutant) ⇒ rung 2 never passes ⇒ the slice can't reach `done`.

**`/sde-factory`** is a config + launch + report **front-end** — it cannot *be* the daemon (a long
session rots). The durable loop is the external driver, which **commits to a branch and never
pushes/deploys.**

## Locked Round-2 decisions
- **D-11** Pre-emption adds zero new primitives: safe committed boundaries + git HEAD + the derived dossier.
- **D-12** No token-fraction introspection at any tier; cadence = task boundary (Tier 1) / fresh session per rung (Tier 2).
- **D-13** Tier-2 = external mechanical driver, fresh `claude -p` per rung, keyed off `sde` `phase=`/exit codes.
- **D-14** Executor-in-harness: agents propose; only the driver runs evals/mutants and writes the logs.
- **D-15** Mutant anti-collusion enforced by an **eval-blind worktree**; different-model judge pinned at rungs 2 & 5.
- **D-16** Minimal safe set: HEAD-based no-progress cap + MAX_STEPS + `.sde/STOP` + steer + escalation log; hard stop = block+escalate, never auto-weaken; `sde next` exit-0 escalates done-when review.
- **D-17** Tier-2 default operates on human-seeded slices; autonomous slice-authoring is out of scope.

These bind the Tier-2 artifacts (`/sde-factory`, `framework/bin/sde-factory.sh`). The factory is
**designed and its driver is written; an end-to-end unattended run is not demonstrated in this repo**
(see `KNOWN-LIMITATIONS.md`).
