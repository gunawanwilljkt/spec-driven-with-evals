derived_from: 5659056edd7578e9620f66145dcfbadc5c85baf3
# ^ /sde-handoff stamps this with `git rev-parse HEAD`. A resuming agent ignores this dossier if the
#   fingerprint != current HEAD and re-derives from RESUME.md. (Hint only; disk is authoritative.)

# SDE Handoff @ 2026-05-30

## OBJECTIVE
Build the SDE framework — evals-first Spec-Driven Development for Claude Code.

## WHERE WE ARE  (derived — confirm with `python3 framework/bin/sde status --root .`)
- 01-tier0-core:   phase=done   (core built; eval-trust proven on examples/01-pagination; deriver 6/6; self-derivation works)
- 02-factory-mode: phase=bind   (Tier-2 factory DESIGNED — driver + /sde-factory + reasoning/03; behavioral evals DEFERRED)

## THE SINGLE NEXT ACTION
Bind behavioral evals to the factory intents (I1..I4) and demonstrate a bounded unattended run.
DEFERRED: needs the `claude` CLI + a target project + wired eval runners (see KNOWN-LIMITATIONS.md).
The framework is fully usable at Tier 0/1 today; the factory is the Tier-2 enhancement.

## RECENT  (disk is authoritative)
- Round 2 complete: docs/reasoning/03 + framework/bin/sde-factory.sh + /sde-factory skill + D-11..D-17.
- examples/01-pagination derives `done` (coverage 2/2, trust 2/2); `bash run.sh` PROOF HOLDS.
- framework/bin/sde: 6/6 deriver tests pass (incl. drift, blocked, malformed-log, non-dir slices).
- Live drift demo: extending test_sde.py invalidated I2.unit's trust (stale) until re-established.

## OPEN QUESTIONS / BLOCKERS
- Tier-2 factory behavioral proof (an unattended run) is the main deferred item.
- Final advisor pass pending; then git init + checkpoint commit.
