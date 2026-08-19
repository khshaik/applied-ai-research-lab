from pathlib import Path
import unittest

from gate2.quality_appraisal_reconcile import verify


class QualityAppraisalReconcileTests(unittest.TestCase):
    def test_real_reconciliation_validates_when_available(self):
        path = Path("gate2/output/systematic/v1.3/20260816/d12/reconciliation")
        if not path.exists():
            self.skipTest("D12 cross-audit reconciliation pending")
        result = verify(path)
        self.assertEqual(result["concordant_count"] + result["dispute_count"], 570)


if __name__ == "__main__":
    unittest.main()
