# Slice 01 — Paginated item list

Intent: a client pages the item list and sees every item present for the whole session exactly
once, stable under concurrent writes. This is the canonical reason keyset pagination exists.
Non-goals: infinite scroll; realtime push; total-count display.

## Intents
I1. Every item present for the whole paging session is returned exactly once — no omission, no duplicate.
    eval: journey  evals/session.py     gate=required  mutant=evals/mutant.diff
I2. Paging is stable under a concurrent insert before the cursor (keyset semantics, not OFFSET).
    eval: journey  evals/session.py     gate=required  mutant=evals/mutant.diff
    eval: ux       evals/I2.rubric.md   gate=flag

## Coverage   (DERIVED — `sde status`; never hand-edit)
I1 ✓  I2 ✓   covered = 2/2

## Intent-audit   (DERIVED — last run by /sde-verify)
status: satisfied
note: 2 consecutive audit rounds found no implementation that passes the session eval yet betrays
      I1/I2. (The naive OFFSET impl was the betrayer the eval was hardened against — see mutant.diff.)
