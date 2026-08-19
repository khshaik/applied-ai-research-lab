import tempfile
from pathlib import Path
import unittest

from gate2.fulltext_screening import FullTextScreeningError, prepare, verify_packet


class FullTextScreeningTests(unittest.TestCase):
    def test_packet_reconciles_and_is_immutable(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "screening"
            manifest = prepare(output)
            self.assertEqual(manifest["assessable_family_count"], 1604)
            self.assertEqual(manifest["unavailable_family_count"], 472)
            self.assertEqual(manifest["total_family_count"], 2076)
            self.assertEqual(manifest, verify_packet(output))
            with self.assertRaises(FullTextScreeningError):
                prepare(output)


if __name__ == "__main__":
    unittest.main()
