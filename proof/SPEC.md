# Spec — Paginated item list

- OBJECTIVE: Page through the item list so every item present for the whole paging session is returned exactly once, stable under concurrent writes.

## Intent statements (each must map to >=1 eval)
- I1: Pages return items in a stable total order.
- I2: The union of all pages equals the full set — no omissions, no duplicates.
- I3: Paging is stable under a concurrent insert before the cursor (keyset, not offset).

## Eval coverage matrix
| Intent | Eval | Kill record (mutant it reds on) |
|--------|------|---------------------------------|
| I2,I3  | eval_contract.py :: pagination.stable_under_concurrent_write | page_offset() (OFFSET paging) -> duplicated_ids:[3] |
