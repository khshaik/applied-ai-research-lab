import json
from pathlib import Path
import tempfile
import unittest

from gate2.adjudication_finalize import D09, validate_adjudications, verify
from gate2.title_abstract_screening import ScreeningControlError


class AdjudicationFinalizeTests(unittest.TestCase):
    def test_current_adjudication_and_final_decisions_verify(self):
        adjudication = validate_adjudications()
        self.assertEqual(adjudication["candidate_count"], 1314)
        self.assertEqual(adjudication["decision_counts"], {"exclude": 1059, "include": 255})
        final = verify()
        self.assertEqual(final["family_count"], 3930)
        self.assertEqual(final["decision_counts"], {"exclude": 1854, "include": 2076})

    def test_incomplete_copy_fails_closed(self):
        rows = (D09 / "adjudicated_decisions.jsonl").read_text(encoding="utf-8").splitlines()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "incomplete.jsonl"
            path.write_text("\n".join(rows[:-1]) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ScreeningControlError, "incomplete"):
                validate_adjudications(path)


if __name__ == "__main__":
    unittest.main()
