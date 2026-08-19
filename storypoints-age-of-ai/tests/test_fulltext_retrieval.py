from pathlib import Path
import tempfile
import unittest

from gate2.fulltext_retrieval import FullTextError, build_inventory, verify_final, verify_inventory


class FullTextRetrievalTests(unittest.TestCase):
    def test_inventory_reconciles_and_is_immutable(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "d10"
            manifest = build_inventory(output)
            self.assertEqual(manifest["family_count"], 2076)
            self.assertEqual(manifest, verify_inventory(output))
            self.assertGreater(manifest["preliminary_status_counts"].get("open_candidate_identified", 0), 0)
            with self.assertRaises(FullTextError):
                build_inventory(output)

    def test_current_final_retrieval_reconciles(self):
        manifest = verify_final()
        self.assertEqual(manifest["family_count"], 2076)
        self.assertEqual(manifest["retrieved_pdf_count"], 1605)
        self.assertEqual(sum(manifest["status_counts"].values()), 2076)


if __name__ == "__main__":
    unittest.main()
