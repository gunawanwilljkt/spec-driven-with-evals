# SDE skills (Claude Code plugin)

Ten slash commands operate SDE — eight **Tier-1** verbs (thin orchestration layers over the on-disk
state + the read-only deriver `framework/bin/sde`, sharing one ladder so they can't drift) plus the
two **autonomous drivers** `/sde-factory` (Tier 2, `docs/reasoning/03-*`) and `/sde-auto`.

## Install
Copy these `sde-*/` skill folders where Claude Code discovers skills (e.g. `~/.claude/skills/` or a
plugin directory). Put `framework/bin/sde` on `PATH`, or call `python3 framework/bin/sde`. Python
3.8+ (stdlib only); `git` required.

## The verbs
| Command | Rung / role |
|---|---|
| `/sde-init "<objective>"` | scaffold `.sde/`, capture the objective |
| `/sde-spec` | author numbered intent statements (rung: spec) |
| `/sde-eval` | bind evals + establish **trust** — the centerpiece (rung: bind/trust) |
| `/sde-next` | do the one derived next action, then checkpoint (the drive verb) |
| `/sde-verify` | run the suite + the intent-audit — the gate (rung: evalrun) |
| `/sde-handoff` | stamp the derived dossier for a clean resume |
| `/sde-resume` | fresh-session entry; recover state from disk alone |
| `/sde-status` | print derived state + next action (read-only) |
| `/sde-factory` | **Tier 2** — external mechanical driver; a fresh `claude -p` per ladder rung (`bin/sde-factory.sh`) |
| `/sde-auto` | **autonomous** — drive the ladder hands-off from scratch or `HANDOFF.md`; commits every rung; at ~20% context left asks *continue* (auto-compact) vs *pause+resume*; prints a one-line status |

Typical flow: `/sde-init` → `/sde-spec` → `/sde-eval` → `/sde-next` (×N: freeze, execute…) →
`/sde-verify`. Any step may run in a fresh session; `/sde-resume` continues. For unattended runs use
`/sde-auto` (interactive, context-rot-safe) or `/sde-factory` (detached, fresh process per rung).
Canonical reference: [`../../FRAMEWORK.md`](../../FRAMEWORK.md).
