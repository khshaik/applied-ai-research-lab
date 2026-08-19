from pathlib import Path
import unittest

from gate2.evidence_extraction_finalize import validate_verified, verify


class EvidenceExtractionFinalizeTests(unittest.TestCase):
    def test_verified_parts_when_available(self):
        paths = {
            "a": Path("gate2/output/systematic/v1.3/20260816/d13/verified_part_a_v2.jsonl"),
            "b": Path("gate2/output/systematic/v1.3/20260816/d13/verified_part_b.jsonl"),
        }
        for part, path in paths.items():
            if path.exists(): self.assertEqual(validate_verified(path, part)["family_count"], 285)

    def test_final_when_available(self):
        path = Path("gate2/output/systematic/v1.3/20260816/d13/final")
        if not path.exists(): self.skipTest("D13 verification pending")
        self.assertEqual(verify(path)["family_count"], 570)


if __name__ == "__main__": unittest.main()
