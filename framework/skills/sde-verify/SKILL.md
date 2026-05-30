---
name: sde-verify
description: Run the active slice's eval suite, append verdicts to runs.log, and run the bounded adversarial intent-audit. This is the gate that decides whether a slice can be `done`. Use after implementing tasks.
allowed-tools: Read, Bash, Write, Edit, Agent
---

# /sde-verify — run the suite + the intent-audit (the gate)

`sde` = `python3 framework/bin/sde`. Active slice = first non-done slice from `sde next`.

## A. Run the eval suite
1. For each eval bound in the slice's `spec.md`, run it with the project's runner. Capture the
   verdict (PASS/FAIL/FLAG) and an evidence path (log/screenshot).
2. Append one line per eval to `.sde/runs.log`:
   `{"ts":...,"slice":"<id>","eval":"<I#.tier>","verdict":"PASS|FAIL|FLAG","gate":"required|flag|advisory","spec_fp":"<sha>","evidence":"<path>","by":"<you>"}`
   (`spec_fp` from `sde status`; a verdict only counts if it matches the current fingerprint.)
3. The gate: `sde status` must show the slice `phase=done` (all `required` evals PASS at the frozen
   spec, all trusted). A `required` FAIL blocks; `flag` surfaces but allows; `advisory` always allows.

## B. The bounded adversarial intent-audit (coverage validity)
Catches the case where every eval passes yet the *set* of evals misses an aspect of intent.

1. Spawn an **independent auditor** subagent (Agent tool). Give it ONLY the slice's **intent
   statements** + the **eval files** (read-only). **Do NOT give it the implementation code** — it
   must reason about what the evals *do and don't* pin, not about the current code.
2. Its task each round: **exhibit a concrete betrayer** — an implementation sketch (pseudocode or
   precise prose) that **passes every eval yet violates a named intent facet** — or return "none
   found" with a one-line justification. A vague "there might be a gap" does not count.
3. Stopping rule (bounded — never an open loop):
   - **HOLE:** any round exhibits a betrayer → write it into `spec.md`'s `## Intent-audit` block and
     add a `tasks.md` row: "add an eval covering <facet>". Re-audit after it's bound + trusted.
   - **SATISFIED:** 2 consecutive rounds find no betrayer.
   - **INCONCLUSIVE:** after 3 rounds total without resolution → record `status: inconclusive` and
     surface to a human. Never spin.
4. Write the outcome into the slice `spec.md` `## Intent-audit` block (status + betrayer if any).

## Output
Report: per-eval verdicts, the gate result (slice done? blocked on which eval?), and the audit
status. If anything is `required`-FAIL or the audit found a HOLE, the next action is to fix it —
`/sde-next` will route there.
