# Objective: Reliable list pagination

North star: users paging any list or feed see a consistent, complete view — every item present for
the whole session exactly once — even as data changes underneath them.

Done when:
- A paging session returns every item present throughout it exactly once, proven by a *trusted* eval.
- That eval is trusted (GREEN-on-right ∧ RED-on-wrong) and passes at the frozen spec.

Slices:
- 01-pagination — the core keyset paging guarantee.
