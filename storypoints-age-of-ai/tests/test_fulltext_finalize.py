import json
from pathlib import Path
import tempfile
import unittest

from gate2.fulltext_finalize import finalize, validate_adjudication, verify
from gate2.fulltext_screening import FullTextScreeningError


class FullTextFinalizeTests(unittest.TestCase):
    def test_real_adjudication_is_exactly_bound_when_available(self):
        path = Path("gate2/output/systematic/v1.3/20260816/d11/screening/adjudication/adjudicated_decisions.jsonl")
        if not path.exists():
            self.skipTest("D11 adjudication is still in progress")
        result = validate_adjudication(path)
        self.assertEqual(result["family_count"], 357)

    def test_final_output_conserves_population_when_available(self):
        final = Path("gate2/output/systematic/v1.3/20260816/d11/screening/final")
        if not final.exists():
            self.skipTest("D11 final output is not published yet")
        result = verify(final)
        self.assertEqual(result["total_family_count"], 2076)
        self.assertEqual(sum(result["status_counts"].values()), 2076)

    def test_duplicate_adjudication_is_rejected(self):
        source = Path("gate2/output/systematic/v1.3/20260816/d11/screening/adjudication/adjudicated_decisions.jsonl")
        if not source.exists():
            self.skipTest("D11 adjudication is still in progress")
        rows = source.read_text(encoding="utf-8").splitlines()
        with tempfile.TemporaryDirectory() as directory:
            bad = Path(directory) / "bad.jsonl"
            bad.write_text("\n".join(rows + [rows[0]]) + "\n", encoding="utf-8")
            with self.assertRaises(FullTextScreeningError):
                validate_adjudication(bad)


if __name__ == "__main__":
    unittest.main()
