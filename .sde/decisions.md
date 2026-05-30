# Decisions — append-only ADR log (framework self-build)

## 2026-05-30 — Name + distinctness  [slice:objective]
Decision: name it SDE (Spec-Driven, Evals-first); state dir `.sde/`; commands `/sde-*`.
Why: keep it cleanly distinct from the prior `../sdd/` reference (which the user wants kept as a
separate reference) and put EVALS in the name. Trivial to rename to SDD via sed if preferred.
By: claude.

## 2026-05-30 — D-1..D-9 locked (see docs/reasoning/02)  [slice:01-tier0-core]
Decision: lock the Round-1 decisions: spec = numbered intent + bound evals + coverage (D-1);
eval trust = GREEN-on-right ∧ RED-on-wrong (D-2); mutant anti-collusion via eval-hidden information
barrier (D-3); PRIMITIVE vs DERIVED state (D-4); resume IS derivation, one ladder (D-5); trust
cached, invalidated by drift → stale (D-6); no bespoke CLI, stock git/grep/diff + a tested
read-only deriver (D-7); mobile shown honestly via the runner-adapter contract (D-8); proof before
framework (D-9).
Why: see the advisor pass (docs/reasoning/01) and peer synthesis (docs/reasoning/02).
Alternatives rejected: extend ../sdd/ in place (user chose a fresh best-effort build).
By: claude.

## 2026-05-30 — Eval paths are project-root-relative  [slice:01-tier0-core]
Decision: eval/mutant paths in spec.md resolve against the project root (parent of .sde/), not the
slice dir, so eval code lives in the repo's normal structure (evals/, tests/).
Why: burying eval code in a hidden state dir is unnatural and breaks imports.
By: claude.

## 2026-05-30 — Round-2 decisions D-11..D-17 (factory + handoff)  [slice:02-factory-mode]
Decision: lock the Tier-2 design — pre-emption adds zero new primitives (D-11); no token-fraction
introspection (D-12); external mechanical driver, fresh `claude -p` per rung (D-13); executor-in-harness
(D-14); eval-blind worktree + different-model judge at rungs 2&5 (D-15); minimal safe set + escalate-never-
auto-weaken + exit-0 escalates done-when (D-16); human-seeded slices only (D-17). Full record: reasoning/03.
By: claude (Round-2 peers, each self-advised).

## 2026-05-30 — Re-established I2.unit trust after extending its eval  [slice:01-tier0-core]
Decision: after adding the non-dir-slices regression test to test_sde.py (the eval bound to I2), its
eval_hash drifted and trust correctly went `stale`; re-stamped trust.log once the suite was re-confirmed
green (6/6) and still catching the deliberately-wrong drift/blocked states.
Why: this is D-6 working — a changed eval must be re-trusted. Recorded as a live demonstration.
By: claude.
