from __future__ import annotations

import copy
import unittest
from pathlib import Path

from simulation.config import ConfigError, cross_validate, load_and_validate, validate_config


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "simulation" / "configs" / "example.yaml"
SCHEMA = ROOT / "research-design/03b_simulation_schema.json"


class DependencyFreeSchemaValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.valid = load_and_validate(CONFIG, SCHEMA)

    def assert_schema_rejects(self, mutate) -> None:
        candidate = copy.deepcopy(self.valid)
        mutate(candidate)
        with self.assertRaises(ConfigError):
            validate_config(candidate, SCHEMA)

    def test_maximum_rejects_pdd_level_99(self):
        self.assert_schema_rejects(
            lambda c: c["work_item_templates"][0]["pdd_profile"]["iu"].update(level=99)
        )

    def test_maximum_rejects_route_probability_above_one(self):
        self.assert_schema_rejects(
            lambda c: c["rework_models"][0]["routes"][0].update(probability=1.7)
        )

    def test_date_time_format_requires_valid_timestamp_and_offset(self):
        for invalid in ("not-a-date", "2026-08-13T12:00:00"):
            with self.subTest(invalid=invalid):
                candidate = copy.deepcopy(self.valid)
                candidate["study_manifest"]["created_at"] = invalid
                with self.assertRaises(ConfigError):
                    validate_config(candidate, SCHEMA)

    def test_nonfinite_schema_number_is_rejected(self):
        self.assert_schema_rejects(lambda c: c["time_model"].update(horizon=float("nan")))

    def test_schema_rejects_out_of_scope_mechanism_declarations(self):
        mutations = {
            "non-FIFO": lambda c: c["role_pools"][0].update(queue_discipline="risk_priority"),
            "preemption": lambda c: c["role_pools"][0].update(preemption_policy="resume"),
            "numeric backlog": lambda c: c["role_pools"][0].update(initial_backlog=1),
            "parallel stage": lambda c: c["lifecycle_stages"][0].update(parallelization_policy="parallel"),
            "non-fixed arrival": lambda c: c["arrival_models"][0].update(type="renewal"),
            "mixture distribution": lambda c: c["demand_models"][0]["base_distribution"].update(family="mixture"),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                self.assert_schema_rejects(mutate)


class SemanticInvariantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.valid = load_and_validate(CONFIG, SCHEMA)

    def assert_cross_rejects(self, mutate) -> None:
        candidate = copy.deepcopy(self.valid)
        mutate(candidate)
        with self.assertRaises(ConfigError):
            cross_validate(candidate)

    def test_world_failure_probability_above_one_is_rejected(self):
        self.assert_cross_rejects(
            lambda c: c["data_generating_worlds"][0]["truth_parameters"].update(gate_fail_probability=1.7)
        )

    def test_world_outcome_probabilities_cannot_sum_above_one(self):
        def mutate(candidate):
            candidate["data_generating_worlds"][0]["truth_parameters"].update(
                gate_fail_probability=0.7, gate_conditional_probability=0.4
            )

        self.assert_cross_rejects(mutate)

    def test_negative_duration_parameter_is_rejected(self):
        self.assert_cross_rejects(
            lambda c: c["demand_models"][0]["base_distribution"]["parameters"].update(low=-0.1)
        )

    def test_invalid_triangular_order_is_rejected(self):
        self.assert_cross_rejects(
            lambda c: c["demand_models"][0]["base_distribution"]["parameters"].update(mode=5)
        )

    def test_semantics_reject_ignored_initial_state_and_setup_declarations(self):
        mutations = {
            "initial WIP": lambda c: c["arrival_models"][0]["initial_wip"].append({"id": "work"}),
            "setup penalty": lambda c: c["role_pools"][0].update(setup_penalty_distribution_id="implementation_time"),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                self.assert_cross_rejects(mutate)

    def test_unknown_references_and_destinations_are_rejected(self):
        mutations = {
            "role capacity calendar": lambda c: c["role_pools"][0].update(capacity_calendar_id="unknown"),
            "stage role": lambda c: c["lifecycle_stages"][0]["eligible_role_pool_ids"].append("unknown"),
            "stage gate": lambda c: c["lifecycle_stages"][1].update(gate_id="unknown"),
            "gate evidence": lambda c: c["gate_definitions"][0]["required_evidence_ids"].append("unknown"),
            "gate distribution": lambda c: c["gate_definitions"][0].update(evaluation_demand_distribution_id="unknown"),
            "gate transition destination": lambda c: c["gate_definitions"][0]["transitions"].update(Fail="unknown"),
            "template gate": lambda c: c["work_item_templates"][0]["required_gate_ids"].append("unknown"),
            "demand template": lambda c: c["demand_models"][0].update(work_item_selector="unknown"),
            "demand provenance": lambda c: c["demand_models"][0].update(provenance_id="unknown"),
            "rework gate": lambda c: c["rework_models"][0].update(from_gate_id="unknown"),
            "rework destination": lambda c: c["rework_models"][0]["routes"][0].update(destination_stage_id="unknown"),
            "development world": lambda c: c["experimental_design"]["development_world_ids"].append("unknown"),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                self.assert_cross_rejects(mutate)

    def test_duplicate_distribution_ids_are_rejected(self):
        self.assert_cross_rejects(
            lambda c: c["demand_models"][2]["base_distribution"].update(id="implementation_time")
        )

    def test_dependency_edges_require_known_template_endpoints(self):
        def mutate(candidate):
            candidate["dependency_models"] = [{
                "id": "feature_dependencies",
                "edges": [["feature_template", "unknown_template"]],
                "cycles_allowed_for_test": False,
            }]

        self.assert_cross_rejects(mutate)

    def test_dependency_edge_endpoint_must_be_an_id(self):
        def mutate(candidate):
            candidate["dependency_models"] = [{
                "id": "feature_dependencies",
                "edges": [["feature_template", 17]],
                "cycles_allowed_for_test": False,
            }]

        candidate = copy.deepcopy(self.valid)
        mutate(candidate)
        with self.assertRaises(ConfigError):
            validate_config(candidate, SCHEMA)

    def test_stage_gate_link_must_match_gate_stage(self):
        self.assert_cross_rejects(
            lambda c: c["gate_definitions"][0].update(stage_id="implementation")
        )

    def test_gate_stage_requires_reciprocal_stage_link(self):
        self.assert_cross_rejects(
            lambda c: next(stage for stage in c["lifecycle_stages"] if stage["id"] == "verification").update(gate_id=None)
        )

    def test_every_allowed_gate_state_requires_a_transition(self):
        def mutate(candidate):
            del candidate["gate_definitions"][0]["transitions"]["Conditional"]

        self.assert_cross_rejects(mutate)

    def test_allowed_gate_states_must_be_unique(self):
        self.assert_cross_rejects(
            lambda c: c["gate_definitions"][0]["allowed_states"].append("Pass")
        )

    def test_invalid_time_and_capacity_domains_are_rejected(self):
        mutations = {
            "warmup after horizon": lambda c: c["time_model"].update(warmup=81),
            "arrival duration": lambda c: c["arrival_models"][0]["parameters"].update(spacing=-1),
            "capacity effective": lambda c: c["capacity_calendars"][0]["intervals"][0].update(effective_hours=81),
            "capacity interval order": lambda c: c["capacity_calendars"][0]["intervals"][0].update(end="2026-08-12T00:00:00Z"),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                self.assert_cross_rejects(mutate)


if __name__ == "__main__":
    unittest.main()
