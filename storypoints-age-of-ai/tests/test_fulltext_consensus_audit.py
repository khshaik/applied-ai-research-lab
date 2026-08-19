import tempfile
from pathlib import Path
import unittest

from gate2.fulltext_consensus_audit import prepare, validate_decisions, verify
from gate2.fulltext_screening import FullTextScreeningError


class FullTextConsensusAuditTests(unittest.TestCase):
    def test_sample_is_deterministic_and_immutable(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "audit"
            result = prepare(output)
            self.assertEqual(result["population_count"], 1096)
            self.assertEqual(result["sample_size"], 100)
            self.assertEqual(result, verify(output))
            with self.assertRaises(FullTextScreeningError):
                prepare(output)

    def test_real_decisions_are_bound_when_available(self):
        path = Path("gate2/output/systematic/v1.3/20260816/d11/screening/adjudication/consensus_quality_audit/consensus_include_audit_decisions.jsonl")
        if not path.exists():
            self.skipTest("D11 consensus audit decisions are still in progress")
        result = validate_decisions(decisions_path=path)
        self.assertEqual(result["sample_size"], 100)


if __name__ == "__main__":
    unittest.main()
