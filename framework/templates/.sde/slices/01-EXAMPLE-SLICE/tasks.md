# Tasks — 01-EXAMPLE-SLICE
<!-- status ∈ {todo, in_progress, done, blocked}.  owner@ts claims a task (stale-reclaimable, 30min).
     targets = the eval id(s) this task must turn (and keep) green — the task→eval binding.
     deps = task ids that must be `done` first.
     A task is effectively DONE only if status=done AND runs.log shows PASS for its `targets` at the
     current spec_lock AND those evals are trusted. Derive done; never trust the label (RESUME Rule B). -->

| id   | targets | deps | status | owner@ts |
|------|---------|------|--------|----------|
| T-01 | I1      | -    | todo   | -        |
| T-02 | I2      | T-01 | todo   | -        |
