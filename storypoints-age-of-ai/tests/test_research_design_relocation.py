import hashlib
import json
import unittest
from pathlib import Path

from gate2.frozen_paths import resolve_frozen_path


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "docs/traceability/RESEARCH_DESIGN_RELOCATION_2026-08-20.json"


class ResearchDesignRelocationTests(unittest.TestCase):
    def test_relocation_is_complete_unique_and_byte_preserving(self):
        record = json.loads(RECORD.read_text(encoding="utf-8"))
        rows = record["relocations"]
        self.assertEqual(record["change_type"], "path_only_relocation")
        self.assertEqual(record["relocated_file_count"], 35)
        self.assertEqual(len(rows), 35)
        self.assertEqual(len({row["original_path"] for row in rows}), 35)
        self.assertEqual(len({row["relocated_path"] for row in rows}), 35)
        for row in rows:
            self.assertFalse((ROOT / row["original_path"]).exists())
            relocated = resolve_frozen_path(ROOT, row["original_path"])
            self.assertTrue(relocated.is_file(), row["relocated_path"])
            actual = hashlib.sha256(relocated.read_bytes()).hexdigest()
            self.assertEqual(actual, row["sha256"], row["relocated_path"])
            self.assertFalse(row["content_changed"])

    def test_legacy_frozen_paths_resolve_to_recorded_destinations(self):
        record = json.loads(RECORD.read_text(encoding="utf-8"))
        for row in record["relocations"]:
            resolved = resolve_frozen_path(ROOT, row["original_path"])
            self.assertTrue(resolved.is_file())
            self.assertTrue(resolved.relative_to(ROOT).as_posix().startswith("research/design/"))

    def test_controlled_consolidation_has_no_missing_destination(self):
        path = ROOT / "docs/traceability/CONTROLLED_FOLDER_RELOCATION_2026-08-20.json"
        record = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(record["file_count"], 146)
        self.assertFalse(record["frozen_package_bytes_modified"])
        self.assertFalse(record["scientific_findings_or_decisions_modified"])
        for row in record["relocations"]:
            destination = ROOT / row["relocated_path"]
            self.assertTrue(destination.is_file(), row["relocated_path"])
            actual = hashlib.sha256(destination.read_bytes()).hexdigest()
            self.assertEqual(actual, row["sha256_after_reference_repair"])


if __name__ == "__main__":
    unittest.main()
