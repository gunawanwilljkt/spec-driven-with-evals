---
name: sde-auto
description: Drive the SDE ladder autonomously — from an empty project or resuming from HANDOFF.md — one COMMITTED step at a time, with context-rot safety. Two modes: interactive (you supervise; it MEASURES remaining context from the session transcript and pauses for your call near the limit) and detached (a fresh process per rung, unattended). Checkpoints after every step so any stop is lossless. The eval-trust barrier is enforced structurally (an eval-blind worktree), and "objective complete" is checked against the full slice roster. Prints a one-line status.
allowed-tools: Bash, Read, Write, Edit, Agent, AskUserQuestion
---

# /sde-auto — autonomous SDE driver (context-rot-safe)

`sde` = `python3 framework/bin/sde`. Drive the ladder to the objective, one COMMITTED step at a time,
terse. **First pick a mode** — they differ in *who paces the loop* and *whether anyone can answer*:

## Modes — choose one up front
- **A · Interactive (supervised, this session).** You loop the rungs; a human is present. Near the
  context limit you ASK them (continue / pause). Use when you want to approve trust + the gate.
- **B · Detached (unattended, a fresh process per rung).** Launch the external driver — it runs a fresh
  `claude -p` per ladder rung, so **no process accumulates context** and there is **no human to ask**:
  ```bash
  bash framework/bin/sde-factory.sh --root . --max-steps 60 --branch sde/auto
  ```
  This is the real "trigger a new process per step." It enforces the eval-blind worktree, caps,
  escalation, and a kill-switch by construction; it commits to a branch and never pushes/deploys.
  **Use B for truly hands-off runs.** Watch `.sde/escalations.log` + `sde status`.

The rest of this skill is **Mode A** (the in-session loop). Mode B is the driver above.

## 0 · Bootstrap — where to start
`HANDOFF.md` at root → read it, then `sde status`, resume. Else `.sde/` exists → `sde status`, resume.
Else (empty) → get an objective (use the user's, or ask once), `/sde-init "<objective>"`, continue.

## 1 · The drive loop (Mode A) — repeat until a STOP CONDITION
1. `sde status` → the single NEXT ACTION + active slice/phase.
2. Do that one rung. Dispatch by phase: `spec`→`/sde-spec` · **`bind`/`trust`→ "Trust rung" below
   (NOT a bare `/sde-eval`)** · `freeze`→`cp spec.md spec.lock.md` · `execute`→implement the next ready
   task · `evalrun`→`/sde-verify` · `blocked`→deliberate re-freeze.
3. **Checkpoint — ALWAYS:** `git add -A && git commit`; `/sde-handoff`; update `HANDOFF.md` if a slice changed.
4. Print the STATUS line.
5. Context guard (§2).

## Trust rung — the eval-blind barrier MUST be structural
You authored the eval, so you already *know* it — a "spawn a subagent that won't look at the eval" rule
is a discipline you can leak, not a guarantee (especially at low effort). Enforce it with a **git
worktree the mutant author physically cannot see the eval in:**
```bash
git worktree add -q /tmp/sde-mutant HEAD
rm -rf /tmp/sde-mutant/evals /tmp/sde-mutant/tests          # the mutant author sees source + intent, NOT the evals
```
Spawn the mutant-author subagent scoped to `/tmp/sde-mutant` (intent + source only); take its diff;
apply it to the MAIN tree; run the bound eval (expect RED) + the others (expect green); revert;
`git worktree remove -f /tmp/sde-mutant`. Only then record trust. **If you cannot run the worktree
path, do NOT claim trust autonomously — hand the trust rung to Mode B (`sde-factory.sh`), which builds
the eval-blind worktree by construction.**

## RULES (unsupervised — these keep you honest)
- Eval trust = GREEN-on-right ∧ RED-on-wrong, mutant authored in the **eval-blind worktree** (above).
- Derive, never trust a label. **Never weaken an eval to pass a gate** → STOP + escalate.
- One rung = one commit. Eval code in `evals/`/`tests/`, referenced by project-root paths.

## Completion check — the roster is disk-derived, not prose-parsed (the autonomy keystone)
A prior false-positive: with a roster of 01–06 but only 01–02 scaffolded, the deriver said "objective
complete" because it cannot see slices that don't exist yet. **Fixed structurally** — `sde next` is now
roster-aware (it routes to *scaffolding the first unbuilt roster slice* rather than declaring complete),
and a dedicated primitive prints the scoreboard from disk — so you do **not** hand-parse `objective.md`:
```bash
sde roster        # one line per PLANNED slice + "roster: <done>/<total>"; exit 0 iff ALL done, else 2
```
The loop trusts the deriver, not a prose read:
1. `sde roster` exit **2** → a roster slice is unscaffolded or not done → **CONTINUE**. `sde next`
   already points at it (an unscaffolded slice's action is `mkdir -p .sde/slices/<id>` then `/sde-spec`).
2. `sde roster` exit **0** (every roster slice `done`) → the objective's "Done when" is a **human** call:
   - Mode A → ask the human to verify `objective.md`'s "Done when".
   - Mode B → append `.sde/escalations.log` ("roster N/N done — human verify Done-when") and EXIT.

(The roster is parsed from `objective.md` bullets shaped `- NN-slug — …`; keep roster lines in that
shape so `sde roster` sees them. A slice off the roster still builds — it just won't gate completion.)

## 2 · Context guard — Mode A ONLY (a MEASUREMENT, not a guess)
> Mode B has **no** context guard: each `claude -p` does one rung and exits, so nothing rots, and
> there is no human to ask — never call `AskUserQuestion` in a detached run.

The model can't introspect its own context, but the bundled meter reads it off **this session's
transcript** (the same token data the status line uses) and **auto-detects the window**:
```bash
python3 framework/bin/ctx.py --json     # {"pct_left":88.6,"window":"1M","basis":"detected",...}
```
After each rung, read `pct_left`. **ASK when `pct_left <= 25`** — the user asked for "~20%"; the extra
margin covers the meter's ~one-turn lag plus one more rung (a single rung can be a big jump). Erring
early is free: step 3 already committed + refreshed the handoff. Also ASK on any **compaction/
summarization system reminder**, regardless of the number.

- If `ctx.py` prints `ctx: ?` or errors (no transcript — e.g. a headless context) → fall back to the
  old backstop: trigger **every ~5 rungs** / on any very large op.
- Heed `basis`: `statusline`/`override`/`detected` = window known (`statusline` = EXACT, from Claude
  Code's own `context_window` via the bridge below). `assumed` = no evidence yet, so it fail-safe
  defaults to the **smaller** window (200k) and ASKs early — safe, and self-corrects to 1M once context
  crosses 200k. To pin it manually: `CONTEXT_LIMIT=1000000` (or `200000`).
- **Optional — exact window (no inference):** the model can't see its window, but Claude Code pipes the
  authoritative `context_window_size` to the *status line*. Tee it to a cache the meter reads. Install the
  meter at a **stable** path — **NOT** inside `framework/` (which `/sde-update` `rm -rf`s; a status line
  piping through a missing file goes blank): `cp framework/bin/ctx.py ~/.claude/ctx.py`, then set your
  `statusLine` command to `python3 ~/.claude/ctx.py --cache | <your existing status-line cmd>`. It writes
  `~/.claude/.ctx-<session>.json` and re-emits the JSON so your status line renders unchanged → basis
  `statusline`. (Match is by the `<session>.jsonl` basename, so the cache and meter agree across paths.)

On trigger, ASK (AskUserQuestion):
> ⚠ Context ~`<pct_left>`% left (window `<window>·<basis>`) — state committed + handoff refreshed, safe to stop.
> • **Continue** → I keep driving; Claude Code auto-compacts. • **Pause** → I stop; resume per §4.

## STATUS — print after EVERY rung, one line (ctx from `python3 framework/bin/ctx.py`)
```
SDE ⟦<slice> · <phase>⟧ trust <k/n> · roster <done>/<total> · ctx <pct_left>%·<window>·<basis> · step <i>/<cap> · @<sha> · next: <action>
```
(`<basis>` lets you confirm the source at a glance: `statusline`/`override`/`detected` = exact-or-known,
`assumed` = fail-safe inference — if you wired the bridge and still see `assumed`, it isn't engaging.)

## §4 · RESUME — print on any pause/stop (resuming is lossless; the repo is the memory)
1. `cd <project> && claude`  ·  2. (optional) `/model` `/effort`  ·  3. `/sde-auto` (or "Read HANDOFF.md and continue").

## STOP CONDITIONS (always end on a committed boundary + STATUS + RESUME)
every roster slice `done` (→ §completion-check human verify) · gate unpassable after retries (→ escalate)
· Mode-A user chose Pause · `--max-steps`/`--cap` reached.
