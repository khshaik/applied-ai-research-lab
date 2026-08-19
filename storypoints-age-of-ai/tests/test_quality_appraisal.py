from pathlib import Path
import unittest

from gate2.quality_appraisal import validate_part, verify_primary


class QualityAppraisalTests(unittest.TestCase):
    def test_real_parts_validate_when_available(self):
        for part in ("a", "b"):
            path = Path(f"gate2/output/systematic/v1.3/20260816/d12/appraisal_part_{part}.jsonl")
            if path.exists():
                self.assertEqual(validate_part(path, part)["family_count"], 285)

    def test_primary_validates_when_available(self):
        path = Path("gate2/output/systematic/v1.3/20260816/d12/primary")
        if not path.exists():
            self.skipTest("D12 primary appraisals still in progress")
        self.assertEqual(verify_primary(path)["family_count"], 570)


if __name__ == "__main__":
    unittest.main()
