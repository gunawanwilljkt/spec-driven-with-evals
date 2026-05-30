# SDE — Spec-Driven Development, Evals-First

> Build full-stack and mobile software with an AI agent (or a cohort of them), where **evals are
> the first-class citizen** that confirm the code follows the *intent* — not just that it runs.
> State lives on disk so any fresh session resumes cleanly before context rot. The same discipline
> scales from a solo developer to an autonomous software factory.
>
> `Version 0.1` · `2026-05-30` · Canonical reference — **read this first.**
> Design trail with advisor + peer reasoning: [`docs/reasoning/`](docs/reasoning/).

The thesis, in one sentence: **code generation is solved enough; intent-conformance is not — so
the unit of trust is not a passing test, it is a *trustworthy eval*.**

---

## 1. The three pillars (what makes this different)

1. **Eval validity is the product.** An eval is *untrusted by default*. It becomes **trusted** only
   when it is `GREEN-on-right ∧ RED-on-wrong`: it passes on the intended code **and** is shown to
   FAIL on a plausible, intent-violating *mutant*. A test that can't catch a wrong implementation
   isn't a safeguard — it's decoration. This is the structural answer to *"who evals the evals?"*
2. **Progressive rigor — one framework, three tiers.** The same artifacts adopt in layers: Tier 0
   pure convention (minutes to start, no runtime), Tier 1 gated (eval-trust + coverage enforced),
   Tier 2 factory (bounded autonomy). You never install machinery you don't need yet.
3. **Proof by dogfooding.** The framework is built using itself and ships a *runnable* proof that an
   eval catches an intent-violation the unit tests miss ([`examples/01-pagination/`](examples/01-pagination/)),
   plus a *demonstrated* fresh-agent resume from disk alone.

---

## 2. Mental model in 30 seconds

```
OBJECTIVE  (north star, on disk)
  └─► for each SLICE (a thin vertical feature):
        spec     numbered intent statements (what we mean)
          ▼
        bind     each intent ↦ ≥1 eval            (coverage)
          ▼
        trust    each eval proven GREEN-on-right ∧ RED-on-wrong   ← the load-bearing gate
          ▼
        freeze   spec.lock.md = frozen copy (drift detected by `diff`)
          ▼
        execute  implement tasks until the trusted evals pass
          ▼
        evalrun  run the suite; verdicts appended to runs.log
          ▼
        done     all required evals PASS at the frozen spec, no drift
```

Every `▼` is a **pure function of disk state** (a `grep`/`diff`/`cat`), not a value held in the
chat. The chat is a disposable cache; the repo is the memory. A fresh agent reading only the repo
computes the exact same "what's next?". That property is the whole context-rot defense.

---

## 3. Progressive rigor: the three tiers

| Tier | Name | You get | You add | Runtime |
|---|---|---|---|---|
| **0** | Discipline | spec + evals + coverage + tasks + handoff as plain files; evals run with *your* existing runner; the filesystem layout *is* the state machine | nothing — read §4–§8 and `cp` the templates | none |
| **1** | Gated | eval-trust (GREEN∧RED), coverage + intent-audit, the resume ladder, slash-command skills | the `sde-*` skills (a Claude Code plugin) + optional read-only `sde` deriver | git + Python stdlib (helpers are optional & tested) |
| **2** | Factory | bounded autonomous loop, multi-session/multi-agent fan-out, caps + escalation + kill-switch | `/sde-factory` + an external orchestrator (Round-2 design) | git + an outer driver |

Adopt Tier 0 today for one feature; turn on Tier 1 when you want the gate enforced; reach Tier 2
when you want it to run unattended. **No tier rewrites the artifacts of the tier below.**

---

## 4. The spec format (intent statements)

One `spec.md` per slice. Numbered **intent statements** in prose — *what we mean*, not how — each
**bound to ≥1 eval**. A derived coverage block proves nothing is unbound. (We do **not** invent a
spec language; the novelty is the trust layer on the evals, not the prose.)

```markdown
# Slice 01 — Paginated item list
Intent: a client pages the list and sees every item exactly once.
Non-goals: infinite scroll; realtime push.

## Intents
I1. Pages return items in a stable total order.
    eval: contract  evals/I1.order.py      gate=required  mutant=evals/I1.mutant.diff
I2. The union of all pages equals the full set — no omissions, no duplicates.
    eval: contract  evals/I2.coverage.py   gate=required  mutant=evals/I2.mutant.diff
I3. Paging is stable under a concurrent insert before the cursor.
    eval: journey   evals/I3.session.py    gate=required  mutant=evals/I3.mutant.diff
    eval: ux        evals/I3.rubric.md     gate=flag

## Coverage   (DERIVED — regenerate, never hand-edit)
I1 ✓  I2 ✓  I3 ✓   covered = 3/3
```

Greppable contract: intents match `^I[0-9]`, bindings match `^\s+eval:`. Each `gate=required` eval
must name a `mutant=` (its RED-on-wrong evidence) or be explicitly `mutant=manual`.

**Gates:** `required` (FAIL blocks the slice), `flag` (FAIL surfaces, doesn't block), `advisory`
(always allows; for tautological checks that don't claim to guard intent).

---

## 5. Eval trust — the centerpiece

### 5.1 Definition
```
trusted(E) ⇔ green_on_right(E) ∧ red_on_wrong(E)
  green_on_right : E passes (N-of-N, default 3) on the intended code
  red_on_wrong   : E fails (N-of-N) on a plausible intent-violating mutant M,
                   where M was authored WITHOUT sight of E   (the information barrier)
```
A vacuous eval (`assert True`) is green-on-right but green-on-wrong too → **untrusted, rejected.**
The reference framework's "skeleton that fails by default" is *not enough*: it only proves an eval
fails when code is **absent**. Trust requires proving the eval is **specific** to the intent — that
it goes red on a *plausible wrong implementation*.

### 5.2 Anti-collusion: the information barrier
If the eval's author also writes the validating mutant, you get a strawman kill-record. So:

> **The mutant author sees the intent (prose) + the code-under-test, but NOT the eval.**

Forced to attack the *intent blind to the assertion*, the author can't tune a mutant to the check.
Gold-standard kill-record: a **surgical** mutant that violates one intent facet while **passing all
other evals** — proving the eval is both load-bearing and non-redundant. At Tier 1 the mutant author
is a fresh restricted-context subagent (same model is fine; a *different* model is an optional
Tier-2 strengthening). The barrier, not model diversity, is the mechanism.

### 5.3 The bounded mutant protocol (Tier 0 = `git` + your runner)
```
for k in 1..K (default 3):
   M = (barriered) mutant-author proposes a code diff that violates intent facet F
   git apply M ; run the FULL eval suite ; git checkout -- .     # idempotent, no residue
   if E went RED and all OTHER evals stayed GREEN → trusted (surgical); record kill-record; stop
   if E went RED but others also RED → keep as weak fallback
after K: weak fallback ⇒ trusted (flagged "broad"); else ⇒ untrusted  (a coverage hole)
```
Terminating by construction (K bounded attempts, each a concrete diff + run) with a wall-clock
backstop → `untrusted: timeout`.

### 5.4 Coverage validity: the bounded intent-audit
An independent auditor sees **only intent + the eval set** (never the code) and each round must
**exhibit a concrete betrayer** — a sketch that passes every eval yet violates a named facet.
- **SATISFIED** = 2 consecutive rounds find no betrayer.  • **HOLE** = a betrayer ⇒ required new eval.
- Hard cap 3 rounds, else `audit: inconclusive` → human. Never an open loop.

### 5.5 Trust is cached; drift makes it `stale`
Trust is verified **once** and re-derived only when the eval file *or* the code-under-test changes
(hash/`diff` drift). `stale ≠ failing`; it means "re-verify on budget." **This is what makes
expensive / flaky / journey / mobile evals affordable** — you don't re-mutate every commit.

### 5.6 Hard cases (don't pretend they vanish)
| Case | What to do |
|---|---|
| Flaky | Trust needs N-of-N both sides; any nondeterminism ⇒ `untrusted: flaky` → deflake/quarantine. |
| Expensive E2E / journey | Verify once, cache, mark `stale` on drift; mutate at the cheapest layer that still violates the facet. |
| Mobile | Same caching; prefer **fixture/data mutants** (feed a bad payload) over rebuilding the app. |
| LLM-as-judge / semantic | Mutant = a curated **bad-output fixture**; judge must FAIL it and PASS the good one (a golden pair). Pin model + rubric hash. |
| Mutant awkward (idempotency, "no secret in logs") | Fixture/env mutant; or `mutant=manual` (prose + eval output, flagged lower-assurance). Never `mutant=none` on a required gate. |
| Tautological ("file exists") | `gate=advisory` only; excluded from the trust requirement. |

### 5.7 Evidence kinds — mutation is the floor; stronger evidence upgrades it
Record `kind` in the ledger. **mutation** always applies. Upgrade where earned: **property-based**
(universals like "always sorted"), **metamorphic** (no oracle, only relations — the fix for
semantic/ML intent), **golden/differential** (a labeled corpus or trusted reference exists).

### 5.8 The eval-trust ledger
`slices/<id>/trust.log` — append-only, one JSON event per line; trust state is **derived** from the
latest events (never hand-set). See [`framework/templates/trust.log.example`](framework/templates/).
A slice's rung-2 (`trust`) guard passes only when every required eval has both a `mutant:killed` and
a `real:passed` event at the *current* `eval_hash` + `spec_fp` fingerprint.

---

## 6. The on-disk state machine (PRIMITIVE vs DERIVED)

The organizing law: **every fact is either PRIMITIVE (authored once / append-only, never
recomputed) or DERIVED (a pure function of primitives, computed at read time, never stored as
truth).** Phase, coverage, eval-trust, next-action, and the handoff dossier are all *derived*. This
makes "next action is a pure function of disk" literally true and removes every dual-source-of-truth
bug class.

### 6.1 Layout (Tier 0 — pure convention)
```
.sde/
├─ objective.md          # PRIMITIVE  north star + "done when" criteria
├─ decisions.md          # PRIMITIVE  append-only ADR log
├─ RESUME.md             # PRIMITIVE  the ladder checklist (static; agents run it)
├─ runs.log              # PRIMITIVE  append-only eval-run verdicts (all slices, JSON/line)
└─ slices/<id>/
   ├─ spec.md            # PRIMITIVE  intents + eval bindings + (derived) coverage
   ├─ spec.lock.md       # PRIMITIVE  frozen copy; drift = `diff spec.md spec.lock.md` non-empty
   ├─ tasks.md           # PRIMITIVE  task table (id, targets-eval, deps, status, owner@ts)
   ├─ trust.log          # PRIMITIVE  append-only eval-trust events
   └─ evals/             # PRIMITIVE  runner files + per-eval mutant diffs
```
(The framework uses `.sde/`; you may keep app code anywhere in the repo.)

### 6.2 The ladder — resume **is** state-derivation (one walk, so they can't diverge)
Per slice, evaluate top-down; the **first failing guard is the current phase** and its action is the
next action. Every guard is a pure disk read.

| Rung | Phase | Guard (pure) | Next action |
|---|---|---|---|
| 0 | spec | `spec.md` has ≥1 `^I` line | author spec |
| 1 | bind | every intent has ≥1 `eval:` | bind evals to uncovered intents |
| 2 | trust | every required eval: latest `trust.log` = killed ∧ passed @ current hash | author/repair mutant or eval |
| 3 | freeze | `spec.lock.md` exists ∧ `diff spec.md spec.lock.md` empty | freeze (`cp spec.md spec.lock.md`) |
| 4 | execute | every ready task (deps done) is `done` | run next ready task |
| 5 | evalrun | latest `runs.log` per required eval = PASS @ current lock | run suite / fix failing eval's task |
| 6 | done | rung 5 satisfied & no drift | slice complete |
| — | blocked | `diff` non-empty after freeze | deliberate re-freeze + re-derive trust |

**Objective next-action `f(disk)`:** for each slice in `slices/` (lexical order) compute its rung;
pick the first slice not `done`/`blocked` with a ready action; that rung's action is the global next
action. If all slices `done` → check `objective.md` "done when" → finished.

### 6.3 Corruption guards
- **Stale handoff** → the dossier is derived and stamped `derived_from: <git HEAD>`; resume ignores
  it if that ≠ current HEAD and re-derives. A handoff is a *hint*, never truth.
- **Partial write** → mutable state is append-only JSON-lines; readers **skip malformed lines**.
  In-place files are git-committed each step → recover with `git checkout`.
- **Task/eval divergence** → **derive "done", never trust the label.** A task is done only if its
  row says `done` AND `runs.log` shows PASS for its target evals at the current lock AND those evals
  are `trusted`. There is no authoritative `done:true`/`trusted:true` field to lie with.

---

## 7. Eval tiers (runner-agnostic — full-stack + mobile)

SDE is **not** a test runner; it adapts to yours. A journey eval is an adapter satisfying one
contract: **`flow-spec in → {verdict, artifacts} out`.**

| Tier | Checks | Typical runner (web / backend / mobile) | Default gate |
|---|---|---|---|
| unit | pure logic | vitest·jest / pytest / xctest·junit | required |
| contract | API & data-shape | vitest+zod / pytest+pydantic | required |
| journey | end-to-end user flow | playwright / supertest / **maestro·detox·xcuitest** | required |
| ux | visual / interaction vs rubric | judge (LLM-as-judge) | flag |
| semantic | freeform output meets a rubric | judge + golden pair | required iff LLM output |
| regression | golden-set pass-rate stable | differential / golden runner | required |

Mobile is **stack-agnostic**: provide a flow spec and a runner adapter; the trust protocol uses
fixture/data mutants so you needn't rebuild the app per check. See
[`examples/01-pagination/evals/journey.maestro.yaml`](examples/01-pagination/) for the documented
mobile binding of the same contract whose API instance actually runs.

---

## 8. Handoff & resumability

After every meaningful step, state is already on disk (that's the point of §6). The **handoff
dossier** is a *derived* convenience: a ≤120-line `cat` of "where we are + the single next action",
stamped with the git HEAD it was derived from. A fresh session:

1. reads `objective.md`; 2. lists `slices/`; 3. walks the ladder (§6.2) per slice; 4. computes the
global next action; 5. acts. It may read the dossier as a hint but **trusts the derivation** if the
fingerprint is stale. This is demonstrated for real (`examples/01-pagination`, a cold `claude -p`
agent recovered objective + eval-status + next-action from disk alone).

---

## 9. Slash commands (the Tier 1 plugin)

Lean by design — eight verbs, each load-bearing (the reference's twelve collapsed). All share the
ladder.

| Command | Does |
|---|---|
| `/sde-init <objective>` | scaffold `.sde/`, write `objective.md`, `RESUME.md`, empty logs |
| `/sde-spec` | author/refine `spec.md` intents for the active slice |
| `/sde-eval` | bind evals + run the trust protocol (barriered mutant) + append `trust.log` |
| `/sde-next` | run the ladder; do (or dispatch) the single next action |
| `/sde-verify` | run the suite → append `runs.log`; run the bounded intent-audit; the gate |
| `/sde-handoff` | materialize the derived dossier (fingerprinted) |
| `/sde-resume` | fresh-session entry: walk the ladder, print state, continue |
| `/sde-status` | print derived state (phase, coverage, trust, next action) |

`/sde-factory` (Tier 2, Round-2 design) wraps `/sde-next` in a bounded loop. Skill bodies live in
[`framework/skills/`](framework/skills/).

---

## 10. What SDE is / is NOT
- **Is:** a discipline + an on-disk state machine + an eval-trust protocol, operable by an AI agent
  across fresh sessions.
- **Is NOT:** a test runner (bring your own), a project tracker (use Issues for roadmaps), or magic.
  A vague intent yields vague evals yields vague code. The intent-audit *surfaces* that; it can't
  fix it for you.

---

## 11. Quick start

**Tier 0 (no install):**
```bash
cp -r framework/templates/.sde ./.sde         # scaffold
# edit .sde/objective.md, then .sde/slices/01-*/spec.md (intents),
# write evals + a mutant diff per required intent, run them with your runner,
# append trust.log when an eval is GREEN-on-right ∧ RED-on-wrong. Follow .sde/RESUME.md.
```
**Tier 1 (plugin):** install `framework/skills/` into Claude Code, then:
```
/sde-init "Page through the item list, every item exactly once"
/sde-spec → /sde-eval → /sde-next → /sde-verify        # each may run in a fresh session
/sde-resume                                            # after any context reset
```
See the runnable proof: `bash examples/01-pagination/run.sh`.
