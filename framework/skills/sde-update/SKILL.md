---
name: sde-update
description: Update the vendored SDE framework (framework/ — the deriver, templates, skills — plus FRAMEWORK.md and the installed /sde-* slash commands) to the latest version from its public GitHub repo. It checks the current vs latest version first and only updates if newer. Your project STATE in .sde/ (objective, slices, specs, trust/run logs, handoff) is preserved — never overwritten. Use to pull framework bug-fixes and new skills.
allowed-tools: Bash, Read, AskUserQuestion
---

# /sde-update — update the SDE framework from GitHub (state-preserving)

Pulls the latest **framework code** from its source repo. It updates the *tooling*, not your *work*:
your project state in `.sde/` (`objective.md`, `decisions.md`, `runs.log`, `handoff.md`, `slices/`) is
**never touched** — only `.sde/RESUME.md` (the protocol doc, a framework artifact) is refreshed.

Run from the **project root** (the dir containing `framework/` and `.sde/`).

## Steps
1. **Check versions** (read-only, no changes):
   ```bash
   bash framework/bin/sde-update.sh --check
   ```
   It prints `current: X    latest: Y    source: owner/repo@branch` and exits:
   **0** = up-to-date · **2** = update available · **1** = error (offline, or the repo has no
   `framework/VERSION`).
2. **Up-to-date (exit 0)** → report "already on the latest (vX)"; stop. Nothing else to do.
3. **Error (exit 1)** → report what it printed (likely offline, or the source repo hasn't published a
   `framework/VERSION` yet). Do not change anything.
4. **Update available (exit 2)** → tell the user `current → latest` and that applying will replace the
   framework artifacts + re-install the `/sde-*` skills + refresh `RESUME.md`, while preserving all
   `.sde/` project state. Ask to proceed (**AskUserQuestion**).
5. **Apply** (only after the user confirms; commit any pending work first so you can roll back):
   ```bash
   git add -A && git commit -m "wip before sde-update" 2>/dev/null
   bash framework/bin/sde-update.sh
   ```
   The script fetches the repo tarball, replaces **only** framework artifacts, re-installs skills,
   refreshes `RESUME.md`, then runs `framework/tests/test_sde.py` + `sde status` to verify.
6. **Report + commit** the result:
   ```bash
   git add -A && git commit -m "sde: update framework <old> -> <new>"
   git diff --stat HEAD~1            # show the user exactly what changed
   ```
   If the script's post-update checks FAILED, do **not** commit — roll back with
   `git checkout -- framework FRAMEWORK.md .claude .sde/RESUME.md` and report.

## Configuration
- Source repo = `framework/REPO` (default `gunawanwilljkt/spec-driven-with-evals@main`). Override per
  run with `SDE_UPDATE_REPO=owner/repo@branch bash framework/bin/sde-update.sh`.
- Version = `framework/VERSION` (semver `X.Y.Z`). The repo's `framework/VERSION` is the "latest".

## Safety (state the guarantee to the user)
- **Your `.sde/` project state is never overwritten** — only `RESUME.md` (the protocol) is refreshed.
- The update **aborts before touching anything** if the fetched tree isn't a valid framework.
- Always run on a clean/committed tree so a bad update is one `git checkout` away.
