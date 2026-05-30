"""Paginated item list — one pure module, the kind every list/feed endpoint has.

INTENT: a client paging the list sees every item present for the whole paging session exactly
once — no omission, no duplicate — stable under a concurrent insert before the cursor. That is the
entire reason keyset (cursor) pagination exists.

Public contract (stable across the correct impl and the mutant):
    page(conn, limit, cursor=None) -> (ids, next_cursor)
The mutant (evals/I3.mutant.diff) swaps ONLY the body of page() for naive OFFSET paging while
keeping this signature — the "obvious first implementation" a reviewer nods at.
"""
import sqlite3


def make_db(rows):
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, created_at TEXT NOT NULL)")
    conn.executemany("INSERT INTO items (id, created_at) VALUES (?, ?)", rows)
    conn.commit()
    return conn


def insert_item(conn, item_id, created_at):
    conn.execute("INSERT INTO items (id, created_at) VALUES (?, ?)", (item_id, created_at))
    conn.commit()


def page(conn, limit, cursor=None):
    """Stable keyset pagination. cursor is None for page 1, else the (created_at, id) of the last
    row of the previous page. Continuation is 'strictly after the cursor', so an insert BEFORE the
    cursor cannot shift the window. Returns (ids, next_cursor)."""
    if cursor is None:
        rows = conn.execute(
            "SELECT id, created_at FROM items ORDER BY created_at, id LIMIT ?",
            (limit,),
        ).fetchall()
    else:
        last_ts, last_id = cursor
        rows = conn.execute(
            "SELECT id, created_at FROM items WHERE (created_at, id) > (?, ?) "
            "ORDER BY created_at, id LIMIT ?",
            (last_ts, last_id, limit),
        ).fetchall()
    ids = [r[0] for r in rows]
    next_cursor = (rows[-1][1], rows[-1][0]) if rows else None
    return ids, next_cursor
