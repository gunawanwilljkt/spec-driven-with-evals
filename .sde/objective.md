# Objective: Build the SDE framework (evals-first SDD for Claude Code)

North star: a framework an AI agent uses inside Claude Code to build full-stack and mobile software
where EVALS are first-class — they confirm the code follows the *intent*, not just that it runs —
state survives the context window via clean handoff, the task list is preserved on disk for any
fresh agent, and the same discipline scales to a self-running software factory.

Done when (the success criteria, SC-1..SC-6 from docs/reasoning/00):
- SC-1: an enforced mechanism catches "code runs, tests green, intent violated" — demonstrated.
- SC-2: trustworthy evals are structurally distinguished from vacuous ones (GREEN∧RED).
- SC-3: a fresh agent resumes from the repo alone (objective + next action + eval status).
- SC-4: adoptable in minutes (Tier 0, no runtime) and scales to autonomous factory (Tier 2).
- SC-5: proven, not asserted — the core loop runs end-to-end on a real slice, eval catches a mutant.
- SC-6: runner-agnostic across web / backend / mobile.

Slices:
- 01-tier0-core   — the eval-trust protocol + resumable state machine + the proof. (the foundation)
- 02-factory-mode — Tier-2 bounded autonomous orchestration. (the factory the foundation enables)

<!-- This .sde/ is the framework dogfooding itself. If you are a fresh agent, run .sde/RESUME.md (or
     `python3 framework/bin/sde status --root .`) and continue from the derived next action. -->
