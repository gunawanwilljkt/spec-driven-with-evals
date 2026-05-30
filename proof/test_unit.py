"""
ORDINARY unit test — exactly what a competent engineer writes for pagination.

It seeds a STATIC fixture, fetches each page, and asserts the pages return the
expected slices in order and the page size is respected. It is a genuine,
defensible test of "does pagination return the right pages?" — NOT a strawman.

It passes for BOTH implementations, because it never mutates the dataset
mid-paging. With a static set, OFFSET paging and keyset paging return the same
thing. The intent the test silently fails to encode is *stability under
concurrent writes* — the whole point of using a cursor.

IMPL env var selects the implementation under test (default: correct).
"""

import os
import unittest
import paginate

IMPL = os.environ.get("IMPL", "correct")


def get_all_pages(conn, page_size):
    """Drive whichever implementation, return the concatenated id stream."""
    out = []
    if IMPL == "mutant":
        offset = 0
        while True:
            page = paginate.page_offset(conn, page_size, offset)
            if not page:
                break
            out.extend(page)
            offset += page_size
    else:
        cursor = None
        while True:
            ids, cursor = paginate.page_keyset(conn, page_size, cursor)
            if not ids:
                break
            out.extend(ids)
    return out


class TestPaginationUnit(unittest.TestCase):
    def setUp(self):
        # Static happy-path fixture: ids 1..6, distinct increasing timestamps.
        self.rows = [(i, f"t{i:02d}") for i in range(1, 7)]
        self.conn = paginate.make_db(self.rows)

    def test_first_page_is_correct_slice(self):
        out = get_all_pages(self.conn, page_size=3)
        self.assertEqual(out[:3], [1, 2, 3])

    def test_second_page_is_correct_slice(self):
        out = get_all_pages(self.conn, page_size=3)
        self.assertEqual(out[3:6], [4, 5, 6])

    def test_all_pages_cover_static_set(self):
        out = get_all_pages(self.conn, page_size=3)
        self.assertEqual(out, [1, 2, 3, 4, 5, 6])


if __name__ == "__main__":
    unittest.main(verbosity=2)
