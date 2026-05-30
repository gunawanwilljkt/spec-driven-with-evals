# RESUME — the SDE ladder

> **You are an agent (or operator) resuming with ZERO chat history.** The repo is the truth; the
> chat is gone. Do **not** guess what's next — **derive** it. Every step below is a plain disk
> read. Two fresh agents running this on the same disk reach the same next action. That is the
> whole point: it is why a session can rot or die and the work survives intact.
>
> Tier 1 automates this exact walk as `sde status` / `sde next`. The walk is identical; the script
> just computes it deterministically. (See `framework/bin/sde`.)

## 0 — Orient (read the primitives)
```bash
cat .sde/objective.md            # north star + "done when"
ls  .sde/slices/                 # a slice EXISTS iff its directory exists
tail -n 20 .sde/decisions.md     # recent decisions / ADRs
```
Optionally read `.sde/handoff.md` — but **only as a hint.** Verify its first line
`derived_from: <sha>` equals `git rev-parse HEAD`. If it differs, the handoff is **stale → ignore
it** and trust the derivation below. A handoff never overrides the disk.

## 1 — Per-slice phase = the lowest UNSATISFIED rung
For each slice `S` in `.sde/slices/` (lexical order), walk the rungs **top-down**. The **first rung
whose guard fails** is `S`'s current phase; its action is what `S` needs next.

| Rung | Phase | Guard — how to check (pure disk read) | Action if it FAILS |
|---|---|---|---|
| 0 | spec | `spec.md` exists and has ≥1 intent line: `grep -qE '^I[0-9]' .sde/slices/$S/spec.md` | author `spec.md` intents |
| 1 | bind | **every** intent block has ≥1 *parseable* `eval:` binding (`eval: <tier> <path> gate=<g> [mutant=<p>]`); read `spec.md` — each `^I#` block (until the next `^I#`/`^##`) must contain such a line. **0 parseable bindings ⇒ bind fails.** The `## Coverage` `covered = N/N` line is a derived convenience, not the guard. | bind an eval to each unbound intent |
| 2 | trust | **every** `gate=required` eval is *trusted*: in `trust.log`, its latest events include `result:killed` **and** `result:passed` at the **current** `eval_hash` + `spec_fp`. (Derive — see Rule A + **Fingerprints** below.) | author/repair the mutant or the eval until both events log |
| 3 | freeze | `spec.lock.md` exists **and** `diff .sde/slices/$S/spec.md .sde/slices/$S/spec.lock.md` is empty | freeze: `cp spec.md spec.lock.md` (deliberate) |
| 4 | execute | every *ready* task (its `deps` are done) has `status=done` in `tasks.md` | run the next ready task |
| 5 | evalrun | latest `runs.log` verdict for **each** `gate=required` eval of `S` = `PASS` at the current `spec_fp` | run the eval suite; fix the failing eval's task |
| 6 | **done** | rung 5 satisfied and no spec drift | nothing — `S` is complete |
| — | **blocked** | special: `diff spec.md spec.lock.md` is **non-empty after a freeze** | deliberate re-freeze → re-derive trust (rung 2) for changed intents |

## 2 — Objective next action = f(disk)
1. For each slice, compute its rung (§1).
2. Pick the **first** slice (lexical order) that is **not `done`** and **not `blocked`** and whose
   rung has a *ready* action (rung-4 readiness also needs an unclaimed-or-stale task — see Rule C).
3. **That rung's action, for that slice, is THE next action.** Do it. (Tier 1: `/sde-next` performs
   or dispatches it.)
4. If a slice is `blocked`, resolving it is the next action.
5. If **all** slices are `done`, re-read `.sde/objective.md` "done when": if met, the **objective is
   complete**; if not, the next action is to add the slice(s) that close the gap.

## 3 — The three rules that stop the state from lying
**Rule A — DERIVE trust; never trust a `trusted:true` label (there is none).**
`trusted(E)` ⇔ `trust.log` shows, for `E`, a latest `result:killed` AND a latest `result:passed`,
both stamped with the **current** `eval_hash` AND `spec_fp` (both defined under **Fingerprints**
below). If the eval file changed (`eval_hash` drift) or an intent statement changed (`spec_fp`
drift) since, those events are **stale** → `E` is **not** trusted → rung 2 fails → re-verify. (This
is what makes drift safe and journey/mobile evals affordable.)

**Rule B — DERIVE done; never trust a `done` label alone.**
A task counts as done only if: its row says `done` **and** `runs.log` shows `PASS` for each of its
**`gate=required`** `targets` evals at the current `spec_fp` **and** those evals are trusted (Rule
A). `flag`/`advisory` targets do not gate (this matches rung 5, which scopes to required evals). A
mismatch ⇒ rung 5 fails ⇒ next action = "re-run / fix that task", regardless of the label.

**Rule C — Claims are stale-reclaimable (multi-agent).**
A task `in_progress` with `owner@ts` may be reclaimed by another agent if `now − ts` exceeds the
staleness window (default 30 min) with no newer commit by that owner. Per-slice directories are
disjoint write sets; shared root logs (`runs.log`, `decisions.md`) are append-only.

**Fingerprints — how to compute `eval_hash` and `spec_fp` BY HAND (rungs 2 & 5 need these).**
You need a SHA-256 tool (`shasum -a 256`); plain `cat/grep/diff` is not enough for the strict check.
- **`eval_hash`** = `shasum -a 256 <eval-file>` → `sha256:` + the first 12 hex chars.
- **`spec_fp`** = SHA-256 of `spec.md` **with the derived blocks removed** — drop everything from a
  `## Coverage` or `## Intent-audit` heading until the next `## ` heading, right-strip each remaining
  line, join with `\n`, `.strip()` the whole, then `sha256:` + first 12 hex. (This is exactly
  `spec_fingerprint` in `framework/bin/sde`.) **It is NOT `shasum spec.lock.md`** — the derived
  blocks are excluded so regenerating Coverage never invalidates trust. Logs key this field as
  `spec_fp`; earlier prose called it `spec_lock` — same thing.
- **Quick hand-check (hash-free, weaker but usually enough):** confirm (a) `trust.log` and `runs.log`
  carry the **same** `spec_fp` string for the eval, (b) `diff spec.md spec.lock.md` is empty, and
  (c) each required eval has a latest `killed`+`passed` pair. This won't catch an intent edit that was
  never re-fingerprinted; the strict recompute above is authoritative.

## 4 — After you act (keep the next resume honest)
1. Write results to disk **immediately** (append-only logs; in-place edits only to `spec.md` /
   `tasks.md`). 2. `git add -A && git commit` (each meaningful step = one commit → torn writes
   recover via `git checkout`). 3. Tier 1: refresh `.sde/handoff.md` (it re-stamps `derived_from`).
   Now a fresh agent re-running §0–§2 continues seamlessly.

---
*The chat is a cache. The repo is the memory. If you remember nothing, this file plus the disk is
enough.*
