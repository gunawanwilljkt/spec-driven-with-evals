"""
VALIDITY-AWARE eval (contract / invariant eval).

Encodes the INTENT as an invariant over a realistic paging SESSION, not an
example slice: fetch page 1, then a NEW item arrives (concurrent write), then
fetch the rest. Assert that every item present for the WHOLE session is
returned exactly once — no omission, no duplicate.

This is the scenario keyset pagination is designed to survive and OFFSET
paging is not. Deterministic: no randomness, no timing. Emits a structured
JSON verdict (the eval-result contract) and exits non-zero on FAIL to gate.

IMPL env var selects the implementation (default: correct).
"""

import os
import sys
import json
import paginate

IMPL = os.environ.get("IMPL", "correct")


def page_session_with_concurrent_insert(conn, page_size):
    """Fetch page 1, inject a new EARLY-timestamp row, fetch remaining pages."""
    collected = []
    if IMPL == "mutant":
        # page 1
        collected += paginate.page_offset(conn, page_size, 0)
        # concurrent write: a row with an earlier-than-everything timestamp
        paginate.insert_item(conn, 99, "t00")
        # continue paging by offset (the bug: offset window shifted)
        offset = page_size
        while True:
            page = paginate.page_offset(conn, page_size, offset)
            if not page:
                break
            collected += page
            offset += page_size
    else:
        ids, cursor = paginate.page_keyset(conn, page_size)
        collected += ids
        paginate.insert_item(conn, 99, "t00")  # same concurrent write
        while True:
            ids, cursor = paginate.page_keyset(conn, page_size, cursor)
            if not ids:
                break
            collected += ids
    return collected


def run():
    # ids 1..6 exist for the WHOLE session -> all 6 must be returned exactly once.
    rows = [(i, f"t{i:02d}") for i in range(1, 7)]
    conn = paginate.make_db(rows)
    must_be_present = {i for i, _ in rows}

    collected = page_session_with_concurrent_insert(conn, page_size=3)

    seen_counts = {x: collected.count(x) for x in set(collected)}
    duplicates = sorted([x for x, n in seen_counts.items() if n > 1])
    omissions = sorted(must_be_present - set(collected))
    passed = (not duplicates) and (not omissions)

    verdict = {
        "eval": "pagination.stable_under_concurrent_write",
        "intent": "every item present for the whole paging session is returned exactly once",
        "impl": IMPL,
        "verdict": "PASS" if passed else "FAIL",
        "evidence": {
            "stream": collected,
            "duplicated_ids": duplicates,
            "omitted_ids": omissions,
        },
    }
    print(json.dumps(verdict, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(run())
