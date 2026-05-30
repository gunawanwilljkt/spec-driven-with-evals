# 01 — Advisor Pass #1: the sequencing inversion

> Before any building, I put the §00 thesis to the advisor (a stronger reviewer who sees the
> whole transcript). This doc records the challenge and what I changed. Date: 2026-05-30.

## What the advisor affirmed

- **Pillar 1 is the real contribution.** "An eval is trusted only when GREEN-on-right ∧
  RED-on-wrong" + a coverage matrix is the genuine delta over `../sdd/` and the actual answer to
  "who evals the evals?" Keep it central; don't let brainstorming dilute it into something
  fancier. → *Affirmed, not pivoted.*

## The challenge that mattered (and the fix)

> **"Your single biggest risk is reproducing G-3 — the exact sin you indicted the prior art for."**

My original plan ordered *proof* dead last (phase 5 of 6), behind an advisor pass, a 5-axis peer
fan-out, "two rounds of variants," synthesis docs, and ADRs. For a framework whose entire thesis
is *hand off before context rot*, burning the context window on process and dying before the
proof would be self-refuting. My task ordering **contradicted my own §5**.

**Fix adopted — the sequencing inversion:**

1. Round 1 brainstorm locks **only** the Tier 0/1 core (Q-A spec format, Q-B eval validity).
2. Build the **minimum** Tier 0 that can run the two proofs (intent-violation catch + resumability).
3. Get them **green**. Make them durable on disk.
4. *Then* Round 2 (Q-C handoff pre-emption, Q-D factory autonomy) — that's Tier 2 and far less urgent.

This honors the user's "multiple rounds, variants" ask **and** guarantees a proven core survives
on disk even if this very session rots or ends. That survival *is* the thesis under test — so I
demonstrate it by construction, not by luck.

## The five specific holes (and disposition)

| # | Advisor hole | Disposition |
|---|---|---|
| 1 | **Mutant generation needs anti-collusion too.** If the eval-author also writes the validating mutant, you get strawman kill-records. | Adopted as a hard requirement. Peer 1 resolved it with an **information barrier**: mutant author sees intent + code, *not* the eval. (Cheaper & stronger than model-diversity; also the solo-dev story.) See §02. |
| 2 | **Intent-audit needs a stopping rule** or it's an unbounded LLM loop. | Adopted. Peer 1: bounded rounds (≤3) that must each *exhibit a concrete betrayer artifact* or return clean; 2 consecutive empty rounds = SATISFIED; else `inconclusive` → human. |
| 3 | **Scope the proof tiny** — one endpoint/module + one eval + one planted mutant. Don't stand up an app. | Adopted. Peer 3 built exactly this: one pure pagination module, one unit test, one mutant, one catching eval. Verified green/red. |
| 4 | **Verify mobile is even runnable before spending on it.** Don't fake an emulator run. | Adopted. Peer 3 did real recon: the Android emulator *does* boot headless here (~23s) — but "boots" ≠ "a journey eval ran." We report the capability and present mobile via the **runner-adapter contract**, executing only the API/web analogue. No faked run. |
| 5 | **Resolve Q-A plainly and fast** — don't reinvent the spec format; the delta is the validity layer. | Adopted. Q-A locked in §02 as: numbered intent statements + each bound to ≥1 eval + coverage check. No new spec language. |

## Net effect on the plan

Round 1 peers were scoped to the **core only** (eval validity, minimal state machine, proof +
env recon) and instructed to return *concise* briefs to protect my context. The proof was built
and verified **first**. Everything downstream now builds on a demonstrated foundation, not a
promised one.
