import unittest

from gate2.citation_chasing import choose_title_match, normalized_title, seed_rows


class CitationChasingTests(unittest.TestCase):
    def test_seed_population_is_exact(self):
        rows = seed_rows(); self.assertEqual(len(rows), 570); self.assertEqual(len({r["family_id"] for r in rows}), 570)

    def test_title_matching_is_conservative(self):
        seed = {"title": "Human Attention in AI Assisted Software Delivery", "year": 2026}
        exact = [{"id": "W1", "title": "Human Attention in AI-Assisted Software Delivery", "publication_year": 2026}]
        row, basis, score = choose_title_match(seed, exact)
        self.assertEqual(row["id"], "W1"); self.assertEqual(basis, "exact_normalized_title"); self.assertEqual(score, 1.0)
        row, basis, _ = choose_title_match(seed, [{"id": "W2", "title": "Unrelated Chemistry", "publication_year": 2026}])
        self.assertIsNone(row); self.assertEqual(basis, "unresolved")

    def test_normalization_does_not_expose_credentials(self):
        self.assertEqual(normalized_title("AI-Assisted: Review!"), "ai assisted review")


if __name__ == "__main__": unittest.main()
