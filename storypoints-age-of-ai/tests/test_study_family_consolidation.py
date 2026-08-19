import csv
import json
from pathlib import Path
import tempfile
import unittest

from gate2.study_family_consolidation import (
    APPROVED_MULTI_REPORT_GROUPS,
    D06,
    ConsolidationError,
    _read_reports,
    build,
    consolidate,
    verify,
)


class StudyFamilyConsolidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = _read_reports()
        cls.families, cls.mapping, cls.candidates = consolidate(cls.rows)

    def test_approved_groups_are_disjoint_and_present(self):
        available = {row["canonical_id"] for row in self.rows}
        approved = [member for group in APPROVED_MULTI_REPORT_GROUPS for member in group["members"]]
        self.assertEqual(len(approved), len(set(approved)))
        self.assertTrue(set(approved) <= available)

    def test_expected_reconciliation(self):
        self.assertEqual(len(self.rows), 3962)
        self.assertEqual(len(self.families), 3930)
        self.assertEqual(sum(f["member_count"] > 1 for f in self.families), 23)
        self.assertEqual(sum(f["member_count"] == 1 for f in self.families), 3907)
        self.assertEqual(sum(f["member_count"] for f in self.families if f["member_count"] > 1), 55)
        self.assertEqual(len(self.candidates), 39)
        self.assertEqual(sum(c["decision"] == "consolidate" for c in self.candidates), 34)
        self.assertEqual(sum(c["decision"] == "keep_separate" for c in self.candidates), 5)

    def test_every_report_maps_to_exactly_one_family(self):
        report_ids = {row["canonical_id"] for row in self.rows}
        mapped_ids = [row["canonical_id"] for row in self.mapping]
        self.assertEqual(len(mapped_ids), len(report_ids))
        self.assertEqual(set(mapped_ids), report_ids)
        self.assertEqual(sum(row["representative"] == "true" for row in self.mapping), len(self.families))

    def test_known_merge_and_keep_separate(self):
        family_by_report = {row["canonical_id"]: row["family_id"] for row in self.mapping}
        self.assertEqual(
            family_by_report["CAN-3eb30db192b5bbddb26f"],
            family_by_report["CAN-c0aa43d9e6055e072e52"],
        )
        self.assertNotEqual(
            family_by_report["CAN-7478ece040e9ed80bff1"],
            family_by_report["CAN-db1e15fdb9ef3f6bbbc4"],
        )

    def test_immutable_build_and_verify(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "d07"
            manifest = build(output)
            self.assertEqual(manifest["canonical_report_count"], 3962)
            self.assertEqual(manifest["study_family_count"], 3930)
            self.assertEqual(manifest, verify(output))
            with self.assertRaises(ConsolidationError):
                build(output)

            with (output / "canonical_to_family.csv").open(encoding="utf-8", newline="") as handle:
                self.assertEqual(len(list(csv.DictReader(handle))), 3962)
            families = [json.loads(line) for line in (output / "study_families.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(families), 3930)


if __name__ == "__main__":
    unittest.main()
