---
name: sde-spec
description: Author or refine the active slice's numbered intent statements (what we mean, not how). Each intent will bind at least one eval next.
allowed-tools: Read, Write, Edit, AskUserQuestion
---

# /sde-spec

1. Open the active slice's `spec.md` (the slice from `sde next`).
2. Write numbered **intent statements** (I1, I2, …): each a single, checkable statement of *intent*
   — the behavior we mean, not the implementation. State **Non-goals** explicitly (so the
   intent-audit doesn't flag deliberately-absent things as holes).
3. Resolve ambiguity with **AskUserQuestion** before committing. A vague intent yields a vague eval
   yields vague code — do not guess load-bearing behavior (auth rules, money handling, ordering,
   idempotency, privacy). The intent-audit will surface vagueness later, but it's cheaper to ask now.
4. Keep intents **thin**: each should be coverable by an eval that fits one context window. If an
   intent needs a sprawling eval, split it.
5. Leave eval bindings to `/sde-eval` (the next rung). Do **not** freeze yet. Commit. Next: `/sde-eval`.
