# 00 — Problem, Prior Art, and the Thesis for Going Deeper

> **Reading order:** This is doc #0 of the design trail. It states the problem, honestly
> assesses the prior `../sdd/` v0.1 framework (treated as reference, not foundation), and
> commits to a thesis for what *this* framework must do better. Everything downstream
> (advisor passes, peer variants, architecture, build) is judged against the criteria here.
>
> **Author:** Claude Opus 4.8 (1M), max effort. **Date:** 2026-05-30.

---

## 1. The objective, restated sharply

Build a **Spec-Driven Development (SDD) framework**, usable inside Claude Code, that lets an
AI agent (or a cohort of them) build **full-stack and mobile** software, where:

1. **Evals are the first-class citizen**, integrated into the build loop — *not* a separate
   QA phase, *not* an afterthought. Considered early, prioritized, woven in.
2. **The framework survives the AI's limited context window.** Work hands off cleanly to a
   *fresh* session before context rot degrades quality — **autonomously**, before the rot
   happens, not after it has already corrupted decisions.
3. **The task list is preserved on disk** as the work progresses, so *any* fresh agent can
   pick up exactly where the last one stopped.
4. **The whole thing is the seed of a self-running software factory**: objective → specs →
   evals → code → confirmed-by-evals, looping with bounded autonomy.

The user's framing of *why evals matter now* is the load-bearing insight, and I will quote it
because it sets the bar:

> "We have come to the moment that an AI model can generate coding flawlessly but still need
> Evals to confirm that it follows specs and intention given."

Read that precisely. The claim is **not** "AI writes buggy code, so we need tests." The claim
is "**code generation is solved enough; intent-conformance is not.**" The bottleneck has moved
from *can it produce working code?* to *did it build the thing we actually meant?* That is a
different and harder problem than testing, and it is the problem this framework must center.

---

## 2. Success criteria (how we'll know this is better, not just different)

A future reader — human or agent — should be able to check these:

- **SC-1 (Intent conformance):** There is an explicit, enforced mechanism that catches the case
  where *the code runs, the tests are green, but the intent is violated.* Not asserted —
  demonstrated on a real example.
- **SC-2 (Eval trustworthiness):** The framework has an answer to *"who evals the evals?"* —
  it can distinguish a *trustworthy* eval from a *vacuous* one, structurally.
- **SC-3 (Resumability):** A fresh agent, given **only the repo** (zero chat history), can
  state the objective, the current eval status, and the exact next action — and continue.
  This is itself written as an eval and must pass.
- **SC-4 (Adoptability):** A solo developer can start using it in minutes for one feature,
  without installing a bespoke runtime — and the *same* framework scales up to autonomous
  factory mode. Rigor is progressive, not all-or-nothing.
- **SC-5 (Proven, not asserted):** The core loop is exercised end-to-end on a concrete
  full-stack slice, including a mobile-shaped eval, with an eval *catching a deliberately
  planted intent violation*. Dogfooding: the framework builds itself under its own discipline.
- **SC-6 (Full-stack + mobile reach):** The eval model is runner-agnostic and demonstrably
  covers web, backend/API, and mobile journeys.

---

## 3. Honest assessment of the prior art (`../sdd/` v0.1)

The v0.1 framework next door is **genuinely strong**. I am not going to pretend otherwise to
justify a rebuild. What it gets right, I will keep (as ideas, re-derived cleanly):

**Strengths worth inheriting (by idea, with credit):**
- **State on disk; sessions are ephemeral.** The repo is the memory. (Load-bearing, correct.)
- **Fresh-context subagents per phase**, mechanical dispatcher vs. creative agents split.
- **Default-FAIL**: evals start failing; flipping to PASS requires real evidence.
- **Anti-collusion judge**: fresh context, no write tools, *different model* than the builder.
- **Layered handoff**: multiple triggers so state is always resumable.
- **Runner-agnostic eval tiers** (unit / contract / journey / ux / semantic / regression).
- **Bounded autonomy**: wall-clock + retry caps, escalation, kill-switch, steer file.

**Where it falls short — the openings this version must exploit:**

- **G-1 — Eval *validity* is unaddressed (the big one).** v0.1 binds every assertion to an
  eval and gates on it. But it never asks the decisive question: *do these evals, when all
  green, actually mean the intent is met?* An eval can be **vacuous** (passes regardless), or
  the implementation can **game** it, or the eval can **miss** an aspect of intent entirely.
  v0.1's "default-FAIL skeleton" proves an eval *can* fail before it's implemented — but not
  that it fails *for the right reason*, nor that the eval set *covers* the intent. The gap
  between "evals pass" and "intent satisfied" is exactly the user's stated problem, and v0.1
  leaves it open. **This is where we go deepest.**

- **G-2 — Heavy, all-or-nothing ceremony.** 12 skills, 6 subagents, 5 hooks, a bespoke Python
  CLI (with, by its own admission, *no automated tests*), hash-canonicalization, three-layer
  default-FAIL, model-policy files. That is a lot of surface to adopt and to trust. For the
  headline use case — a developer in Claude Code shipping a feature — it risks being too
  bureaucratic to actually use. There is no lightweight on-ramp.

- **G-3 — Asserted, not proven.** Its own `KNOWN-ISSUES.md` admits: CLI only smoke-tested,
  runner *parsers not implemented*, Maestro/Detox adapters are skeletons, examples minimal,
  token caps are a placeholder. The framework is "design-complete," but the central promise —
  *evals catch intent violations* — is never demonstrated end-to-end. A stronger effort must
  **show the dog eating the food.**

- **G-4 — "Autonomous before context rot" is mostly *reactive*.** The handoff triggers fire at
  task boundaries or when the session stops. There's no notion of *sizing work to the context
  budget up front*, nor a clean account of *when* rot begins and how to checkpoint ahead of it.
  The mechanism is good; the *policy* for pre-emption is thin.

- **G-5 — The bespoke CLI is a liability as much as an asset.** A deterministic dispatcher is
  the right instinct, but a hand-rolled, untested Python state machine that every project must
  install is fragile and hard to trust. We should get the determinism with far less bespoke
  code — ideally with the filesystem layout + plain conventions *being* the state machine.

---

## 4. The thesis: three pillars that define this version

### Pillar 1 — **Eval validity is the product.** (Addresses G-1, SC-1, SC-2)

The central, novel contribution. We treat an eval as *untrusted by default* and define
**eval trust** structurally:

> **An eval is trusted only when it is both `GREEN-on-right` and `RED-on-wrong`.**
> It must pass on the intended implementation **and** be demonstrated to *fail* on a
> deliberately broken variant (a "mutant") that violates the intent it guards.

This is mutation testing turned on the evals themselves. A vacuous eval (`expect(true)`) is
GREEN-on-right but also GREEN-on-wrong → **untrusted, rejected.** Every eval ships with its
*kill record*: the mutant it was shown to catch. This is concrete, checkable, and directly
answers "who evals the evals?"

On top of that, two coverage mechanisms:
- **Coverage matrix:** every intent statement maps to ≥1 eval; uncovered intent is a hard flag.
- **Intent audit (adversarial):** an independent fresh-context agent reads *only* the intent +
  the eval set and answers: *"Describe an implementation that passes every one of these evals
  yet betrays the intent."* If it can, that's a coverage/validity hole → new eval required.
  This is the anti-collusion judge repurposed from "grade the code" to "attack the eval set."

### Pillar 2 — **Progressive rigor: one framework, three tiers.** (Addresses G-2, G-5, SC-4)

The same artifacts, adoptable in layers. No bespoke runtime required to start.
- **Tier 0 — Discipline (minutes to adopt):** plain Markdown/YAML files for spec, evals,
  coverage, task list, and handoff; evals run with whatever the project already uses; the
  *filesystem layout is the state machine*. Pure convention. No CLI, no hooks.
- **Tier 1 — Gated:** add the eval-as-gate rule + eval-trust (GREEN/RED) + coverage/intent
  audit. Enforced by slash-command skills (and, optionally, a thin hook).
- **Tier 2 — Factory:** add bounded autonomous orchestration, multi-session/multi-agent fan-out,
  caps + escalation + kill-switch.

Determinism comes from **explicit on-disk state + small idempotent skills**, not a monolithic
CLI. Anyone can read the state by `cat`-ing files.

### Pillar 3 — **Proof by dogfooding.** (Addresses G-3, SC-3, SC-5)

The framework is built *using itself*. It has its own objective, spec, evals, coverage matrix,
task list, and handoff docs in-repo. Two proofs are mandatory deliverables, not stretch goals:
1. **The intent-violation catch:** drive one real full-stack slice; plant a mutation that
   keeps tests green but violates intent; show an eval (likely a semantic/journey eval) catch it.
2. **The resumability eval:** spawn a fresh agent with access to *only* the repo; it must
   correctly report objective + next action + eval status. Encoded as `SC-3` and run for real.

---

## 5. The recursion that makes this honest

This framework's purpose is to seed a factory that turns *objectives* into *eval-confirmed
code*. The very first object that factory processes is **the framework itself.** If the
discipline cannot carry its own multi-session construction across context windows, it will not
carry an app's. So I will deliberately operate this build as the framework prescribes:
externalize state to disk immediately, keep an on-disk task list current, write a handoff after
each checkpoint. My own context window is just a cache; the repo is the truth. If this session
rots or ends, a fresh one continues from `docs/` + the task list + the handoff. That property is
not decoration — it is the thesis under test.

---

## 6. What I'm deliberately *not* deciding yet (hand to advisor + peers)

These are the live forks I will *not* resolve by fiat. They go to the advisor (to pressure-test
my read) and to parallel peer agents (to explore variants), per the user's explicit request to
brainstorm "multiple times, with variants, so all things are considered":

- **Q-A (spec↔eval relationship):** Is the eval *derived from* a prose spec (A: spec-primary),
  the eval *is* the spec (B: eval-primary/TDD-extended), or co-equal bidirectionally-bound with
  a validity layer (C)? I lean C, but it must survive challenge.
- **Q-B (eval-validity mechanism):** Is GREEN-on-right ∧ RED-on-wrong the right trust
  definition? How do we make "produce a mutant" cheap and not a burden? Where does it break
  (flaky evals, expensive journeys, mobile)? Is the adversarial intent-audit worth its cost?
- **Q-C (context handoff / pre-emption):** What is the *trigger policy* for handing off
  **before** rot — task-size budgeting, a context-fraction heuristic, an always-fresh handoff,
  or an external per-task orchestrator? What is the minimal durable state for a clean resume?
- **Q-D (factory autonomy):** What is the smallest control loop that is genuinely safe to run
  unattended, and what are its hard stops? How do multiple agents coordinate without collusion?
- **Q-E (how much machinery):** How far can Tier 0 go on pure convention before a thin runtime
  earns its keep? Where exactly is the line between "convention" and "code"?

---

## 7. Process for the rest of this trail

1. **Advisor pass #1** — pressure-test §3 (prior-art read) and §4 (the three pillars) before I
   commit. (`docs/reasoning/01-advisor-pass-1.md`.)
2. **Peer variant fan-out** — independent agents explore Q-A…Q-E with divergent lenses;
   synthesized in `02-variants.md` / `02a-*`.
3. **Decision + lock** — converge to an architecture; ADRs in `docs/decisions/`.
4. **Build** — Tier 0→2 artifacts, evals-first, dogfooded.
5. **Prove** — the two mandatory proofs (§4 Pillar 3).
6. **Advisor pass #2 + honest status** — what works, what's a known limitation.

The bar is not "a framework exists." The bar is **SC-1…SC-6, demonstrated.**
