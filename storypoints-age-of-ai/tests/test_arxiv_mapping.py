from __future__ import annotations

import csv
import json
from pathlib import Path
import tempfile
import unittest

from gate2.arxiv_mapping import ArxivMappingError, appraise_mapping, verify_mapping
from gate2.query_appraisal import deterministic_sample_positions


class ArxivMappingTests(unittest.TestCase):
    def test_checked_in_mapping_reconciles_and_recalls_both_classes(self):
        result = verify_mapping(
            "gate2/output/development/arxiv/AX-S5R-20260814-retry1",
            "research/studies/vdcm/evidence-map/registries/arxiv_s4_mapping_v0.1.json",
        )
        self.assertEqual(result["records_reconciled"], 187)
        self.assertTrue(result["sentinel_recall_pass"])
        self.assertFalse(result["freeze_ready"])

    def test_query_drift_hard_stops(self):
        source = Path("research/studies/vdcm/evidence-map/registries/arxiv_s4_mapping_v0.1.json")
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "registry.json"
            value = json.loads(source.read_text())
            value["query"] += " AND all:drift"
            target.write_text(json.dumps(value))
            with self.assertRaisesRegex(ArxivMappingError, "query text"):
                verify_mapping("gate2/output/development/arxiv/AX-S5R-20260814-retry1", target)

    def test_s5t_mapping_reconciles_and_recalls_positive_and_disconfirming_classes(self):
        result = verify_mapping(
            "gate2/output/development/arxiv/AX-S5T-20260814-retry1",
            "research/studies/vdcm/evidence-map/registries/arxiv_s5t_mapping_v0.1.json",
        )
        self.assertEqual(result["mapped_family_id"], "S5T")
        self.assertEqual(result["records_reconciled"], 394)
        self.assertTrue(result["sentinel_class_complete"])
        self.assertTrue(result["sentinel_recall_pass"])
        self.assertFalse(result["freeze_ready"])

    def test_checked_in_s5t_precision_appraisal_rederives_exactly(self):
        decisions = json.loads(Path(
            "gate2/output/development/query_appraisals/AX-S5T-20260816-query-decisions-v1.json"
        ).read_text())["decisions"]
        result = appraise_mapping(
            "gate2/output/development/arxiv/AX-S5T-20260814-retry1",
            "research/studies/vdcm/evidence-map/registries/arxiv_s5t_mapping_v0.1.json",
            decisions,
        )
        checked = json.loads(Path(
            "gate2/output/development/query_appraisals/AX-S5T-20260816-query-appraisal-v1.json"
        ).read_text())
        self.assertEqual(result, checked)
        self.assertTrue(result["freeze_ready"])
        self.assertEqual(result["sample_size"], 50)

    def test_s5s_mapping_reconciles_and_recalls_positive_and_disconfirming_classes(self):
        result = verify_mapping(
            "gate2/output/development/arxiv/AX-S5S-20260814-retry1",
            "research/studies/vdcm/evidence-map/registries/arxiv_s5s_mapping_v0.1.json",
        )
        self.assertEqual(result["mapped_family_id"], "S5S")
        self.assertEqual(result["records_reconciled"], 1333)
        self.assertTrue(result["sentinel_class_complete"])
        self.assertTrue(result["sentinel_recall_pass"])
        self.assertFalse(result["freeze_ready"])

    def test_checked_in_s5s_precision_sample_and_appraisal_rederive_exactly(self):
        export = Path("gate2/output/development/arxiv/AX-S5S-20260814-retry1")
        decision_path = Path(
            "gate2/output/development/query_appraisals/"
            "AX-S5S-20260816-query-decisions-v2.json"
        )
        result_path = Path(
            "gate2/output/development/query_appraisals/"
            "AX-S5S-20260816-query-appraisal-v2.json"
        )
        artifact = json.loads(decision_path.read_text(encoding="utf-8"))
        rows = list(csv.DictReader(
            (export / "records.csv").open(encoding="utf-8", newline="")
        ))
        positions, seed = deterministic_sample_positions(
            len(rows), "arxiv", "S5S", "0.1"
        )
        ordered_ids = [rows[position]["arxiv_id_version"] for position in positions]
        self.assertEqual(artifact["source"], "arxiv")
        self.assertEqual(artifact["family_id"], "S5S")
        self.assertEqual(artifact["query_version"], "0.1")
        self.assertEqual(artifact["sampling_seed_sha256"], seed)
        self.assertEqual(artifact["sample_positions_zero_based"], positions)
        self.assertEqual(artifact["ordered_sample_source_ids"], ordered_ids)
        self.assertEqual(
            [row["source_id"] for row in artifact["decisions"]], ordered_ids
        )
        result = appraise_mapping(
            export,
            "research/studies/vdcm/evidence-map/registries/arxiv_s5s_mapping_v0.1.json",
            artifact["decisions"],
        )
        checked = json.loads(result_path.read_text(encoding="utf-8"))
        self.assertEqual(result, checked)
        self.assertEqual(result["sample_size"], 100)
        self.assertEqual(result["sample_likely_relevant"], 6)
        self.assertEqual(result["sample_uncertain"], 7)
        self.assertEqual(result["relevant_plus_uncertain_count"], 13)
        self.assertTrue(result["freeze_ready"])

    def test_checked_in_s6_narrow_rule_full_population_appraisal_rederives_exactly(self):
        export = Path("gate2/output/development/arxiv/AX-S6R-20260814-retry1")
        decision_path = Path(
            "gate2/output/development/query_appraisals/"
            "AX-S6R-20260816-query-decisions-v2.json"
        )
        result_path = Path(
            "gate2/output/development/query_appraisals/"
            "AX-S6R-20260816-query-appraisal-v2.json"
        )
        artifact = json.loads(decision_path.read_text(encoding="utf-8"))
        rows = list(csv.DictReader(
            (export / "records.csv").open(encoding="utf-8", newline="")
        ))
        positions, seed = deterministic_sample_positions(
            len(rows), "arxiv", "S6", "0.2"
        )
        ordered_ids = [rows[position]["arxiv_id_version"] for position in positions]
        self.assertEqual(len(rows), 29)
        self.assertEqual(positions, list(range(29)))
        self.assertEqual(artifact["sampling_seed_sha256"], seed)
        self.assertEqual(artifact["sample_positions_zero_based"], positions)
        self.assertEqual(artifact["ordered_sample_source_ids"], ordered_ids)
        self.assertEqual(
            [row["source_id"] for row in artifact["decisions"]], ordered_ids
        )
        result = appraise_mapping(
            export,
            "research/studies/vdcm/evidence-map/registries/arxiv_s6_mapping_v0.2.json",
            artifact["decisions"],
        )
        checked = json.loads(result_path.read_text(encoding="utf-8"))
        self.assertEqual(result, checked)
        self.assertEqual(result["records_reconciled"], 29)
        self.assertEqual(result["sample_size"], 29)
        self.assertEqual(result["sample_likely_relevant"], 10)
        self.assertEqual(result["sample_uncertain"], 0)
        self.assertEqual(result["sample_likely_irrelevant"], 19)
        self.assertTrue(result["sentinel_recall_pass"])
        self.assertTrue(result["freeze_ready"])

    def test_rejected_s6_v1_registry_cannot_be_appraised(self):
        with self.assertRaisesRegex(ArxivMappingError, "developmental family"):
            verify_mapping(
                "gate2/output/development/arxiv/AX-S6R-20260814-retry1",
                "research/studies/vdcm/evidence-map/registries/arxiv_s6_mapping_v0.1.json",
            )

    def test_precision_appraisal_remains_separate_from_screening(self):
        export = "gate2/output/development/arxiv/AX-S5R-20260814-retry1"
        rows = __import__("csv").DictReader(open(f"{export}/records.csv", encoding="utf-8"))
        decisions = [
            {"source_id": row["arxiv_id_version"], "decision": "likely_relevant", "reason": "fixture"}
            for row in list(rows)[:50]
        ]
        result = appraise_mapping(
            export, "research/studies/vdcm/evidence-map/registries/arxiv_s4_mapping_v0.1.json", decisions
        )
        self.assertTrue(result["freeze_ready"])
        self.assertIn("not screening", result["interpretation_boundary"])


if __name__ == "__main__":
    unittest.main()
