#!/usr/bin/env bash
# One command reproduces the entire core proof. Zero install (python3 stdlib).
set -u
cd "$(dirname "$0")"
IMPL=correct python3 -m unittest test_unit >/dev/null 2>&1; UC=$?
IMPL=mutant  python3 -m unittest test_unit >/dev/null 2>&1; UM=$?
IMPL=correct python3 eval_contract.py >/dev/null 2>&1; EC=$?
IMPL=mutant  python3 eval_contract.py >/dev/null 2>&1; EM=$?
pf(){ [ "$1" = 0 ] && echo "PASS"; [ "$1" != 0 ] && echo "FAIL"; }
echo "unit×correct=$(pf $UC)  unit×mutant=$(pf $UM)  eval×correct=$(pf $EC)  eval×mutant=$(pf $EM)"
if [ "$UC" = 0 ] && [ "$UM" = 0 ] && [ "$EC" = 0 ] && [ "$EM" != 0 ]; then
  echo "PROOF HOLDS: mutant is GREEN on unit tests but RED on the eval."; exit 0
else
  echo "PROOF BROKEN"; exit 1
fi
