---
name: sde-eval
description: Bind evals to the active slice's intents and establish eval TRUST (GREEN-on-right ∧ RED-on-wrong) using the eval-hidden mutant barrier. The centerpiece of SDE. Use after /sde-spec, before writing implementation code.
allowed-tools: Read, Write, Edit, Bash, Agent
---

# /sde-eval — bind evals and establish trust

`sde` below means `python3 framework/bin/sde` (or `sde` if on PATH). The active slice is the first
non-done slice from `sde next`.

## Goal
Every `gate=required` intent gets an eval that is **trusted**: it passes on the intended code
(GREEN-on-right) **and** is proven to FAIL on a plausible intent-violating mutant (RED-on-wrong).
A vacuous eval is worthless; this skill refuses to mark one trusted.

## Steps
1. **Find the gaps.** `sde trust <slice>` lists each required eval's state. Work on every
   `untrusted`/`stale` one. For an intent with no eval yet, write the eval file (in the project's
   `evals/` or `tests/`) and add a binding line to `spec.md`:
   `    eval: <tier> <path> gate=required mutant=<path-to-diff>`.

2. **GREEN-on-right.** Run the eval against the current (intended) code. It must PASS, N-of-N
   (default 3 runs; any flakiness ⇒ stop and deflake — flakiness is a trust failure). Record the
   eval file hash: `shasum -a 256 <eval-path>` and the spec fingerprint from `sde trust`.

3. **RED-on-wrong — THE INFORMATION BARRIER (load-bearing anti-collusion).** Spawn a mutant-author
   subagent via the Agent tool. Give it ONLY: the **intent statement (prose)** + the **code-under-test
   paths**. **Do NOT show it the eval.** Prompt it to propose a small code diff that *plausibly
   violates that one intent facet* (the kind of bug a competent dev might actually write). Then,
   yourself:
   - `git apply <mutant.diff>` (or `patch`), run the **full** eval suite, `git checkout -- <code>`.
   - **Success (gold):** the target eval goes RED while **all other evals stay GREEN** (surgical →
     the eval is load-bearing and non-redundant). Save the diff as the binding's `mutant=` file.
   - If the eval stays GREEN on a genuine intent-violating mutant → the eval is **vacuous/weak** →
     fix the eval (or sharpen the intent) and retry. Bounded to **K=3** mutant attempts.

4. **Record trust** (only when both hold). Append two lines to `<slice>/trust.log`:
   `{"ts":...,"eval":"<I#.tier>","result":"killed","kind":"mutant","mutant":"<path>","others_stayed_green":true,"barrier":"eval-hidden","eval_hash":"<sha>","spec_fp":"<sha>","by":"<you>"}`
   `{"ts":...,"eval":"<I#.tier>","result":"passed","runs":3,"of":3,"eval_hash":"<sha>","spec_fp":"<sha>","by":"<you>"}`
   (`sde trust <slice>` recomputes `eval_hash`/`spec_fp`; copy those exact values so the events are
   machine-verifiable.)

5. **Confirm.** `sde trust <slice>` shows every required eval `trusted`. If any is `untrusted`,
   that intent has a coverage/validity hole — do not proceed to freeze.

## Hard cases (see FRAMEWORK.md §5.6)
LLM-judge/semantic eval → the "mutant" is a curated **bad-output fixture** the judge must FAIL.
Mobile/expensive → fixture/data mutant; trust is cached and only re-checked on drift. Awkward mutant
→ `mutant=manual` (prose + eval output, flagged lower-assurance) — never `mutant=none` on a required gate.

## Anti-collusion reminder
You are the orchestrator. The subagent that writes the mutant must never see the eval. If you wrote
both the eval and the mutant in the same context, the kill-record is a strawman — start over with a
fresh eval-hidden subagent.
