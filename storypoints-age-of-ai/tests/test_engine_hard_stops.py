import copy
import unittest

from simulation.config import load_and_validate
from simulation.engine import run_truth


SCHEMA = "research-design/03b_simulation_schema.json"
EXAMPLE = "simulation/configs/example.yaml"


class EngineHardStopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = load_and_validate(EXAMPLE, SCHEMA)

    def test_fixed_seed_event_hash_is_identical(self):
        first = run_truth(copy.deepcopy(self.base), "world_mixed", seed=101)
        second = run_truth(copy.deepcopy(self.base), "world_mixed", seed=101)
        self.assertEqual(first.digest(), second.digest())

    def test_zero_arrival_creates_no_entities_or_events(self):
        config = copy.deepcopy(self.base)
        config["arrival_models"][0]["parameters"]["count"] = 0
        config["arrival_models"][0]["parameters"]["template_ids"] = []
        result = run_truth(config, "world_sp", seed=7)
        self.assertEqual(result.items, ())
        self.assertEqual(result.events, ())
        self.assertEqual(result.services, ())

    def test_effectively_infinite_capacity_has_zero_queue_wait(self):
        config = copy.deepcopy(self.base)
        config["arrival_models"][0]["parameters"]["spacing"] = 0
        for role in config["role_pools"]:
            role["concurrent_servers"] = 1000
        result = run_truth(config, "world_sp", seed=11)
        waits = [row.service_start - row.queue_enter for row in result.services]
        self.assertTrue(waits)
        self.assertTrue(all(abs(wait) <= 1e-12 for wait in waits))

    def test_no_failure_world_has_no_rework(self):
        config = copy.deepcopy(self.base)
        world = next(w for w in config["data_generating_worlds"] if w["id"] == "world_sp")
        world["truth_parameters"]["gate_fail_probability"] = 0
        world["truth_parameters"]["gate_conditional_probability"] = 0
        result = run_truth(config, "world_sp", seed=13)
        self.assertTrue(all(item.rework_loops == 0 for item in result.items))
        self.assertFalse(any(event.event == "rework" for event in result.events))

    def test_mandatory_failure_cannot_complete_after_loop_limit(self):
        config = copy.deepcopy(self.base)
        config["time_model"]["horizon"] = 1000
        config["arrival_models"][0]["parameters"]["count"] = 1
        config["arrival_models"][0]["parameters"]["template_ids"] = ["standard_feature"]
        world = next(w for w in config["data_generating_worlds"] if w["id"] == "world_sp")
        world["truth_parameters"]["gate_fail_probability"] = 1
        world["truth_parameters"]["gate_conditional_probability"] = 0
        result = run_truth(config, "world_sp", seed=17)
        self.assertEqual(result.items[0].terminal_state, "failed")
        self.assertFalse(any(event.event == "completed" for event in result.events))

    def test_entity_reconciliation(self):
        result = run_truth(copy.deepcopy(self.base), "world_mixed", seed=19)
        terminal = sum(item.terminal_state in {
            "completed", "completed_with_residual_risk", "failed",
            "blocked_dependency_failure", "dependency_failed",
        } for item in result.items)
        censored = sum(item.terminal_state == "censored" for item in result.items)
        self.assertEqual(len(result.items), terminal + censored)

    def test_completed_item_time_is_conserved(self):
        result = run_truth(copy.deepcopy(self.base), "world_sp", seed=23)
        for item in result.items:
            if item.terminal_state != "completed":
                continue
            services = [row for row in result.services if row.item_id == item.item_id]
            waiting = sum(row.service_start - row.queue_enter for row in services)
            service = sum(row.service_end - row.service_start for row in services)
            first_queue = min(
                event.time for event in result.events
                if event.item_id == item.item_id and event.event == "queue_enter"
            )
            dependency_block = max(0.0, first_queue - item.arrival)
            self.assertAlmostEqual(
                item.terminal_time - item.arrival,
                dependency_block + waiting + service,
                places=9,
            )


if __name__ == "__main__":
    unittest.main()
