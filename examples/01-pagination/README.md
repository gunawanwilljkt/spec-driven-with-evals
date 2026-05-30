# Example 01 — Pagination (the runnable proof)

SDE applied to one real slice — and the **proof of the framework's core claim**: an eval catches an
intent-violation that the ordinary unit tests miss. "Tests pass" ≠ "intent satisfied."

## Run it
```bash
bash run.sh                                       # the truth table (zero install: python3 + patch)
python3 ../../framework/bin/sde status --root .   # derive this slice's state from disk
```

## What it shows
| File | Role |
|---|---|
| `.sde/slices/01-pagination/spec.md` | Intents I1/I2: every item present for the whole session returned exactly once, stable under a concurrent insert. |
| `src/paginate.py` | The **correct** keyset implementation. |
| `evals/mutant.diff` | The **intent-violating mutant** (naive `LIMIT/OFFSET` paging) — the "obvious" wrong impl a reviewer nods at. |
| `tests/test_unit.py` | An ordinary, defensible unit test. **GREEN on both** implementations. |
| `evals/session.py` | The validity-aware journey eval. **GREEN on right, RED on the mutant.** |

Truth table (`run.sh`):

| | correct | mutant |
|---|---|---|
| **unit test** | PASS | **PASS** ← "tests pass" |
| **eval** | PASS | **FAIL** ← intent satisfied only on the right impl |

The eval's RED-on-mutant is its **kill record** → `GREEN-on-right ∧ RED-on-wrong` ⇒ a **trusted,
non-vacuous** eval. That evidence is in `.sde/slices/01-pagination/trust.log`, and `sde status`
derives the slice as `done` (`coverage=2/2 trust=2/2`) purely from disk.

## Mobile, honestly
`evals/journey.maestro.yaml` is the **documented** mobile binding of the *same* journey-eval
contract (`flow-spec in → {verdict, artifacts} out`). It is **not executed** here (no Maestro, no
app build — see `../../KNOWN-LIMITATIONS.md`); `session.py` is the executable analogue. The point:
the identical intent binds to a mobile runner with zero change to the spec or the contract.

## Judge tier (no API key)
`evals/I2.rubric.md` + `judge_sample_verdict.json` show the LLM-as-judge **contract** (`gate=flag`,
excluded from the trust requirement) without a faked model call.

## Why this is the whole thesis in one folder
Code generation was never the hard part here — both implementations are a few lines and "look
right." The hard part is knowing which one honors the intent. The **eval** is what knows.
