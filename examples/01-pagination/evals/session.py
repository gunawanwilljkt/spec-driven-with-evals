"""VALIDITY-AWARE eval for intent I3 (a journey/contract eval).

Encodes I3 as an INVARIANT over a realistic paging session, not an example slice: fetch page 1, a
new EARLY-timestamp row arrives (concurrent write before the cursor), then fetch the rest. Assert
every item present for the WHOLE session (ids 1..6) is returned exactly once. Deterministic — no
randomness, no timing. Emits a structured JSON verdict (the eval-result contract) and exits
non-zero on FAIL, so it gates.

This is the runner-agnostic journey contract: flow in (a paging session) → {verdict, evidence} out.
The mutant (naive OFFSET paging) returns the stream [1,2,3,3,4,5,6] → duplicated_ids:[3]: a user
paging the feed sees row 3 twice. Keyset returns each item once. RED-on-mutant ∧ GREEN-on-right =
this eval's kill record → it is a TRUSTED, non-vacuous eval.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import paginate  # noqa: E402


def run():
    rows = [(i, f"t{i:02d}") for i in range(1, 7)]      # ids 1..6 exist for the whole session
    conn = paginate.make_db(rows)
    must_be_present = {i for i, _ in rows}

    collected = []
    ids, cursor = paginate.page(conn, 3, None)          # page 1
    collected += ids
    paginate.insert_item(conn, 99, "t00")               # concurrent write: earlier than everything
    while True:                                         # continue paging
        ids, cursor = paginate.page(conn, 3, cursor)
        if not ids:
            break
        collected += ids

    counts = {x: collected.count(x) for x in set(collected)}
    duplicated = sorted([x for x, n in counts.items() if n > 1])
    omitted = sorted(must_be_present - set(collected))
    passed = not duplicated and not omitted

    verdict = {
        "eval": "I3.contract",
        "intent": "every item present for the whole paging session is returned exactly once",
        "verdict": "PASS" if passed else "FAIL",
        "evidence": {"stream": collected, "duplicated_ids": duplicated, "omitted_ids": omitted},
    }
    print(json.dumps(verdict, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(run())
