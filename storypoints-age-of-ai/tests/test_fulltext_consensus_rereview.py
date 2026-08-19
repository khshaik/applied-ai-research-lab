from pathlib import Path
import unittest

from gate2.fulltext_consensus_rereview import validate


class FullTextConsensusRereviewTests(unittest.TestCase):
    def test_real_rereview_is_bound_when_available(self):
        path = Path("gate2/output/systematic/v1.3/20260816/d11/screening/adjudication/consensus_rereview_decisions.jsonl")
        if not path.exists():
            self.skipTest("D11 consensus re-review is still in progress")
        result = validate(path)
        self.assertEqual(result["family_count"], 1096)


if __name__ == "__main__":
    unittest.main()
