# Known Limitations — SDE v0.1

The framework's whole thesis is *evals confirm intent*, so this file holds itself to the same
standard: it states **what is proven, what is designed-but-not-proven, and what is not done** —
honestly, with the commands to check each claim. Read this before relying on SDE.

---

## Proven in this environment (re-run and verify)

| Claim | Evidence | Verify |
|---|---|---|
| An eval catches an intent-violation that unit tests miss (SC-1) | `examples/01-pagination` truth table: unit GREEN on both impls, eval RED on the mutant | `bash examples/01-pagination/run.sh` |
| Eval trust = GREEN-on-right ∧ RED-on-wrong is structural (SC-2) | the mutant *is* the kill record; `sde trust` derives `trusted` only with both | `python3 framework/bin/sde trust 01-pagination --root examples/01-pagination` |
| The state machine is derived (not stored) and correct | a tested read-only deriver computes phase/coverage/trust/next-action from disk | `python3 framework/tests/test_sde.py` (6/6) |
| The framework dogfoods itself; state is resumable from disk (SC-3) | `.sde/` tracks this build; status derives the next action with zero chat history | `python3 framework/bin/sde status --root .` |
| Drift invalidation works | extending `test_sde.py` flipped I2.unit's trust to `stale` until re-established (logged in `.sde/decisions.md`) | edit any trusted eval, re-run `sde trust` |
| Cold-start resumability (SC-3, stronger) | in Round 1, a real `claude -p` given only the proof repo recovered objective + eval status + next action | `proof/resume.py` (deterministic gate); see `docs/reasoning/02` |

## Designed, but NOT behaviorally proven here
- **Tier-2 autonomous factory.** The design is complete and locked (`docs/reasoning/03`, decisions
  D-11..D-17), and the driver `framework/bin/sde-factory.sh` is written and **syntax-valid**
  (`bash -n`). But an **end-to-end unattended run is not demonstrated** in this repo — it needs the
  `claude` CLI, a target project, and the `# RUNNER:` hooks wired to real eval runners. Treat the
  driver as a reference implementation, not a turnkey daemon.
- **The 8 Tier-1 skills** are written as agent operating instructions and are internally consistent
  with the deriver, but they have **not been exercised as installed Claude Code slash commands**
  end-to-end. v0.1.
- **Subagent roles** (eval-author, eval-blind mutant-author, judge, intent-auditor) are specified as
  protocols inside the skills/driver; they are **not shipped as separate agent-definition files**.
  The anti-collusion barrier is currently enforced by orchestrator discipline (+ the worktree pattern
  in the driver), not by packaged agent configs.

## Not done / honest gaps
- **Mobile journey eval is NOT executed.** The Android emulator *does* boot headless here (~23s;
  `proof/mobile_screen.png`), but no app/runner (Maestro/Detox) was built. Mobile is shown via the
  **runner-adapter contract** + a documented Maestro flow (`examples/01-pagination/evals/journey.maestro.yaml`)
  + the executable API analogue (`session.py`). **We claim no mobile journey run** (SC-6 is met by the
  contract + web/API execution, not by a device run).
- **LLM-as-judge / semantic evals are NOT wired to a real model** (no `ANTHROPIC_API_KEY` in this
  sandbox). Shown via the judge **contract** (`examples/01-pagination/judge_sample_verdict.json`,
  labeled "model NOT called"). The gate-blocking evals are deterministic and don't depend on the judge.
- **The bounded intent-audit** is a specified protocol run via a subagent; no automated runner ships.
- **N-of-N trust runs** (default 3) are documented; the deterministic example records the count but the
  helper ran each eval once. For flaky/nondeterministic evals you must actually run N times.
- **No Stop-hook / kill-switch / steer scripts are shipped** as install-ready hooks (the driver reads
  `.sde/STOP` / `.sde/STEER`; a packaged Stop-hook is a documented Tier-1 hardening, not included).
- Assumes a **local POSIX filesystem + git**. `.sde/` on a sync service (Dropbox/iCloud) may corrupt
  under concurrent writes.

## Scorecard against the original goal
| Goal clause | Status |
|---|---|
| Spec-driven framework usable in Claude Code | ✅ Tier 0 (convention) + Tier 1 (skills); proven on a real slice |
| Evals first-class, *alongside* not separate | ✅ trust is a rung *before* freeze/execute; the gate blocks on required evals |
| Confirms code follows **intent**, not just runs | ✅ proven (SC-1/SC-2): mutant green on tests, red on eval |
| Full-stack **+ mobile** | ✅ web/backend executable; ⚠️ mobile via adapter contract + documented flow (not a device run) |
| Autonomous handoff before context rot | ✅ resumable-from-disk proven; pre-emption policy designed (one action/fresh session); ⚠️ unattended driver not run |
| Task list preserved for a fresh agent | ✅ on-disk `tasks.md` + the `.sde/` dogfood literally tracks this build |
| Foundation for a self-running software factory | ✅ designed + driver written (Tier 2); ⚠️ not yet run unattended |

## Path to v0.2 (in priority order)
1. Wire the driver's `# RUNNER:` hooks + run the factory unattended on one small real objective (binds slice 02's behavioral evals).
2. Package the subagent roles as agent-definition files; ship the Stop-hook.
3. Execute one real mobile journey eval (Expo + Maestro) end-to-end on the emulator that boots here.
4. Wire a real different-model judge once an API key is available; add the intent-audit runner.
5. Exercise the 8 skills as installed slash commands; add skill-level tests.
