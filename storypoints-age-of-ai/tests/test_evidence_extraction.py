from pathlib import Path
import unittest

from gate2.evidence_extraction import validate_part, verify_primary


class EvidenceExtractionTests(unittest.TestCase):
    def test_parts_validate_when_available(self):
        for part in ("a", "b"):
            path = Path(f"gate2/output/systematic/v1.3/20260816/d13/extraction_part_{part}.jsonl")
            if path.exists(): self.assertEqual(validate_part(path, part)["family_count"], 285)

    def test_primary_validates_when_available(self):
        path = Path("gate2/output/systematic/v1.3/20260816/d13/primary")
        if not path.exists(): self.skipTest("D13 extraction pending")
        self.assertEqual(verify_primary(path)["family_count"], 570)


if __name__ == "__main__": unittest.main()
