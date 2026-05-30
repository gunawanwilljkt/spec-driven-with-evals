#!/usr/bin/env bash
# sde-factory.sh — the SDE Tier-2 autonomous driver (REFERENCE implementation).
#
# A MECHANICAL loop. It spawns a FRESH, information-scoped `claude -p` per ladder RUNG, keyed off the
# deriver's phase token (`sde next --porcelain`). There is NO LLM creativity in this script —
# creativity lives inside the per-rung agents. The DRIVER (not the agents) runs evals/mutants and
# writes trust.log/runs.log, so a builder can never grade its own work (executor-in-harness, D-14).
# It commits to a branch and NEVER pushes or deploys.
#
# Bounded by: a HEAD-based no-progress retry cap, a MAX_STEPS budget, a .sde/STOP kill-switch, and a
# steer file. Hard stop = block + escalate (never auto-weaken a gate). `sde next` exit-0 ESCALATES for
# human "done-when" review — it never auto-succeeds (D-16).
#
# STATUS: reference implementation. Needs the `claude` CLI, a git repo containing .sde/, and your eval
# runners wired where marked `# RUNNER:`. An end-to-end unattended run is NOT demonstrated in this repo
# (see ../../KNOWN-LIMITATIONS.md). Read docs/reasoning/03-factory-and-handoff.md for the rationale.
set -u

ROOT="."; MAX_STEPS=60; RETRY_CAP=3; BRANCH="sde/factory"; JUDGE_MODEL="${SDE_JUDGE_MODEL:-}"
while [ $# -gt 0 ]; do case "$1" in
  --root) ROOT="$2"; shift 2;;            --max-steps) MAX_STEPS="$2"; shift 2;;
  --retry-cap) RETRY_CAP="$2"; shift 2;;  --branch) BRANCH="$2"; shift 2;;
  --judge-model) JUDGE_MODEL="$2"; shift 2;; *) echo "unknown arg: $1" >&2; exit 64;;
esac; done

HERE="$(cd "$(dirname "$0")" && pwd)"; SDE="python3 $HERE/sde"
ESCALOG="$ROOT/.sde/escalations.log"
git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "sde-factory: $ROOT is not a git repo" >&2; exit 1; }
git -C "$ROOT" checkout -B "$BRANCH" >/dev/null 2>&1 || true   # work on a branch; never push/deploy

escalate(){ echo "$(date -u +%FT%TZ) ESCALATE $*" | tee -a "$ESCALOG" >&2; }
commit(){ git -C "$ROOT" add -A && git -C "$ROOT" commit -q -m "sde: $1" 2>/dev/null || true; }
advance_or_stop(){ escalate "stopping — a slice needs human attention (Tier-2 default = stop; advancing to an independent slice is a documented enhancement)"; exit 5; }
block_slice(){ : > "$ROOT/.sde/slices/$1/.blocked"; escalate "blocked slice $1"; }

# A fresh, scoped agent. Per-rung prompts hand it ONLY what that rung needs (information barrier).
run_agent(){ claude -p "$1" --permission-mode acceptEdits >/dev/null 2>&1; }

# rung 2 — establish trust. The DRIVER runs the green/red protocol; the agent only proposes the mutant,
# and only from an EVAL-BLIND git worktree (it cannot see the assertion it must beat — D-15).
establish_trust(){
  local slice="$1" sdir="$ROOT/.sde/slices/$1" evid wt
  $SDE trust "$slice" --root "$ROOT" | awk '$2!="trusted"{print $1}' | while read -r evid; do
    # GREEN-on-right: the DRIVER runs the eval N times against the current code.
    #   RUNNER: replace with the real command for eval $evid; require PASS (N-of-N).
    # RED-on-wrong via an eval-blind worktree:
    wt="$(mktemp -d)"; git -C "$ROOT" worktree add -q "$wt" HEAD || { rm -rf "$wt"; continue; }
    #   RUNNER: in $wt, delete/obscure the eval files bound to $evid so the mutant author can't read them.
    run_agent "You are in a worktree that has the intent + the code but NOT the evals. Propose the smallest
               code diff that plausibly VIOLATES the intent facet guarded by $evid. Write it to /tmp/$evid.mutant.diff. Stop."
    if git -C "$ROOT" apply --check "/tmp/$evid.mutant.diff" 2>/dev/null; then
      git -C "$ROOT" apply "/tmp/$evid.mutant.diff"
      #   RUNNER: run the FULL suite. Require target $evid RED while all OTHER evals stay GREEN (surgical).
      #   On success, the DRIVER appends `killed` + `passed` events to $sdir/trust.log with eval_hash+spec_fp
      #   (the values `sde trust` recomputes). On failure after K tries → leave untrusted (a coverage hole).
      git -C "$ROOT" checkout -- .
    fi
    git -C "$ROOT" worktree remove -f "$wt" 2>/dev/null; rm -rf "$wt"
  done
  commit "establish trust for $slice"
}

# rung 5 — verify. The DRIVER runs the suite and writes runs.log; a different-model judge grades
# semantic/ux evals (pinned via $JUDGE_MODEL); then the bounded intent-audit (eval+intent only).
verify_slice(){
  local slice="$1"
  #   RUNNER: run each bound eval; append {verdict,spec_fp,...} to $ROOT/.sde/runs.log (DRIVER writes, not the agent).
  #   For semantic/ux evals: run the judge with --model "$JUDGE_MODEL" (must differ from the builder).
  run_agent "Resume SDE. Run the bounded intent-audit for slice $slice (you see ONLY the intents + the eval files,
             never the code). Exhibit a betrayer or report none. Write the result into spec.md's Intent-audit block. Stop."
  commit "verify $slice"
}

LAST_RUNG=""; NOPROG=0; STEP=0
while :; do
  [ -f "$ROOT/.sde/STOP" ] && { escalate "kill-switch .sde/STOP present"; exit 7; }            # kill-switch
  [ -f "$ROOT/.sde/STEER" ] && { escalate "steer: $(cat "$ROOT/.sde/STEER")"; rm -f "$ROOT/.sde/STEER"; }  # read-once steer
  STEP=$((STEP+1)); [ "$STEP" -gt "$MAX_STEPS" ] && { escalate "MAX_STEPS=$MAX_STEPS reached"; exit 6; }   # budget

  IFS=$'\t' read -r SLICE PHASE ACTION < <($SDE next --root "$ROOT" --porcelain); rc=$?
  [ "$rc" -eq 0 ] && { escalate "all seeded slices done — human must verify objective.md 'done when'"; exit 0; }  # NEVER auto-succeed
  [ "$rc" -eq 1 ] && { escalate "structural error from sde next"; exit 1; }
  [ -f "$ROOT/.sde/slices/$SLICE/.blocked" ] && advance_or_stop

  RUNG_ID="$SLICE/$PHASE"; HEAD_BEFORE="$(git -C "$ROOT" rev-parse HEAD)"
  echo ">> step $STEP  $RUNG_ID :: $ACTION"

  case "$PHASE" in
    spec)    run_agent "Resume SDE via .sde/RESUME.md. Author intent statements for slice $SLICE (spec.md). Commit. Stop."; commit "spec $SLICE";;
    bind|trust) run_agent "Resume SDE. For slice $SLICE, write eval code for unbound/untrusted intents and bind them in spec.md. Commit. Stop."
                commit "bind evals $SLICE"; establish_trust "$SLICE";;
    freeze)  cp "$ROOT/.sde/slices/$SLICE/spec.md" "$ROOT/.sde/slices/$SLICE/spec.lock.md"; commit "freeze $SLICE";;
    execute) run_agent "Resume SDE. Implement the next ready task in $SLICE/tasks.md (code only; do not touch evals). Commit. Stop."; commit "execute $SLICE";;
    evalrun) verify_slice "$SLICE";;
    blocked) escalate "$SLICE spec drift after freeze — human re-freeze"; block_slice "$SLICE"; advance_or_stop;;
    done)    : ;;  # this slice done; loop re-derives the next
    *)       escalate "unknown phase '$PHASE' for $SLICE"; block_slice "$SLICE"; advance_or_stop;;
  esac

  HEAD_AFTER="$(git -C "$ROOT" rev-parse HEAD)"                 # no-progress = same rung, no new commit
  if [ "$RUNG_ID" = "$LAST_RUNG" ] && [ "$HEAD_AFTER" = "$HEAD_BEFORE" ]; then NOPROG=$((NOPROG+1)); else NOPROG=0; fi
  LAST_RUNG="$RUNG_ID"
  [ "$NOPROG" -ge "$RETRY_CAP" ] && { escalate "$RUNG_ID: no progress after $RETRY_CAP tries"; block_slice "$SLICE"; advance_or_stop; }
done
