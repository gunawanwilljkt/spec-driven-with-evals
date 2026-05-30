---
name: sde-factory
description: Launch and supervise the SDE Tier-2 autonomous factory — a bounded loop that drives an objective through the ladder unattended, with fresh context per step. Front-end only; the durable loop is the external driver.
allowed-tools: Bash, Read, Write
---

# /sde-factory — configure, launch, report (Tier 2)

This skill is a **front-end**. It must NOT *be* the loop — a long-lived session rots. The durable loop
is the external mechanical driver `framework/bin/sde-factory.sh`, which spawns a fresh `claude -p` per
ladder rung (nothing lives long enough to rot). See `docs/reasoning/03-factory-and-handoff.md`.

1. **Preflight.** Confirm a git repo + `.sde/` exist (`sde status`), and that the required-eval runners
   are wired in the driver (the `# RUNNER:` hooks). Confirm slices are **human-seeded** — the factory
   does not author new slices to close an objective gap (D-17).
2. **Configure & arm.** Caps: `--max-steps`, `--retry-cap`, `--branch`, `--judge-model` (a model
   **different** from the builder, for semantic-eval trust + grading). Arm controls: touch `.sde/STOP`
   to kill; write `.sde/STEER` to redirect once.
3. **Launch** (in the background or a separate terminal):
   ```bash
   bash framework/bin/sde-factory.sh --root . --max-steps 60 --retry-cap 3 \
        --branch sde/factory --judge-model claude-sonnet-4-6
   ```
4. **Report.** `tail .sde/escalations.log` and `sde status`. The driver **commits to a branch and never
   pushes/deploys.** When all seeded slices are `done` it **escalates for human "done-when" review** —
   it never auto-succeeds.

**Why it's safe (all structural — not prompt etiquette):** the driver, not the agent, writes the
verdicts, so a builder can't grade itself; weakening an eval changes its hash and **re-opens its trust
gate**; a vacuous eval can never be `trusted`, so its slice can never reach `done`. The bounds —
HEAD-based no-progress cap, `MAX_STEPS`, `.sde/STOP` — guarantee it halts.
