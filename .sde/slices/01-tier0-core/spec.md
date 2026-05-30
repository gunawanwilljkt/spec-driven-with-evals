# Slice 01 — Tier-0/1 core (eval-trust + resumable state machine)

Intent: deliver the evals-first core — an eval-trust protocol and an on-disk, resumable state
machine — proven on real running code. This is the foundation the factory (slice 02) automates.
Non-goals: autonomous orchestration (slice 02); a bespoke runtime.

## Intents
I1. Eval trust is real: a mutant that passes the ordinary unit tests is caught by a trusted eval (GREEN-on-right ∧ RED-on-wrong), demonstrated on running code.
    eval: journey  examples/01-pagination/run.sh   gate=required  mutant=examples/01-pagination/evals/mutant.diff
I2. The state machine is derived, not stored: phase/coverage/trust/next-action are a pure function of disk, computed by a tested deriver.
    eval: unit     framework/tests/test_sde.py     gate=required  mutant=manual
I3. A fresh agent, given only the repo, recovers objective + next action + eval status (resumability).
    eval: journey  proof/resume.py                 gate=flag
I4. The framework is adoptable in tiers (Tier 0 needs no runtime).
    eval: ux       FRAMEWORK.md                    gate=advisory
I5. The eval model is runner-agnostic across web/backend/mobile (mobile via the adapter contract).
    eval: ux       examples/01-pagination/evals/journey.maestro.yaml   gate=flag

## Coverage   (DERIVED — sde status)
I1 ✓  I2 ✓  I3 ✓  I4 ✓  I5 ✓   covered = 5/5

## Intent-audit   (DERIVED)
status: satisfied
note: required intents I1/I2 are eval-trusted (run.sh truth table; deriver test suite). I3 was
      demonstrated by a real cold `claude -p` in Round 1 (re-running needs the claude binary → gate=flag
      here). I4/I5 are advisory/flag (qualitative / documented-contract), excluded from the trust gate.
