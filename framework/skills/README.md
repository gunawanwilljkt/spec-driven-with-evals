# SDE skills (Claude Code plugin)

Eight slash commands that operate SDE at **Tier 1**. Each is a thin orchestration layer over the
on-disk state + the read-only deriver (`framework/bin/sde`) — they share the one ladder, so they
can't drift from each other. `/sde-factory` (Tier 2) is added by the factory design
(`docs/reasoning/03-*`).

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

Typical flow: `/sde-init` → `/sde-spec` → `/sde-eval` → `/sde-next` (×N: freeze, execute…) →
`/sde-verify`. Any step may run in a fresh session; `/sde-resume` continues. Canonical reference:
[`../../FRAMEWORK.md`](../../FRAMEWORK.md).
