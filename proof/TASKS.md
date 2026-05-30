# Task list (on-disk state machine; first unchecked box = next action)

- [x] Write SPEC.md with objective + intent statements
- [x] Write ordinary unit test (test_unit.py)
- [x] Implement correct (keyset) + mutant (offset) in paginate.py
- [x] Write validity-aware contract eval (eval_contract.py) with kill record
- [x] Verify truth table: unit green on mutant, eval red on mutant
- [ ] Add a second eval covering intent I1 (stable order) independently of I2/I3
- [ ] Wire the LLM-as-judge semantic eval (currently a stubbed verdict contract)
