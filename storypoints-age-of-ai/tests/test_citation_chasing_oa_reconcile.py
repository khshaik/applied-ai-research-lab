import unittest

from gate2.citation_chasing_oa_reconcile import _local_bindings


class CitationChasingOpenAlexReconcileTests(unittest.TestCase):
    def test_two_local_bindings_are_exact_and_unique(self):
        rows = _local_bindings()
        self.assertEqual(len(rows), 2)
        self.assertEqual({r["openalex_id"] for r in rows}, {
            "https://openalex.org/W7164784501",
            "https://openalex.org/W7132946893",
        })
        self.assertTrue(all(r["match_basis"].startswith("frozen_d06_exact") for r in rows))


if __name__ == "__main__":
    unittest.main()
