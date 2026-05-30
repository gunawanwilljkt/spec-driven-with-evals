#!/usr/bin/env bash
# Reproduces SC-1/SC-2 for this slice: the mutant is GREEN on the unit tests but RED on the eval.
# The mutant is applied as a DIFF (the framework's canonical mutant form), run, then reverted.
# Zero install (python3 stdlib + `patch`).
set -u
cd "$(dirname "$0")"
SRC=src/paginate.py
run_unit(){ PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py' >/dev/null 2>&1; echo $?; }
run_eval(){ python3 evals/session.py >/dev/null 2>&1; echo $?; }

UC=$(run_unit); EC=$(run_eval)                 # correct implementation
cp "$SRC" "$SRC.bak"
patch -s -p0 < evals/mutant.diff               # apply the intent-violating mutant
UM=$(run_unit); EM=$(run_eval)                 # mutant implementation
mv "$SRC.bak" "$SRC"                            # revert (idempotent)

pf(){ [ "$1" = 0 ] && echo PASS || echo FAIL; }
echo "unit×correct=$(pf $UC)  unit×mutant=$(pf $UM)  eval×correct=$(pf $EC)  eval×mutant=$(pf $EM)"
if [ "$UC" = 0 ] && [ "$UM" = 0 ] && [ "$EC" = 0 ] && [ "$EM" != 0 ]; then
  echo "PROOF HOLDS: mutant is GREEN on unit tests but RED on the eval (the eval's kill record)."
  echo "   → GREEN-on-right ∧ RED-on-wrong ⇒ evals/session.py is a TRUSTED, non-vacuous eval."
  exit 0
else
  echo "PROOF BROKEN"; exit 1
fi
