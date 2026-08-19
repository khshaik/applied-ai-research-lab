"""Adversarial regressions for the executable gate state machine."""
from __future__ import annotations

import copy
import unittest

from simulation.config import cross_validate, load_and_validate
from simulation.engine import GateSemanticsError, run_truth


SCHEMA = "research/design/03b_simulation_schema.json"
EXAMPLE = "simulation/configs/example.yaml"


class GateSemanticsAdversarialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = load_and_validate(EXAMPLE, SCHEMA)

    def one_item(self) -> dict:
        config = copy.deepcopy(self.base)
        config["arrival_models"][0]["parameters"].update(count=1, start=0, spacing=0)
        config["arrival_models"][0]["parameters"]["template_ids"] = ["standard_feature"]
        config["time_model"]["horizon"] = 1000
        return config

    @staticmethod
    def force(config: dict, *, fail: float = 0, conditional: float = 0) -> None:
        for world in config["data_generating_worlds"]:
            world["truth_parameters"].update(
                gate_fail_probability=fail,
                gate_conditional_probability=conditional,
            )

    def test_missing_declared_transition_is_a_hard_error(self):
        config = self.one_item()
        del config["gate_definitions"][0]["transitions"]["Fail"]
        with self.assertRaisesRegex(GateSemanticsError, "lacks transitions"):
            run_truth(config, "world_sp", seed=401)

    def test_conditional_state_cannot_override_conditional_policy(self):
        config = self.one_item()
        config["gate_definitions"][0]["conditional_policy"]["allowed"] = False
        self.force(config, conditional=1)
        with self.assertRaisesRegex(GateSemanticsError, "conditional_policy"):
            run_truth(config, "world_sp", seed=402)

    def test_world_cannot_emit_a_state_excluded_by_allowed_states(self):
        config = self.one_item()
        gate = config["gate_definitions"][0]
        gate["allowed_states"].remove("Conditional")
        del gate["transitions"]["Conditional"]
        self.force(config, conditional=1)
        with self.assertRaisesRegex(GateSemanticsError, "does not allow"):
            run_truth(config, "world_sp", seed=403)

    def test_mandatory_failure_without_rework_cannot_advance(self):
        config = self.one_item()
        config["rework_models"] = []
        config["gate_definitions"][0]["transitions"]["Fail"] = "next"
        self.force(config, fail=1)
        with self.assertRaisesRegex(GateSemanticsError, "failed without rework"):
            run_truth(config, "world_sp", seed=404)

    def test_rework_route_must_match_declared_transition(self):
        config = self.one_item()
        config["gate_definitions"][0]["transitions"]["Fail"] = "terminal_failure"
        self.force(config, fail=1)
        with self.assertRaisesRegex(GateSemanticsError, "rework route selected"):
            run_truth(config, "world_sp", seed=405)

    def test_non_applicable_gate_is_explicit_and_consumes_no_gate_service(self):
        config = self.one_item()
        gate = config["gate_definitions"][0]
        gate["mandatory"] = False
        gate["allowed_states"].append("NotApplicable")
        gate["transitions"]["NotApplicable"] = "next"
        config["work_item_templates"][0]["required_gate_ids"] = []
        cross_validate(config)
        result = run_truth(config, "world_sp", seed=406)
        self.assertEqual([row.decision for row in result.gates], ["NotApplicable"])
        self.assertEqual(result.gates[0].rationale,
                         "excluded_by_frozen_risk_and_template_applicability_rule")
        self.assertEqual(result.items[0].terminal_state, "completed")
        self.assertFalse(any(row.kind == "gate" for row in result.services))

    def test_non_applicable_gate_requires_explicit_not_applicable_semantics(self):
        config = self.one_item()
        config["gate_definitions"][0]["mandatory"] = False
        config["work_item_templates"][0]["required_gate_ids"] = []
        with self.assertRaisesRegex(GateSemanticsError, "explicitly allow NotApplicable"):
            run_truth(config, "world_sp", seed=407)

    def test_required_gate_outside_risk_scope_is_rejected(self):
        config = self.one_item()
        config["gate_definitions"][0]["risk_classes"] = ["T4"]
        with self.assertRaisesRegex(GateSemanticsError, "outside its risk scope"):
            run_truth(config, "world_sp", seed=408)

    def test_missing_required_evidence_forces_failure(self):
        config = self.one_item()
        config["readiness_models"][0]["t0_state"]["test_evidence"] = "missing"
        # Production occurs only after this gate, so the gate cannot invent it.
        config["evidence_definitions"][0]["producer_stage_id"] = "acceptance" if any(
            stage["id"] == "acceptance" for stage in config["lifecycle_stages"]
        ) else "implementation"
        config["rework_models"] = []
        config["gate_definitions"][0]["transitions"]["Fail"] = "terminal_failure"
        self.force(config)
        result = run_truth(config, "world_sp", seed=409)
        self.assertEqual(result.items[0].terminal_state, "failed")
        self.assertTrue(any(row.event == "evidence_not_ready" for row in result.events))

    def test_present_same_run_evidence_allows_pass(self):
        config = self.one_item()
        self.force(config)
        result = run_truth(config, "world_sp", seed=410)
        self.assertEqual(result.items[0].terminal_state, "completed")
        self.assertFalse(any(row.event == "evidence_not_ready" for row in result.events))

    def test_rework_invalidates_evidence_before_next_gate_attempt(self):
        config = self.one_item()
        config["rework_models"][0]["maximum_loops"] = 1
        self.force(config, fail=1)
        result = run_truth(config, "world_sp", seed=411)
        self.assertEqual(result.items[0].terminal_state, "failed")
        self.assertTrue(any(row.event == "evidence_invalidated" for row in result.events))
        invalidated = next(i for i, row in enumerate(result.events) if row.event == "evidence_invalidated")
        regenerated = next(i for i, row in enumerate(result.events)
                           if i > invalidated and row.event == "evidence_produced")
        self.assertGreater(regenerated, invalidated)

    def test_missing_evidence_is_produced_only_at_declared_service_completion(self):
        config = self.one_item()
        config["readiness_models"][0]["t0_state"]["test_evidence"] = "absent"
        self.force(config)
        result = run_truth(config, "world_sp", seed=415)
        produced = next(row for row in result.events if row.event == "evidence_produced")
        self.assertEqual(produced.stage_id, "verification")
        self.assertLess(
            next(i for i, row in enumerate(result.events) if row.event == "evidence_produced"),
            next(i for i, row in enumerate(result.events) if row.event == "service_start" and row.detail == "gate"),
        )
        self.assertEqual(result.items[0].terminal_state, "completed")

    def test_conditional_completion_has_distinct_state_and_residual_risk(self):
        config = self.one_item()
        self.force(config, conditional=1)
        result = run_truth(config, "world_sp", seed=416)
        item = result.items[0]
        self.assertEqual(item.terminal_state, "completed_with_residual_risk")
        self.assertIsNotNone(item.residual_risk_id)
        self.assertEqual(result.gates[-1].residual_risk_id, item.residual_risk_id)
        self.assertTrue(any(row.event == "residual_risk_recorded" for row in result.events))

    def test_evidence_requires_declared_producer(self):
        config = self.one_item()
        del config["evidence_definitions"][0]["producer_stage_id"]
        with self.assertRaisesRegex(GateSemanticsError, "producer_stage_id"):
            run_truth(config, "world_sp", seed=417)

    def test_unsupported_freshness_rule_is_a_hard_error(self):
        config = self.one_item()
        config["evidence_definitions"][0]["freshness_rule"] = "within_30_days"
        with self.assertRaisesRegex(GateSemanticsError, "unsupported freshness rule"):
            run_truth(config, "world_sp", seed=412)

    def test_unsupported_expiry_rule_is_a_hard_error(self):
        config = self.one_item()
        config["gate_definitions"][0]["expiry_rule"] = "expire_after_24h"
        with self.assertRaisesRegex(GateSemanticsError, "unsupported expiry rule"):
            run_truth(config, "world_sp", seed=413)

    def test_unsupported_readiness_runtime_declaration_is_a_hard_error(self):
        config = self.one_item()
        config["readiness_models"][0]["runtime_state_model"]["refresh_after_stage"] = "verification"
        with self.assertRaisesRegex(GateSemanticsError, "unsupported readiness runtime"):
            run_truth(config, "world_sp", seed=414)


if __name__ == "__main__":
    unittest.main()
