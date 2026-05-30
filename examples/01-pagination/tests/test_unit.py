"""ORDINARY unit test — exactly what a competent engineer writes for pagination.

Seeds a STATIC fixture, walks the pages, asserts the slices and full coverage. A genuine,
defensible test — NOT a strawman. It passes for BOTH the correct impl and the mutant, because it
never mutates the dataset mid-paging. The intent it silently fails to encode is *stability under a
concurrent write* — the whole point of a cursor. That gap is what the eval (../evals/I3.session.py)
catches and this test does not. "Tests pass" ≠ "intent satisfied".
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import paginate  # noqa: E402


def collect(conn, size):
    out, cursor = [], None
    while True:
        ids, cursor = paginate.page(conn, size, cursor)
        if not ids:
            break
        out.extend(ids)
    return out


class TestPaginationUnit(unittest.TestCase):
    def setUp(self):
        self.rows = [(i, f"t{i:02d}") for i in range(1, 7)]   # static: ids 1..6
        self.conn = paginate.make_db(self.rows)

    def test_first_page_slice(self):
        self.assertEqual(collect(self.conn, 3)[:3], [1, 2, 3])

    def test_second_page_slice(self):
        self.assertEqual(collect(self.conn, 3)[3:6], [4, 5, 6])

    def test_all_pages_cover_static_set(self):
        self.assertEqual(collect(self.conn, 3), [1, 2, 3, 4, 5, 6])


if __name__ == "__main__":
    unittest.main(verbosity=2)
