# 04 — Final Review: Advisor Pass #2 and the Resumability Proof

> The closing arc. The advisor reviewed the finished build and found one gap on the single most
> important claim; closing it converted that claim from *asserted* to *proven on the real artifact*.
> Date: 2026-05-30.

## 1. Advisor pass #2 — the gap that mattered

The advisor affirmed the build (proof-first sequencing held, deriver tested, dogfood derives, honest
limitations) but caught one thing my own checks missed, on my central thesis:

> **SC-3 (resumability) was proven against the *old flat `proof/` layout*, never against the `.sde/`
> + `RESUME.md` ladder that actually ships.** The deterministic deriver had walked it, but no *fresh
> LLM* had ever followed `RESUME.md` by hand and landed on the right next action. Shipping that claim
> unproven would be the same G-3 sin ("asserted, not proven") I indicted the prior art for — on the
> one claim that matters most.

Plus two honesty fixes: the README over-claimed resumability relative to `KNOWN-LIMITATIONS`, and the
example's `trust.log` recorded `barrier: eval-hidden` when that mutant was actually authored *with the
eval in view* during the build (the information barrier was not applied).

## 2. Cold-agent test #1 — deriver forbidden

I spawned a genuinely fresh agent, pointed only at the repo, **forbidden from running `sde`**, forced
to walk `RESUME.md` by hand. Result:

- **Headline PASS.** It independently derived the correct **objective**, **next action**
  (`02-factory-mode / bind`), and **per-slice status** (`01 done`, `02 bind`) — matching the deriver.
- It correctly **detected the stale handoff** (`derived_from ≠ HEAD`) and ignored it — the safety
  mechanism working live.
- **But it found a real defect:** rung 2 (trust) was *not* hand-followable, because `RESUME.md` never
  defined how to compute `spec_fp`. The naive `shasum spec.lock.md` gives the *wrong* value (the real
  fingerprint strips the derived `## Coverage`/`## Intent-audit` blocks). The agent only got the right
  answer by **reading the deriver source** — which a self-sufficient protocol should never require.
  It also flagged `spec_lock` (prose) vs `spec_fp` (logs) naming drift, and that Rule B ("each target
  eval") was stricter than rung 5 ("each *required* eval").

This is exactly the value of testing the real artifact with a real agent: the deterministic deriver
could never have surfaced an *ambiguity in the human-followable protocol*, because it doesn't read it.

## 3. Fixes applied

- **`RESUME.md`** — added a **Fingerprints** section defining `eval_hash` and `spec_fp` by hand
  (including the strip-derived-blocks canonicalization, and a hash-free quick-check fallback);
  unified `spec_lock → spec_fp`; scoped Rule B to `gate=required` targets; sharpened the rung-1 bind
  guard ("0 parseable bindings ⇒ fail"). Propagated to all copies.
- **`trust.log`** (example + dogfood) — `barrier: eval-hidden → not-applied` (honest provenance; the
  barrier is a Tier-2 driver property, not exercised in the hand-built examples).
- **`FRAMEWORK.md`** `spec_lock → spec_fp`; **README** + **KNOWN-LIMITATIONS** aligned to what was shown.

## 4. Cold-agent test #2 — deriver AND its source forbidden (the capstone)

A second fresh agent, this time **forbidden from running the deriver AND from reading its source** —
the strict test of whether `RESUME.md` *alone* suffices. Result:

- **Full PASS, every rung by hand.** Correct objective, next action, and per-slice status again;
  stale handoff again detected and ignored.
- **Rung 2 evaluated entirely from `RESUME.md`.** Using the new Fingerprints recipe with `shasum`, it
  computed `spec_fp = sha256:23e0044093d6` **by hand** and it **matched** the value stamped on every
  `trust.log` event and both `runs.log` verdicts. It even read the *latest* trust epoch correctly —
  catching the live D-6 drift demo (the re-stamped `6a89bd…`, not the superseded `248e…`).
- **One honest residual:** the *strict* `spec_fp` check needs a stream editor (`sed`/`awk`) for the
  canonicalization, beyond bare `cat/grep/diff` — which `RESUME.md` already concedes ("plain
  cat/grep/diff is not enough for the strict check"), offering the hash-free cross-check the agent
  also confirmed. With the SHA-256 tool `RESUME.md` tells you to bring, there is no remaining ambiguity.

## 5. Conclusion

SC-3 — *a fresh agent, given only the repo, resumes correctly* — is now **proven on the shipping
`.sde/` + `RESUME.md` layout**, twice, by real cold agents, the second without even reading the
deriver source. The resume protocol and the deterministic deriver **agree on the real artifact**
(D-5: resume *is* derivation). The thesis the whole framework rests on is no longer asserted; it is
demonstrated — which is the standard this framework exists to enforce.

What remains is in `KNOWN-LIMITATIONS.md` (the Tier-2 factory's behavioral run, a real mobile journey,
a wired judge). None of it touches the proven core. The framework practiced its own discipline on
itself, and an independent agent confirmed the result from disk alone.
