`SDE v0.2.1` — updated 2026-05-30 19:05 WIB (12:05 UTC) · 11 skills · deriver tests 6/6 · [github](https://github.com/gunawanwilljkt/spec-driven-with-evals)

# SDE — Spec-Driven Development, Evals-First

> Build full-stack and mobile software with an AI agent, where **evals are the first-class citizen**
> that confirm the code follows the *intent* — not just that it runs. State lives on disk so any
> fresh session resumes cleanly before context rot. The same discipline scales from a solo developer
> to an autonomous software factory.

**The thesis:** code generation is solved enough; *intent-conformance* is not. So the unit of trust
is not a passing test — it is a **trustworthy eval**. An eval earns trust only when it is
`GREEN-on-right ∧ RED-on-wrong`: it passes on the intended code **and** is proven to FAIL on a
plausible, intent-violating mutant. That is the structural answer to *"who evals the evals?"*

> **Naming.** "SDE" (state dir `.sde/`, commands `/sde-*`) is the evals-first take built fresh in
> this repo. It learns from — but does not extend — the prior `../sdd/` framework. Prefer "SDD"? A `sed` rename away.

---

## Start here
1. **[`FRAMEWORK.md`](FRAMEWORK.md)** — the canonical reference: the three pillars, the eval-trust
   protocol, the PRIMITIVE/DERIVED state machine + the ladder, the eval tiers, handoff, the commands.
2. **[`examples/01-pagination/`](examples/01-pagination/)** — the runnable proof. `bash run.sh` shows a
   mutant **GREEN on the unit tests but RED on the eval** — "tests pass" vs "intent satisfied," one folder.
3. **[`docs/reasoning/`](docs/reasoning/)** — the verbose design trail (advisor passes + peer rounds).

## The skills (11)
Eight Tier-1 **ladder verbs**, two **autonomous drivers**, one **maintenance** command. Each is a thin
layer over the on-disk state + the tested read-only deriver (`framework/bin/sde`), so they can't drift.

| # | Command | What it does |
|---|---|---|
| 1 | `/sde-init "<objective>"` | Scaffold `.sde/` and capture the objective. Run once at the start. |
| 2 | `/sde-spec` | Author the active slice's numbered **intent statements** — what you mean, not how. |
| 3 | `/sde-eval` | Bind an eval to each intent and establish **trust** (GREEN-on-right ∧ RED-on-wrong) via the eval-blind mutant barrier. **The centerpiece.** |
| 4 | `/sde-next` | Compute the single next action from disk, do it, then checkpoint. **The main drive verb.** |
| 5 | `/sde-verify` | Run the eval suite (→ `runs.log`) + the bounded **intent-audit**. **The gate** that lets a slice be `done`. |
| 6 | `/sde-status` | Print derived state (phase · coverage · trust) + the next action. Read-only. |
| 7 | `/sde-handoff` | Stamp `.sde/handoff.md` with the git HEAD so a fresh session resumes losslessly. |
| 8 | `/sde-resume` | Fresh-session entry: recover the full state from disk alone and continue. |
| 9 | `/sde-auto` | **Autonomous** — drive the ladder hands-off, commit every step; near the context limit, ask *continue* (auto-compact) vs *pause+resume*. Prints a one-line status. |
| 10 | `/sde-factory` | **Tier-2** unattended — an external driver spawns a fresh `claude -p` per rung, bounded by caps + a kill-switch. |
| 11 | `/sde-update` | **Maintenance** — update the framework from its GitHub repo if a newer version exists, **preserving your `.sde/` state**. |

## Example — using every skill, first to last
One full pass over an objective. Steps 1–8 are the lifecycle in order; 9–10 wrap the same loop
hands-off; 11 keeps the framework current.

```text
1)  /sde-init "Users page a list and see every item exactly once"
      → creates .sde/ (objective + the RESUME ladder) and slice 01.

2)  /sde-spec
      → I1: every item present the whole paging session is returned exactly once.
        I2: paging is stable under a concurrent insert (keyset, not OFFSET).

3)  /sde-eval                         # the centerpiece
      → writes an eval per intent; spawns an EVAL-BLIND mutant author (it sees the intent + code,
        never the eval); proves each eval GREEN on the right code AND RED on a plausible mutant
        → both TRUSTED. A vacuous eval (green on the mutant too) is rejected.

4)  /sde-next   (repeat)
      → freeze the spec → implement the slice → every rung is one git commit.

5)  /sde-verify                       # the gate
      → runs the suite into runs.log; runs the bounded intent-audit (an independent agent tries to
        pass every eval yet betray the intent). No hole → slice derives `done`.

6)  /sde-status                       # any time, read-only
      → SDE ⟦01-pagination · done⟧ trust 2/2 · next: objective complete — verify "done when"

7)  /sde-handoff                      # stopping or switching model/effort
      → stamps .sde/handoff.md with the current git HEAD.

8)  /sde-resume                       # in a FRESH session (any model), zero chat history
      → reads the disk, runs sde status, picks up at the exact next action.

— hands-off variants of steps 2–6 —
9)  /sde-auto                         → drives the ladder autonomously, commits each rung, and pauses
                                        for your call (continue / resume) near the context limit.
10) /sde-factory --max-steps 40       → Tier-2: a fresh `claude -p` per rung, unattended; escalates
                                        (never self-declares done) at the objective boundary.

— maintenance —
11) /sde-update
      → current: 0.2.0   latest: 0.3.0   → UPDATE-AVAILABLE; pulls framework fixes + new skills,
        re-installs the /sde-* commands, and PRESERVES your .sde/ project state.
```

## Quick start
**Tier 0 — discipline (no install):**
```bash
cp -r framework/templates/.sde ./.sde      # scaffold; edit objective.md + slices/01-*/spec.md
# write evals + a mutant diff per intent; run them with YOUR runner; an eval shown
# GREEN-on-right ∧ RED-on-wrong is trusted. Follow .sde/RESUME.md.
```
**Tier 1 — gated (Claude Code skills):** install `framework/skills/` where Claude Code finds skills,
then run the flow in the example above. **See the deriver on a real, done slice:**
```bash
python3 framework/bin/sde status --root examples/01-pagination   # → phase=done, trust=2/2
```

## What's in here
```
spec-driven-with-evals/
├─ FRAMEWORK.md              # canonical reference        KNOWN-LIMITATIONS.md  # honest status
├─ docs/{reasoning,decisions}/   # the design trail (00 problem … 04 review) + ADRs
├─ framework/
│  ├─ bin/sde                # read-only state deriver (the ladder) — TESTED (6/6)
│  ├─ bin/sde-factory.sh     # Tier-2 driver   ·   bin/sde-update.sh  # version-checked updater
│  ├─ templates/.sde/        # on-disk state templates (Tier 0)
│  ├─ tests/test_sde.py      # the deriver regression net
│  ├─ skills/                # 11 Claude Code slash-command skills (the table above)
│  ├─ VERSION                # 0.2.0   ·   REPO  # update source repo
├─ examples/01-pagination/   # the worked example + runnable proof
├─ proof/                    # the raw verified proof
└─ .sde/                     # the framework dogfooding ITSELF (its own objective/spec/tasks/handoff)
```

## The three pillars
1. **Eval validity is the product.** Trust = GREEN-on-right ∧ RED-on-wrong, mutant authored behind an
   **information barrier**, a bounded adversarial **intent-audit** for coverage, trust invalidated by drift.
2. **Progressive rigor — one framework, three tiers.** Tier 0 convention → Tier 1 gated skills →
   Tier 2 autonomous factory. You never install machinery you don't need yet.
3. **Proof by dogfooding.** Built using itself; the proof is runnable; resumability is demonstrated on
   the shipping `.sde/` layout by a cold agent following `RESUME.md` by hand (see `docs/reasoning/04`).

---
*Honest about what it is: a discipline + an on-disk state machine + an eval-trust protocol. A vague
intent still yields vague code — the intent-audit surfaces that, it doesn't fix it for you. See
[`KNOWN-LIMITATIONS.md`](KNOWN-LIMITATIONS.md).*
