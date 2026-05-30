"""
Slice under test: ONE pure module — a paginated "list items, newest-ordered"
read, the kind every list/feed endpoint has.

INTENT (what we actually mean):
  "A client paging through the list sees every item exactly once. Paging is
   STABLE under concurrent writes: an item that exists for the whole paging
   session is neither dropped nor duplicated across a page boundary."

This is the entire reason keyset (cursor) pagination exists. The classic,
real-world violation is OFFSET pagination ordered by a non-unique / shifting
key: when a row is inserted before the current offset between two page
fetches, the offset window shifts and a row silently falls through the crack
(and another gets duplicated).

Two implementations behind one conceptual contract:
  - Paginator.correct : keyset cursor on (created_at, id)  -> intent-correct
  - Paginator.mutant  : OFFSET paging, ORDER BY created_at -> intent-violating

Both look like reasonable "ORDER BY created_at, page it" code. The mutant is
what you get if you reach for LIMIT/OFFSET (the obvious first implementation)
instead of a stable cursor. The defect only manifests across a page boundary
when the set changes underneath — exactly what a happy-path unit test won't do.
"""

import sqlite3


def make_db(rows):
    """rows: list of (id, created_at). Fresh in-memory DB."""
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, created_at TEXT NOT NULL)")
    conn.executemany("INSERT INTO items (id, created_at) VALUES (?, ?)", rows)
    conn.commit()
    return conn


def insert_item(conn, item_id, created_at):
    conn.execute("INSERT INTO items (id, created_at) VALUES (?, ?)", (item_id, created_at))
    conn.commit()


# --- intent-VIOLATING mutant: OFFSET paging, no stable cursor ---------------
def page_offset(conn, limit, offset):
    """ORDER BY created_at + LIMIT/OFFSET. Plausible, common, and unstable
    under concurrent inserts before the offset. Returns list of ids."""
    cur = conn.execute(
        "SELECT id FROM items ORDER BY created_at LIMIT ? OFFSET ?",
        (limit, offset),
    )
    return [r[0] for r in cur.fetchall()]


# --- intent-CORRECT: keyset cursor on (created_at, id) ----------------------
def page_keyset(conn, limit, cursor=None):
    """
    Stable keyset pagination. `cursor` is None for the first page, else the
    (created_at, id) of the last row of the previous page. Continuation is
    'strictly after the cursor', so inserts BEFORE the cursor cannot shift
    the window. Returns (ids, next_cursor).
    """
    if cursor is None:
        cur = conn.execute(
            "SELECT id, created_at FROM items ORDER BY created_at, id LIMIT ?",
            (limit,),
        )
    else:
        last_ts, last_id = cursor
        cur = conn.execute(
            "SELECT id, created_at FROM items "
            "WHERE (created_at, id) > (?, ?) ORDER BY created_at, id LIMIT ?",
            (last_ts, last_id, limit),
        )
    rows = cur.fetchall()
    ids = [r[0] for r in rows]
    next_cursor = (rows[-1][1], rows[-1][0]) if rows else None
    return ids, next_cursor
