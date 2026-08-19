import unittest

from simulation.seeds import build_seed_manifest, load_seed_manifest
from simulation.verification import (
    HardStopError,
    check_entity_reconciliation,
    check_fixed_seed_reproducibility,
    check_mandatory_failure,
    check_queue_area_reconciliation,
    check_seed_manifest,
    check_time_accounting,
    run_hard_stop_checks,
)


class SeedTests(unittest.TestCase):
    def test_manifest_is_deterministic_locked_and_disjoint(self):
        one = build_seed_manifest(20260813, 5, 7)
        two = build_seed_manifest(20260813, 5, 7)
        self.assertEqual(one, two)
        self.assertTrue(one.verify())
        self.assertFalse(set(one.development_seeds) & set(one.locked_evaluation_seeds))
        self.assertTrue(check_seed_manifest(one).passed)

    def test_checked_in_locked_manifest_verifies(self):
        manifest = load_seed_manifest("simulation/configs/locked_seed_manifest.json")
        self.assertEqual(len(manifest.development_seeds), 8)
        self.assertEqual(len(manifest.locked_evaluation_seeds), 24)
        self.assertTrue(check_seed_manifest(manifest).passed)


class VerificationTests(unittest.TestCase):
    def test_queue_area_includes_item_still_queued_at_horizon(self):
        events = [
            {"sequence": 1, "time": 0.0, "item_id": "served", "event": "queue_enter",
             "stage_id": "review", "role_pool_id": "reviewers", "detail": "service"},
            {"sequence": 2, "time": 1.0, "item_id": "censored", "event": "queue_enter",
             "stage_id": "review", "role_pool_id": "reviewers", "detail": "service"},
            {"sequence": 3, "time": 2.0, "item_id": "served", "event": "service_start",
             "stage_id": "review", "role_pool_id": "reviewers", "detail": "service"},
        ]
        # Served wait = 2; censored item remains queued from 1 to horizon 5 = 4.
        self.assertTrue(check_queue_area_reconciliation(events, horizon=5.0).passed)

    def test_entity_loss_is_hard_stop(self):
        with self.assertRaises(HardStopError):
            check_entity_reconciliation({"created": 3, "completed": 1, "terminal_failed": 0, "in_system": 1})

    def test_time_mismatch_is_hard_stop(self):
        with self.assertRaises(HardStopError):
            check_time_accounting([{"elapsed": 4, "waiting": 1, "service": 1, "gate": 1, "rework": 0}])

    def test_reproducibility_ignores_mapping_order(self):
        self.assertTrue(check_fixed_seed_reproducibility({"a": 1, "b": 2}, {"b": 2, "a": 1}).passed)

    def test_mandatory_fail_cannot_advance(self):
        trace = [
            {"item_id": "x", "mandatory": True, "gate_state": "Fail"},
            {"item_id": "x", "transition": "advance"},
        ]
        with self.assertRaises(HardStopError):
            check_mandatory_failure(trace)

    def test_complete_hard_stop_bundle(self):
        manifest = build_seed_manifest(42, 2, 2)
        results = run_hard_stop_checks(
            manifest=manifest,
            counts={"created": 2, "completed": 1, "terminal_failed": 0, "in_system": 1},
            time_records=[{"elapsed": 4, "waiting": 1, "service": 2, "gate": 1, "rework": 0}],
            forecasts={"story_points": [0.4], "proposed_model": [0.7]},
            reproducibility_pair=({"events": [1, 2]}, {"events": [1, 2]}),
            toy_cases=[{"observed": 3.0, "expected": 3.0}],
            gate_trace=[{"item_id": "x", "mandatory": True, "gate_state": "Pass", "transition": "advance"}],
        )
        self.assertEqual(len(results), 7)
        self.assertTrue(all(result.passed for result in results))


if __name__ == "__main__":
    unittest.main()
