from __future__ import annotations

import copy
import unittest
from pathlib import Path

from simulation.config import ConfigError, load_and_validate
from simulation.engine import run_truth


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "simulation" / "configs" / "example.yaml"
SCHEMA = ROOT / "research-design/03b_simulation_schema.json"


class ConfigurationTests(unittest.TestCase):
    def test_example_conforms_to_frozen_schema(self):
        cfg = load_and_validate(CONFIG, SCHEMA)
        self.assertEqual(cfg["schema_version"], "0.1.0")
        self.assertEqual(len(cfg["data_generating_worlds"]), 6)
        self.assertEqual(len(cfg["comparators"]), 5)

    def test_cross_reference_failure_is_hard(self):
        cfg = load_and_validate(CONFIG, SCHEMA)
        bad = copy.deepcopy(cfg)
        bad["demand_models"][0]["role_pool_id"] = "missing_role"
        with self.assertRaises(ConfigError):
            from simulation.config import cross_validate
            cross_validate(bad)


class EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = load_and_validate(CONFIG, SCHEMA)

    def test_fixed_seed_is_bit_reproducible(self):
        a = run_truth(self.cfg, "world_mixed", 101)
        b = run_truth(self.cfg, "world_mixed", 101)
        self.assertEqual(a.digest(), b.digest())

    def test_entity_reconciliation_and_monotone_trace(self):
        result = run_truth(self.cfg, "world_sp", 102)
        self.assertEqual(len(result.items), self.cfg["arrival_models"][0]["parameters"]["count"])
        self.assertTrue(all(x.terminal_state in {"completed", "failed", "censored"} for x in result.items))
        self.assertEqual([x.sequence for x in result.events], list(range(1, len(result.events) + 1)))

    def test_immutable_internal_tables_and_plain_adapter(self):
        result = run_truth(self.cfg, "world_readiness", 103)
        self.assertIsInstance(result.events, tuple)
        with self.assertRaises(TypeError):
            result.metadata["seed"] = 7
        tables = result.as_tables()
        self.assertIsInstance(tables["event_log"], list)
        self.assertIsInstance(tables["event_log"][0], dict)

    def test_zero_arrival_toy_case(self):
        cfg = copy.deepcopy(self.cfg)
        cfg["arrival_models"][0]["parameters"]["count"] = 0
        cfg["arrival_models"][0]["parameters"]["template_ids"] = []
        result = run_truth(cfg, "world_sp", 104)
        self.assertEqual(result.items, ())
        self.assertEqual(result.events, ())

    def test_capacity_monotonicity_without_rework(self):
        slow = copy.deepcopy(self.cfg)
        for world in slow["data_generating_worlds"]:
            world["truth_parameters"].update(gate_fail_probability=0, gate_conditional_probability=0)
        fast = copy.deepcopy(slow)
        fast["role_pools"][1]["concurrent_servers"] = 2
        a = run_truth(slow, "world_sp", 105); b = run_truth(fast, "world_sp", 105)
        self.assertLessEqual(max(x.terminal_time or 0 for x in b.items), max(x.terminal_time or 0 for x in a.items))

    def test_hand_calculated_single_item(self):
        cfg = copy.deepcopy(self.cfg)
        cfg["arrival_models"][0]["parameters"].update(count=1, start=0, spacing=0)
        cfg["arrival_models"][0]["parameters"]["template_ids"] = ["standard_feature"]
        stage_values = {"context_preparation": 0.5, "implementation": 1.0,
                        "verification": 0.5, "acceptance": 0.5}
        for demand in cfg["demand_models"]:
            if demand["work_item_selector"] != "standard_feature":
                continue
            value = stage_values[demand["stage_id"]]
            demand["base_distribution"]["family"] = "fixed"
            demand["base_distribution"]["parameters"] = {"value": value}
            demand["base_distribution"].pop("truncation", None)
        for world in cfg["data_generating_worlds"]:
            world["truth_parameters"].update(service_multiplier=1, gate_fail_probability=0, gate_conditional_probability=0)
        result = run_truth(cfg, "world_sp", 106)
        # context 0.5 + implementation 1.0 + verification 0.5 +
        # gate audit 0.5 + acceptance 0.5
        self.assertAlmostEqual(result.items[0].terminal_time, 3.0, places=12)

    def test_mandatory_failure_cannot_advance_after_loop_limit(self):
        cfg = copy.deepcopy(self.cfg)
        cfg["arrival_models"][0]["parameters"].update(count=1, start=0, spacing=0)
        cfg["arrival_models"][0]["parameters"]["template_ids"] = ["standard_feature"]
        cfg["rework_models"][0]["maximum_loops"] = 0
        for world in cfg["data_generating_worlds"]:
            world["truth_parameters"].update(gate_fail_probability=1, gate_conditional_probability=0)
        result = run_truth(cfg, "world_sp", 107)
        self.assertEqual(result.items[0].terminal_state, "failed")
        failure_time = result.items[0].terminal_time
        self.assertFalse(any(e.event == "completed" and e.time >= failure_time for e in result.events))


if __name__ == "__main__":
    unittest.main()
