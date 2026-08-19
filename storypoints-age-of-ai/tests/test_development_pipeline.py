import json
import copy
import tempfile
import unittest
from pathlib import Path

from simulation.config import load_and_validate
from simulation.development_pipeline import (
    DevelopmentScenario,
    comparator_input,
    configure_scenario,
    run_development_pipeline,
)
from simulation.engine import run_truth


ROOT = Path(__file__).resolve().parents[1]


class DevelopmentPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = load_and_validate(ROOT / "simulation/configs/example.yaml", ROOT / "research-design/03b_simulation_schema.json")

    def test_rejects_locked_evaluation_world(self):
        scenario = DevelopmentScenario("forbidden", "world_mixed", "test", {}, "must fail")
        with self.assertRaisesRegex(ValueError, "non-development world"):
            configure_scenario(self.config, scenario)

    def test_adapter_separates_runtime_truth_fields(self):
        scenario = DevelopmentScenario("unit", "world_sp", "test", {}, "adapter")
        config = configure_scenario(self.config, scenario)
        result = run_truth(config, "world_sp", seed=7)
        item = comparator_input(config, "world_sp", result, 0.5)
        self.assertEqual(item["true_completion_probability"], 0.5)
        self.assertEqual(set(item["role_demand"]), set(item["role_capacity"]))
        self.assertTrue(all(value > 0 for value in item["role_capacity"].values()))
        self.assertIn("role_stage_demand", item)
        self.assertIn("dependency_block_probability", item)

    def test_adapter_capacity_uses_open_calendar_minus_blackout(self):
        scenario = DevelopmentScenario("calendar", "world_sp", "test", {}, "calendar adapter")
        config = configure_scenario(self.config, scenario)
        calendar = config["capacity_calendars"][0]
        calendar["blackout_periods"] = [{
            "start": "2026-08-13T10:00:00Z",
            "end": "2026-08-13T20:00:00Z",
        }]
        result = run_truth(config, "world_sp", seed=8)
        item = comparator_input(config, "world_sp", result, 0.5)
        roles = {role["id"]: role for role in config["role_pools"]}
        # The explicit window and horizon are 80h; the blackout removes 10h.
        self.assertEqual(item["role_capacity"]["developers"],
                         70 * roles["developers"]["concurrent_servers"])

    def test_adapter_nonoracle_fields_do_not_depend_on_runtime_result(self):
        scenario = DevelopmentScenario("isolation", "world_sp", "test", {}, "boundary")
        config = configure_scenario(self.config, scenario)
        first_result = run_truth(config, "world_sp", seed=9)
        second_result = run_truth(config, "world_sp", seed=10)
        first = comparator_input(config, "world_sp", first_result, 0.2)
        second = comparator_input(config, "world_sp", second_result, 0.8)
        runtime_fields = {"true_completion_probability", "true_role_load"}
        self.assertEqual({k: v for k, v in first.items() if k not in runtime_fields},
                         {k: v for k, v in second.items() if k not in runtime_fields})

    def test_pipeline_is_deterministic_and_marks_outputs_developmental(self):
        scenarios = (DevelopmentScenario("tiny", "world_sp", "test", {"arrival_count": 3}, "fast fixture"),)
        with tempfile.TemporaryDirectory() as left, tempfile.TemporaryDirectory() as right:
            a = run_development_pipeline(self.config, left, replications=2, scenarios=scenarios)
            b = run_development_pipeline(self.config, right, replications=2, scenarios=scenarios)
            self.assertEqual([r["digest"] for r in a["run_rows"]], [r["digest"] for r in b["run_rows"]])
            manifest = json.loads((Path(left) / "development_manifest.json").read_text())
            self.assertFalse(manifest["seed_policy"]["locked_evaluation_seeds_accessed"])
            self.assertEqual(manifest["status"], "developmental_synthetic")
            self.assertTrue((Path(left) / "comparator_scores.csv").exists())
            self.assertEqual(set(manifest["output_sha256"]), set(manifest["outputs"]))
            self.assertEqual(manifest["manifest_version"], "0.2.0-development")
            self.assertEqual(
                set(manifest["provenance"]["source_file_sha256"]),
                {
                    "comparators.py", "config.py", "development_pipeline.py",
                    "engine.py", "evaluation.py", "scheduling.py", "seeds.py",
                },
            )
            self.assertEqual(
                a["manifest"]["provenance"], b["manifest"]["provenance"]
            )


if __name__ == "__main__":
    unittest.main()
