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
> this repo. It learns from — but does not extend — the prior `../sdd/` framework (kept as a
> separate reference). Prefer the name "SDD"? It's a `sed` rename away.

---

## Start here
1. **[`FRAMEWORK.md`](FRAMEWORK.md)** — the canonical reference (read first): the three pillars, the
   eval-trust protocol, the PRIMITIVE/DERIVED state machine + the ladder, the eval tiers, handoff,
   the slash commands.
2. **[`examples/01-pagination/`](examples/01-pagination/)** — the runnable proof. `bash run.sh`
   shows a mutant that is **GREEN on the unit tests but RED on the eval** — "tests pass" vs "intent
   satisfied" in one folder.
3. **[`docs/reasoning/`](docs/reasoning/)** — the verbose design trail (follow-along): the problem &
   prior-art assessment, the advisor pass, and the peer-brainstorm synthesis with locked decisions.

## What's in here
```
spec-driven-with-evals/
├─ FRAMEWORK.md              # canonical reference
├─ README.md                 # this file
├─ KNOWN-LIMITATIONS.md      # honest status — what's proven vs designed vs deferred
├─ docs/
│  ├─ reasoning/             # 00 problem+prior-art · 01 advisor · 02 peer round 1 · 03 factory…
│  └─ decisions/             # ADRs
├─ framework/
│  ├─ templates/.sde/        # the on-disk state templates (Tier 0: pure convention)
│  ├─ bin/sde                # read-only state deriver (the ladder, automated) — TESTED
│  ├─ tests/test_sde.py      # 5/5 passing — the deriver regression net
│  └─ skills/                # 8 Claude Code slash-command skills (Tier 1)
├─ examples/01-pagination/   # the worked example + runnable proof (SC-1, SC-2, SC-5, SC-6)
├─ proof/                    # the raw verified proof (referenced by docs/reasoning/02)
└─ .sde/                     # the framework dogfooding ITSELF (its own objective/spec/tasks/handoff)
```

## Quick start

**Tier 0 — discipline (no install):**
```bash
cp -r framework/templates/.sde ./.sde          # scaffold; edit objective.md + slices/01-*/spec.md
# write evals + a mutant diff per required intent; run them with YOUR runner;
# an eval you've shown GREEN-on-right ∧ RED-on-wrong is trusted. Follow .sde/RESUME.md.
```
**Tier 1 — gated (Claude Code skills):**
```
/sde-init "Page the list so every item appears exactly once"
/sde-spec → /sde-eval → /sde-next → /sde-verify     # each may run in a fresh session
/sde-resume                                          # after any context reset
```
**See the deriver work on a real, complete slice:**
```bash
python3 framework/bin/sde status --root examples/01-pagination     # → phase=done, trust=2/2
python3 framework/bin/sde status --root .                          # the framework's own state
```

## The three pillars
1. **Eval validity is the product.** Trust = GREEN-on-right ∧ RED-on-wrong, with the mutant authored
   behind an **information barrier** (the mutant-author never sees the eval), a bounded adversarial
   **intent-audit** for coverage, and a trust ledger invalidated by drift.
2. **Progressive rigor — one framework, three tiers.** Tier 0 convention → Tier 1 gated skills →
   Tier 2 autonomous factory. You never install machinery you don't need yet.
3. **Proof by dogfooding.** It's built using itself; the proof is runnable; resumability is
   demonstrated on the **shipping `.sde/` layout** — a cold agent, *forbidden from the deriver*,
   followed `RESUME.md` by hand and recovered the correct objective + next action + eval status,
   matching `sde next` (see `docs/reasoning/04`).

## How it relates to the prior `../sdd/`
That framework is genuinely strong; this one keeps its best ideas (state-on-disk, fresh-context
subagents, default-FAIL, anti-collusion judge) and adds what it lacked: **eval *validity*** (not
just eval *existence*), **right-sized ceremony** (no monolithic untested CLI — a small tested
deriver instead), and **proof over assertion**. See `docs/reasoning/00-problem-and-prior-art.md`.

---
*Honest about what it is: a discipline + an on-disk state machine + an eval-trust protocol. A vague
intent still yields vague code — the intent-audit surfaces that, it doesn't fix it for you. See
[`KNOWN-LIMITATIONS.md`](KNOWN-LIMITATIONS.md).*
