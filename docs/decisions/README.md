# Architecture Decision Records

The canonical, dated decision record lives in
[`../reasoning/02-peer-round-1-synthesis.md` → "Locked decisions"](../reasoning/02-peer-round-1-synthesis.md)
(D-1…D-9) and the framework's own [`/.sde/decisions.md`](../../.sde/decisions.md). This page is the
quick index.

| ID | Decision | Where |
|---|---|---|
| D-1 | Spec = numbered intent statements + bound evals + coverage (don't reinvent the spec language) | reasoning/02 |
| D-2 | Eval trust = `GREEN-on-right ∧ RED-on-wrong` (default-FAIL is insufficient — prove *specificity*) | reasoning/02, FRAMEWORK §5 |
| D-3 | Mutant anti-collusion = **information barrier** (mutant author never sees the eval) | reasoning/02, FRAMEWORK §5.2 |
| D-4 | State is **PRIMITIVE vs DERIVED**; phase/coverage/trust/next-action/handoff are all derived | reasoning/02, FRAMEWORK §6 |
| D-5 | Resume protocol **is** the state-derivation procedure (one ladder, can't diverge) | reasoning/02, RESUME.md |
| D-6 | Trust is cached, invalidated by eval/intent drift → `stale` (makes expensive/mobile evals affordable) | reasoning/02, FRAMEWORK §5.5 |
| D-7 | No bespoke CLI; stock `git/grep/diff` + a small **tested** read-only deriver | reasoning/02, framework/bin/sde |
| D-8 | Mobile demonstrated honestly via the runner-adapter contract (claim only what ran) | reasoning/02, KNOWN-LIMITATIONS |
| D-9 | Proof before framework (the intent-violation catch + resumability are verified deliverables) | reasoning/01, examples/01 |
| D-10 | Eval/mutant paths in `spec.md` resolve against the project root (eval code lives in the repo, not in `.sde/`) | .sde/decisions.md |

Round-2 decisions (handoff pre-emption, factory autonomy) are recorded in
[`../reasoning/03-factory-and-handoff.md`](../reasoning/03-factory-and-handoff.md).
