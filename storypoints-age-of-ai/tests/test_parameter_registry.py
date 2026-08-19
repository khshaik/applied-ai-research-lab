import copy
import unittest

from simulation.config import load_and_validate
from simulation.parameter_registry import (
    ParameterProvenanceError,
    active_parameter_paths,
    audit_by_intended_use,
    check_parameter_registry,
    load_registry,
)
from tests.test_evidence_review_workflow import complete_bundle


class ParameterRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = load_and_validate("simulation/configs/example.yaml", "03b_simulation_schema.json")
        cls.registry = load_registry("simulation/configs/parameter_registry.json")

    def test_every_active_parameter_has_exactly_one_development_record(self):
        active = active_parameter_paths(self.config)
        checks = check_parameter_registry(self.config, self.registry, use="development_simulation")
        self.assertEqual(len(active), 102)
        self.assertEqual({check.path for check in checks}, set(active))
        self.assertTrue(all(check.permitted for check in checks))

    def test_illustrative_values_hard_stop_production_calibration(self):
        with self.assertRaisesRegex(ParameterProvenanceError, "production_calibration"):
            check_parameter_registry(self.config, self.registry, use="production_calibration")
        audit = audit_by_intended_use(self.config, self.registry)
        self.assertEqual(audit["development_status"], "permitted_illustrative")
        self.assertEqual(audit["production_calibration_status"], "hard_stop")
        self.assertIn("PR-DEMAND", audit["production_blocking_registry_ids"])

    def test_unregistered_active_parameter_and_overlapping_pattern_fail_closed(self):
        missing = copy.deepcopy(self.registry)
        missing["records"] = [r for r in missing["records"] if r["id"] != "PR-TIME"]
        with self.assertRaisesRegex(ParameterProvenanceError, "exactly one registry match, got 0"):
            check_parameter_registry(self.config, missing, use="development_simulation")
        duplicate = copy.deepcopy(self.registry)
        cloned = copy.deepcopy(duplicate["records"][0]); cloned["id"] = "duplicate-time"
        duplicate["records"].append(cloned)
        with self.assertRaisesRegex(ParameterProvenanceError, "exactly one registry match, got 2"):
            check_parameter_registry(self.config, duplicate, use="development_simulation")

    def test_empirical_promotion_requires_confirmed_extraction_and_transform_audit(self):
        config = {"time_model": {"horizon": 1.0}}
        record = {"id": "empirical", "path_pattern": "time_model.*", "provenance_class": "E1",
                  "parameter_kind": "calibration", "source_id": "family-f1", "source_locator": "Methods",
                  "original_measure": "one hour", "transformation": "identity",
                  "applicability_limits": "synthetic test only",
                  "permitted_uses": ["development_simulation", "production_calibration"],
                  "approval_status": "verified_executable", "evidence_extraction_id": "x1",
                  "transformation_audit": {"status": "confirmed", "formula": "x",
                                            "input_unit": "hours", "output_unit": "hours",
                                            "verifier_agent_id": "transform-agent",
                                            "accountable_author_id": "author-1"}}
        registry = {"records": [record]}
        with self.assertRaisesRegex(ParameterProvenanceError, "forbids production_calibration"):
            check_parameter_registry(config, registry, use="production_calibration")
        checks = check_parameter_registry(config, registry, use="production_calibration",
                                          evidence_bundle=complete_bundle())
        self.assertTrue(all(check.permitted for check in checks))


if __name__ == "__main__": unittest.main()
