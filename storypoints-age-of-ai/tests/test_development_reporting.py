import tempfile
import unittest
from pathlib import Path

from simulation.development_reporting import publish_report, summarize_item_forecasts


class DevelopmentReportingTests(unittest.TestCase):
    def rows(self):
        rows = []
        for run_id, outcomes in (("run-a", (1, 0)), ("run-b", (1, 1)), ("run-c", (0, 0))):
            for index, outcome in enumerate(outcomes):
                rows.append({
                    "status": "developmental_synthetic",
                    "scenario_id": "scenario-a",
                    "run_id": run_id,
                    "item_id": f"{run_id}-{index}",
                    "outcome_completed": str(outcome),
                    "story_points": "0.5",
                    "hie_compatible": "0.6",
                    "simple_role_load": "0.4",
                    "proposed_model": "0.7",
                    "oracle": str(float(outcome)),
                })
        return rows

    def test_cluster_bootstrap_is_deterministic_and_keeps_oracle_diagnostic(self):
        first = summarize_item_forecasts(self.rows(), bootstrap_replications=200)
        second = summarize_item_forecasts(self.rows(), bootstrap_replications=200)
        self.assertEqual(first, second)
        model_rows, scenario_rows = first
        self.assertEqual(len(model_rows), 5)
        self.assertEqual(len(scenario_rows), 1)
        oracle = next(row for row in model_rows if row["model"] == "oracle")
        self.assertEqual(oracle["deployable"], "false")
        self.assertEqual(oracle["brier_score"], 0.0)

    def test_rejects_non_development_rows_and_small_bootstrap(self):
        rows = self.rows()
        rows[0]["status"] = "locked"
        with self.assertRaisesRegex(ValueError, "developmental"):
            summarize_item_forecasts(rows, bootstrap_replications=200)
        with self.assertRaisesRegex(ValueError, "100"):
            summarize_item_forecasts(self.rows(), bootstrap_replications=99)


if __name__ == "__main__":
    unittest.main()
