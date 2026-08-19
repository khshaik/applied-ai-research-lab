import hashlib
import json
import unittest
from pathlib import Path

from gate2.frozen_paths import resolve_frozen_path
from gate2.systematic_export import FROZEN, MATRIX, PLAN, build_plan, canonical_hash, reconcile


ROOT = Path(__file__).resolve().parents[1]


class SystematicExportPlanTests(unittest.TestCase):
    def test_plan_is_exactly_the_frozen_18_pair_matrix(self):
        plan = build_plan()
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        self.assertEqual(plan["run_count"], 18)
        self.assertEqual(len(plan["runs"]), 18)
        self.assertEqual(
            {(r["family_id"], r["source"]) for r in plan["runs"]},
            {(r["family_id"], r["source"]) for r in matrix["rows"]},
        )
        self.assertEqual(len({r["output_dir"] for r in plan["runs"]}), 18)
        self.assertTrue(all(r["to_date"] == "2026-08-16" for r in plan["runs"]))

    def test_s2_uses_fresh_frozen_union_query_not_developmental_records(self):
        run = next(r for r in build_plan()["runs"] if r["family_id"] == "S2")
        self.assertEqual(run["query_id"], "OA-S2I3")
        self.assertEqual(run["developmental_source_query_id"], "OA-S2I2")
        self.assertTrue(run["fresh_systematic_execution_required"])
        self.assertIn("Orchestrating Human-AI Software Delivery", run["query"])

    def test_plan_hashes_freeze_registries_queries_and_matrix_rows(self):
        plan = build_plan()
        frozen_hash = hashlib.sha256(FROZEN.read_bytes()).hexdigest()
        self.assertEqual(plan["freeze_package_sha256"], frozen_hash)
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        by_pair = {(r["family_id"], r["source"]): r for r in matrix["rows"]}
        for run in plan["runs"]:
            self.assertEqual(
                run["acceptance_matrix_row_sha256"],
                canonical_hash(by_pair[(run["family_id"], run["source"])]),
            )
            self.assertEqual(
                run["registry_sha256"],
                hashlib.sha256(
                    resolve_frozen_path(ROOT, run["registry_path"]).read_bytes()
                ).hexdigest(),
            )
            self.assertEqual(run["query_sha256"], hashlib.sha256(run["query"].encode()).hexdigest())

    def test_written_plan_sidecar_is_current(self):
        self.assertTrue(PLAN.is_file())
        sidecar = PLAN.with_suffix(PLAN.suffix + ".sha256")
        self.assertEqual(sidecar.read_text().split()[0], hashlib.sha256(PLAN.read_bytes()).hexdigest())

    def test_complete_reconciliation_is_byte_immutable(self):
        path = ROOT / "gate2/output/systematic/v1.3/20260816/d05_reconciliation.json"
        before = hashlib.sha256(path.read_bytes()).hexdigest()
        result = reconcile()
        after = hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["completed_runs"], 18)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
