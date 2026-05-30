# Slice 01 — <slice title>

Intent: <one paragraph of context — what this slice is for, in the user's terms>.
Non-goals: <explicitly out of scope, so the intent-audit doesn't flag absent things as holes>.

## Intents
<!-- Numbered intent statements: WHAT we mean, not HOW. Each MUST bind ≥1 eval.
     gate=required (FAIL blocks the slice) | flag (surfaces, doesn't block) | advisory (always allows).
     Each required eval names mutant=<path-to-diff> (its RED-on-wrong evidence) or mutant=manual. -->
I1. <a single, checkable statement of intent>.
    eval: contract  evals/I1.<name>.py     gate=required  mutant=evals/I1.mutant.diff
I2. <another intent>.
    eval: journey   evals/I2.<name>.py      gate=required  mutant=evals/I2.mutant.diff
    eval: ux        evals/I2.rubric.md      gate=flag

## Coverage   (DERIVED — regenerate with `sde status`; never hand-edit)
I1 ✓  I2 ✓   covered = 2/2

## Intent-audit   (DERIVED — last run by `/sde-verify`)
status: <satisfied | hole | inconclusive | not-run>
<!-- if hole: betrayer: "<impl that passes all evals yet violates a named facet>" → add an eval -->
