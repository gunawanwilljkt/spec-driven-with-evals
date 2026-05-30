# Decisions — append-only ADR log

## 2026-05-30T10:48Z — Keyset cursor over OFFSET paging  [slice:01-pagination]
Decision: implement pagination as a keyset cursor on (created_at, id), not LIMIT/OFFSET.
Why: OFFSET paging duplicates and omits rows when the set changes under the reader — the exact I1/I2
violation the session eval catches (stream becomes [1,2,3,3,4,5,6], duplicated_ids:[3]). Keyset is
stable by construction because continuation is "strictly after the cursor".
Alternatives rejected: OFFSET paging (it is the mutant; it fails the session eval).
By: example.
