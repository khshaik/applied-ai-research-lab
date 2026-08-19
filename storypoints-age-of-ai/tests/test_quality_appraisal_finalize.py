from pathlib import Path
import unittest

from gate2.quality_appraisal_finalize import validate_adjudication, verify


class QualityAppraisalFinalizeTests(unittest.TestCase):
    def test_adjudication_validates_when_available(self):
        path = Path("gate2/output/systematic/v1.3/20260816/d12/reconciliation/adjudicated_appraisals.jsonl")
        if not path.exists():
            self.skipTest("D12 adjudication pending")
        self.assertEqual(validate_adjudication(path)["family_count"], 567)

    def test_final_validates_when_available(self):
        path = Path("gate2/output/systematic/v1.3/20260816/d12/final")
        if not path.exists():
            self.skipTest("D12 final pending")
        self.assertEqual(verify(path)["family_count"], 570)


if __name__ == "__main__":
    unittest.main()
