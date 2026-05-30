# 02 — Peer Round 1: Synthesis and Locked Decisions

> Three peer agents explored the Tier 0/1 core in parallel, each a fresh context with a distinct
> lens. This doc synthesizes them into **locked decisions** the build must conform to. Where a
> peer's idea is adopted, it's credited inline. Date: 2026-05-30.

## Method

| Peer | Lens | Core output |
|---|---|---|
| P1 | Eval validity (the centerpiece) | The trust protocol, anti-collusion via information barrier, the trust ledger |
| P2 | Minimal on-disk state machine | PRIMITIVE/DERIVED spine, the resume=derivation "ladder", corruption guards |
| P3 | Proof + environment recon | A **verified** runnable proof; honest mobile recon; real fresh-agent resumability |

All three were told: Tier 0 must work with **plain files + the project's existing runner, no
bespoke runtime**; the reference `../sdd/` is prior art to critique, not copy.

---

## Locked decisions

These are binding. A later design that violates one is wrong by construction.

- **D-1 — Spec format is settled; do not reinvent it.** Numbered **intent statements** (prose),
  each **bound to ≥1 eval**, plus a **coverage** check. The novelty is the validity layer on the
  evals, *not* a new spec language. (Q-A resolved.)
- **D-2 — Eval trust = `GREEN-on-right ∧ RED-on-wrong`.** An eval is *trusted* only when it passes
  on the intended implementation **and** is demonstrated to FAIL on a *plausible, intent-violating
  mutant*. The reference's "default-FAIL skeleton" is insufficient: it only proves an eval fails
  when code is **absent**, which every non-vacuous eval does. RED-on-wrong must prove
  **specificity** to the guarded intent. (P1.)
- **D-3 — Mutant anti-collusion = information barrier.** The agent that authors an eval must NOT
  author the mutant that validates it. The mutant author sees **intent + code, never the eval**.
  Gold-standard kill-record: a *surgical* mutant that violates one intent facet while **passing all
  other evals**. (P1; closes advisor hole #1.)
- **D-4 — State is PRIMITIVE vs DERIVED.** Every fact is either *primitive* (authored once /
  append-only, never recomputed) or *derived* (a pure function of primitives, computed at read
  time, never stored as truth). Phase, coverage, eval-trust, next-action, and the handoff dossier
  are all **derived**. This makes "next action is a pure function of disk" literally true and
  dissolves dual-source-of-truth bugs. (P2.)
- **D-5 — Resume protocol *is* the state-derivation procedure** (one "ladder" walk), so they can
  never diverge. (P2.)
- **D-6 — Trust is cached, invalidated by hash/diff-drift (`stale`).** Trust is verified once and
  re-derived only when the eval file or the code-under-test changes. This is the single mechanism
  that makes expensive / flaky / journey / mobile evals affordable. (P1.)
- **D-7 — "No bespoke CLI" ≠ "no shell tools."** Stock `git / grep / diff / cat / shasum` are the
  substrate. A monolithic untested `sdd` dispatcher (the reference's liability) is what we avoid.
  Optional thin, *tested*, stdlib-only helpers are allowed at Tier 1. (P2 + advisor.)
- **D-8 — Mobile is demonstrated honestly via the runner-adapter contract.** We claim only what
  ran. Emulator-boot is reported as a capability, not as a journey-eval run. (P3; advisor hole #4.)
- **D-9 — Proof before framework.** The intent-violation catch and the resumability check are
  *verified deliverables*, built before the framework is wrapped around them. (Advisor.)

---

## Q-B in full: the eval-trust protocol (the centerpiece)

### Trust definition
```
trusted(E)  ⇔  green_on_right(E)  ∧  red_on_wrong(E)
green_on_right(E) ⇔ E passes (N-of-N, default 3) on the intended code
red_on_wrong(E)   ⇔ E fails (N-of-N) on a plausible intent-violating mutant M,
                    where M was authored WITHOUT sight of E (information barrier)
```
A vacuous eval (`expect(true)`) is green-on-right but also green-on-wrong → **untrusted, rejected.**

### Bounded, terminating mutant protocol (Tier 0 = git + existing runner)
```
authorMutantTrust(eval E for intent-facet F, code C):
  spawn mutant-author subagent with context = {F (prose), C}   # NOT E  ← the barrier
  for k in 1..K (default 3):
     m_k = subagent proposes a code diff that violates F
     git apply m_k ; run FULL eval suite ; git checkout -- .    # idempotent, no residue
     if E went RED and all OTHER evals stayed GREEN:            # surgical = gold
        record kill-record(E, m_k, output); E.trust = trusted; RETURN
     if E went RED but others also RED: keep as weak fallback
  if a weak fallback exists: trusted (flagged "broad mutant only")
  else:                      untrusted  # eval did NOT pin a real intent-violation → coverage hole
```
Termination is structural (K bounded attempts, each yielding a concrete diff + suite run) with a
per-eval wall-clock/token backstop → `untrusted: timeout`.

### Intent-audit (coverage validity) — bounded
An independent auditor sees **only intent + the eval set** (never the code) and each round must
**exhibit a concrete betrayer**: an implementation sketch that passes every eval yet violates a
named intent facet.
- **SATISFIED** = 2 consecutive rounds produce no betrayer (absorbs model variance).
- **HOLE** = any round exhibits a betrayer → emit a required new-eval task naming the facet.
- **Hard cap** = 3 rounds; otherwise `audit: inconclusive` → human. Never spins.

### Hard cases → mitigations (P1)
| Case | Mitigation |
|---|---|
| Flaky eval | Trust requires N-of-N on both sides; any non-determinism ⇒ `untrusted: flaky`, must deflake/quarantine. Flakiness is a trust *failure*. |
| Expensive E2E / journey | Verify trust once; cache; mark `stale` on drift (don't re-mutate per commit). Mutate at the cheapest layer that still violates the facet. |
| Mobile | Same stale-caching; prefer **fixture/data mutants** (feed the screen a bad payload) over rebuilding the app. |
| LLM-as-judge / semantic | Mutant = a curated **bad-output fixture**. RED-on-wrong = judge FAILs the known-bad output; GREEN-on-right = judge PASSes the known-good. Each judge eval becomes a golden-pair meta-eval. Pin model + rubric hash. |
| Mutant awkward (idempotency, "no secret in logs", config) | Fixture/env mutant; or `mutant: manual` (prose violation + eval output, lower-assurance, flagged). **Never `mutant: none` on a `required` gate.** |
| Tautological ("file exists") | `gate: advisory` only; excluded from the trust requirement (it doesn't claim to guard intent). |

### Evidence kinds — mutation is the floor, stronger evidence upgrades it (P1)
Record `kill_record.kind`. Mutation-trust always applies (cheap, no oracle). Upgrade where earned:
- **property-based** — when intent is a universal ("always sorted", "balance never negative").
- **metamorphic** — when there's no oracle, only relations (`2× users ⇒ ≤2× cost`); the fix for semantic/ML intent.
- **golden dataset / differential** — when a labeled corpus or a trusted reference implementation exists.

### The eval-trust ledger (on disk, plain, derived-trust)
`evals/trust-ledger.yaml` (or the append-only `trust.log` form from P2). Trust state ∈
`{trusted, untrusted, stale}` is **derived**, never hand-set. Schema and a filled example live in
the framework templates; the load-bearing fields are: `intent`, `eval_file`, `eval_hash`,
`code_paths`, `green_on_right{runs,of}`, `kill_record{mutant,kind,red_on_wrong,others_stayed_green,barrier}`,
`last_verified{commit}`, `trust`.

---

## The state machine: PRIMITIVE/DERIVED + the ladder (P2)

### Layout (one objective, N slices) — Tier 0, pure convention
```
.sdd/
├─ objective.md          # PRIMITIVE  north star + "done when" criteria
├─ decisions.md          # PRIMITIVE  append-only ADR log
├─ RESUME.md             # PRIMITIVE  the ladder checklist (static; agents run it)
├─ runs.log              # PRIMITIVE  append-only eval-run results (all slices, JSON-per-line)
└─ slices/<id>/
   ├─ spec.md            # PRIMITIVE  numbered intents + inline eval bindings + (derived) coverage
   ├─ spec.lock.md       # PRIMITIVE  frozen copy; drift = `diff spec.md spec.lock.md` non-empty
   ├─ tasks.md           # PRIMITIVE  task table (id, targets-eval, deps, status, owner@ts)
   ├─ trust.log          # PRIMITIVE  append-only eval-trust events
   └─ evals/             # PRIMITIVE  runner files + per-eval mutant diffs
```
Dropped from the reference: the `sdd` CLI, `manifest.yaml` (dual-SSOT), any stored `next_action`,
`policy.yaml`, hook scripts, `state/` sentinels, model-diversity config. Added: `spec.lock.md`
(runtime-free drift), `trust.log` + `mutant=` bindings, **per-slice derived phase** (the
reference's single global phase is a latent bug the moment slices run in parallel).

### The ladder — resume AND derivation are one walk
Per slice, evaluate top-down; the **first failing guard is the current phase**, and its action is
the next action. All guards are pure disk reads (`grep`/`diff`/`cat`).

| Rung | Phase | Guard (pure, disk-only) | Next action if unsatisfied |
|---|---|---|---|
| 0 | spec | `spec.md` has ≥1 `^I` intent line | author spec |
| 1 | bind | every intent has ≥1 `eval:` binding | bind evals to uncovered intents |
| 2 | trust | every required eval has latest `trust.log` = mutant-killed **and** real-passed at current `eval_hash` | author/repair mutant or eval |
| 3 | freeze | `spec.lock.md` exists **and** `diff spec.md spec.lock.md` empty | freeze (`cp spec.md spec.lock.md`) |
| 4 | execute | every ready task (deps done) is `done` | run next ready task |
| 5 | evalrun | latest `runs.log` verdict per required eval = PASS at current lock | run suite / fix failing eval's task |
| 6 | done | rung 5 satisfied & no drift | slice complete |
| — | blocked | `diff` non-empty after freeze | re-freeze + re-derive trust (deliberate) |

**Objective next-action = f(disk):** for each slice (lexical order) compute its rung; pick the
first slice not `done`/`blocked` with a ready action; that rung's action is the global next action.

### Corruption guards (P2)
- **C1 stale/lying handoff** → handoff is **derived & fingerprinted** (`derived_from: <git HEAD>`).
  Resume ignores it if the fingerprint ≠ current HEAD and re-derives from primitives. A handoff is
  a *hint*, never truth.
- **C2 partial write** → all mutable state is **append-only JSON-lines**; readers **skip malformed
  lines** (a torn final line is ignored). In-place files (`spec.md`, `tasks.md`) are git-committed
  each step → recover via `git checkout`.
- **C3 task/eval divergence** → **derive "done", never believe the label.** A task counts as done
  only when its row says `done` **and** `runs.log` shows PASS for its target evals at the current
  lock **and** those evals are `trusted`. A hand-set "done" or "trusted: true" can't lie because
  there is no such authoritative field — both are derived.

---

## The verified proof (P3) — SC-1, SC-2, SC-3 demonstrated

`proof/` (runnable: `bash proof/run_proof.sh`, python3 stdlib only). **Re-run and verified by me:**
```
unit×correct=PASS  unit×mutant=PASS  eval×correct=PASS  eval×mutant=FAIL
```
- **Slice:** one pure pagination module. **Intent:** every item present for the whole paging
  session is returned exactly once, stable under a concurrent insert before the cursor.
- **Correct:** keyset cursor on `(created_at, id)`. **Mutant:** naive `ORDER BY created_at
  LIMIT/OFFSET` — the *obvious* first implementation, not a contrived one-char bug.
- **Unit test:** static fixture → **green on both** (this is the "tests pass" trap).
- **Contract eval:** the invariant over a realistic session with a concurrent insert → mutant id
  stream `[1,2,3,3,4,5,6]` ⇒ `duplicated_ids:[3]` → **RED on mutant, GREEN on right.**
- ⇒ **SC-1** (eval catches intent violation that unit tests miss) and **SC-2** (the eval's
  RED-on-mutant *is* its kill record → trusted, non-vacuous) in one artifact.
- **SC-3 (resumability):** P3 ran a *real cold* `claude -p` agent (tools: Read, Bash; prompt
  forcing "read only these files") which independently recovered objective + EVAL STATUS=GREEN
  (by re-running the eval) + the correct next action. Plus a deterministic `resume.py` gate that
  recomputes status live. Both agree.

**Honesty note (P3's own):** the first mutant variant (missing tiebreaker) did *not* diverge —
SQLite's stable sort masked it — so the eval wrongly passed on it. P3 diagnosed this and switched
to the deterministic concurrent-insert scenario. We frame the mutant as "naive OFFSET paging,"
not a tiebreaker bug. This is exactly the kind of self-correction the trust protocol is meant to force.

## Mobile, honestly (P3 + D-8)
Three explicit layers, claiming only what ran:
1. **Substrate (proven):** headless Android emulator boots here (~23s, `boot_completed=1`), real
   screenshot `proof/mobile_screen.png`. Proves *boot capability only*, not a journey.
2. **Adapter contract (the runner-agnostic core):** a journey eval is `flow-spec in → {verdict,
   artifacts} out`. The pagination contract eval is the executable **API instance**; Playwright
   (browsers are cached here) is the documented **web instance**.
3. **Mobile instance (documented, not executed):** a Maestro-style YAML flow as the same contract's
   mobile binding. We install no runner and build no APK, so we claim no mobile journey run.

---

## Open for Round 2 (deferred, per the sequencing inversion)
- **Q-C — handoff pre-emption policy:** what *triggers* a handoff **before** rot (context-fraction
  heuristic? task-size budgeting? always-fresh dossier? external per-task orchestrator?).
- **Q-D — factory autonomy:** the smallest control loop safe to run unattended; hard stops; how
  multiple agents coordinate without collusion.
- **Q-E — the Tier line:** how far pure convention (Tier 0) goes before a thin helper earns its keep.

These are Tier 2 and do not block a proven, usable Tier 0/1 core.
