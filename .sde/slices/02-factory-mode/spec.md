# Slice 02 — Factory mode (Tier 2 autonomous orchestration)

Intent: turn the derived "next action" into a bounded, unattended loop — objective → trusted evals
→ code → eval-confirmed — with anti-collusion barriers, hard caps, escalation, and a kill-switch.
Non-goals: removing human escalation; unbounded autonomy; a single rotting session.

## Intents
I1. A mechanical driver runs ONE ladder step per FRESH context (no single long-lived session that rots).
    eval: (to bind — Round 2 synthesis)
I2. Anti-collusion barriers are enforced automatically across steps: eval-author, mutant-author (eval-hidden), builder, and judge stay independent.
    eval: (to bind — Round 2 synthesis)
I3. Bounded autonomy: hard caps (wall-clock, retries/rung, slices) + escalation + kill-switch + mid-run steer; a gate that won't pass after N retries ESCALATES, never silently advances.
    eval: (to bind — Round 2 synthesis)
I4. Structural guards prevent an agent from weakening an eval or forging trust to pass a gate.
    eval: (to bind — Round 2 synthesis)

## Coverage   (DERIVED — sde status)
I1..I4 — bindings DEFERRED (honest). The Round-2 DESIGN is complete: the mechanical driver
`framework/bin/sde-factory.sh` + the `/sde-factory` skill + `docs/reasoning/03-factory-and-handoff.md`
+ locked decisions D-11..D-17. Binding *behavioral* evals to these intents requires a bounded
**unattended run** (the `claude` CLI + a target project + eval runners), which is not demonstrated in
this repo — see KNOWN-LIMITATIONS.md. The framework is fully usable at Tier 0/1 without this slice.

## Intent-audit   (DERIVED)
status: not-run (slice in `bind` phase — design done, behavioral evals deferred)
