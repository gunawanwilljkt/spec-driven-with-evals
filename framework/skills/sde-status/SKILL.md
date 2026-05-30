---
name: sde-status
description: Print the derived state (per-slice phase, coverage, eval-trust) and the single next action — purely from disk. Read-only.
allowed-tools: Bash, Read
---

# /sde-status

Run `python3 framework/bin/sde status --root .` (or `sde status` if on PATH). It derives, from disk
alone — storing nothing:
- each slice's **phase** (the lowest unsatisfied rung of the ladder),
- **coverage** (intents bound to ≥1 eval),
- **trust** (required evals that are GREEN-on-right ∧ RED-on-wrong at the current spec),
- the objective-level **NEXT** action.

For one eval's trust detail (why it's `untrusted`/`stale`): `sde trust <slice>`. This skill never
mutates state — it's a pure read of the primitives.
