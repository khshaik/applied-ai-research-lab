from __future__ import annotations

import copy
import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from simulation.locked_runner import (
    BatchResult,
    LockedRunRefusal,
    adjudicate_gate4b,
    build_output_payloads,
    build_readiness_record,
    collect_batches,
    execute_locked,
    precision_summary,
    protocol_digest,
    publish_outputs,
)
from test_prelock import LOCKED_WORLDS, protocol_fixture


def item_rows(replication: int) -> tuple[dict, ...]:
    rows = []
    for world in LOCKED_WORLDS:
        for model, probability in (("story_points", 0.55), ("hie_compatible", 0.60),
                                   ("simple_role_load", 0.65), ("proposed_model", 0.85)):
            rows.append({"world_id": world, "replication_id": replication,
                         "item_id": f"item-{replication}", "terminal_state": "completed",
                         "outcome_completed": 1,
                         "model": model, "probability": probability})
    return tuple(rows)


class LockedRunnerTests(unittest.TestCase):
    def test_strict_primary_mapping_rejects_mismatch_and_incomplete_mapping(self):
        with tempfile.TemporaryDirectory() as directory:
            protocol = protocol_fixture(Path(directory))
            rows = list(item_rows(0))
            rows[0] = {**rows[0], "terminal_state": "completed_with_residual_risk",
                       "outcome_completed": 1}
            manifest = tuple({"protocol_sha256": "p", "code_sha256": "c", "config_sha256": "f",
                              "seed_manifest_sha256": "s", "world_id": world, "replication_id": 0,
                              "run_id": world, "digest": "d", "status": "locked"} for world in LOCKED_WORLDS)
            robustness = ({"configuration_id": "base", "contrast": "primary", "direction": 1,
                           "reversal": False, "within_plausible_region": True},)
            batch = BatchResult(manifest, tuple(rows), (0.05,), robustness, (0.5,), (0.12,))
            primary = {**precision_summary([0.5, 0.5]), "contrast": "primary_endpoint",
                       "precision_target": 0.01, "precision_resolved": True}
            contrast = {**precision_summary([0.05, 0.05]), "contrast": "proposed_vs_strongest_deployable",
                        "precision_target": 0.001, "precision_resolved": True}
            uncertainty = {"primary": primary, "contrast": contrast, "precision_resolved": True,
                           "status": "resolved", "replications": 2}
            with self.assertRaisesRegex(LockedRunRefusal, "strict primary"):
                build_output_payloads(protocol, [batch], uncertainty)
            protocol["evaluation_design"]["primary_outcome_mapping"]["non_event"].remove("censored")
            fixed = tuple({**row, "outcome_completed": 0} if row["terminal_state"] == "completed_with_residual_risk"
                          else row for row in rows)
            with self.assertRaisesRegex(LockedRunRefusal, "complete and exact"):
                build_output_payloads(protocol, [BatchResult(manifest, fixed, (0.05,), robustness,
                                                              (0.5,), (0.12,))], uncertainty)

    def test_conditional_inclusive_sensitivity_is_mandatory_and_cannot_change_primary(self):
        with tempfile.TemporaryDirectory() as directory:
            protocol = protocol_fixture(Path(directory))
            rows = list(item_rows(0))
            rows = [{**row, "terminal_state": "completed_with_residual_risk", "outcome_completed": 0}
                    if row["world_id"] == LOCKED_WORLDS[0] else row for row in rows]
            manifest = tuple({"protocol_sha256": "p", "code_sha256": "c", "config_sha256": "f",
                              "seed_manifest_sha256": "s", "world_id": world, "replication_id": 0,
                              "run_id": world, "digest": "d", "status": "locked"} for world in LOCKED_WORLDS)
            robustness = tuple({"configuration_id": f"c{i}", "contrast": "primary", "direction": 1,
                                "reversal": False, "within_plausible_region": True} for i in range(5))
            batch = BatchResult(manifest, tuple(rows), (0.05,), robustness, (0.5,), (0.12,))
            primary = {**precision_summary([0.5, 0.5]), "contrast": "primary_endpoint",
                       "precision_target": 0.01, "precision_resolved": True}
            contrast = {**precision_summary([0.05, 0.05]), "contrast": "proposed_vs_strongest_deployable",
                        "precision_target": 0.001, "precision_resolved": True}
            payloads = build_output_payloads(protocol, [batch], {"primary": primary, "contrast": contrast,
                                             "precision_resolved": True, "status": "resolved", "replications": 2})
            report = payloads["conditional_completion_inclusive"]
            self.assertEqual(report["analysis_id"], "conditional_completion_inclusive")
            self.assertIn("brier_scores", report); self.assertIn("paired_contrast", report)
            self.assertTrue(report["calibration"]); self.assertIn("threshold_checks", report)
            self.assertTrue(report["primary_adjudication_unchanged"])
            self.assertEqual(report["primary_result_snapshot"], payloads["adjudication"]["primary_result"])
            # Strict output remains non-event while sensitivity treats residual-risk completion as event.
            primary_rows = [row for row in payloads["item_forecasts"]
                            if row["world_id"] == LOCKED_WORLDS[0]]
            self.assertTrue(all(row["outcome_completed"] == 0 for row in primary_rows))

    def test_every_gate4b_threshold_is_independently_mandatory(self):
        with tempfile.TemporaryDirectory() as directory:
            protocol = protocol_fixture(Path(directory))
            baseline = dict(relative_skill=0.05, absolute_improvement=0.01,
                            contrast_ci_lower=0.001, precision_resolved=True,
                            robustness_fraction=0.80, bottleneck_improvement=0.10)
            self.assertTrue(all(adjudicate_gate4b(protocol, **baseline).values()))
            failures = {
                "relative_brier_skill_pass": ("relative_skill", 0.049),
                "absolute_improvement_pass": ("absolute_improvement", 0.009),
                "ci_excludes_zero_pass": ("contrast_ci_lower", 0.0),
                "precision_pass": ("precision_resolved", False),
                "robustness_pass": ("robustness_fraction", 0.79),
                "bottleneck_improvement_pass": ("bottleneck_improvement", 0.09),
            }
            for check, (field, value) in failures.items():
                values = dict(baseline); values[field] = value
                self.assertFalse(adjudicate_gate4b(protocol, **values)[check], check)

    def test_draft_protocol_refuses_before_executor_invocation(self):
        called = False

        def executor(worlds, start, count):
            nonlocal called
            called = True
            raise AssertionError("must not be invoked")

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "draft.json"
            path.write_text(json.dumps({"status": "draft_prelock"}), encoding="utf-8")
            with self.assertRaises(LockedRunRefusal):
                execute_locked(path, directory, executor)
        self.assertFalse(called)

    def test_precision_batches_stop_at_first_eligible_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            protocol = protocol_fixture(Path(directory))
            protocol["decision_rules"]["smallest_effect_of_interest"] = {"absolute_brier_improvement": 0.01}
            protocol["precision"].update(
                minimum_replications=4, maximum_replications=10,
                replication_batch_size=2, primary_ci_half_width_max=0.01,
                contrast_ci_half_width_fraction_of_seoi=0.10,
            )
            calls = []

            def executor(worlds, start, count):
                calls.append((tuple(worlds), start, count))
                return BatchResult((), (), tuple(0.02 for _ in range(count)), (),
                                   tuple(0.5 for _ in range(count)), tuple(0.12 for _ in range(count)))

            batches, summary = collect_batches(protocol, executor)
            self.assertEqual(len(batches), 2)
            self.assertEqual([call[1:] for call in calls], [(0, 2), (2, 2)])
            self.assertTrue(summary["precision_resolved"])
            self.assertEqual(summary["replications"], 4)
            self.assertTrue(summary["primary"]["precision_resolved"])
            self.assertTrue(summary["contrast"]["precision_resolved"])

    def test_unresolved_precision_stops_exactly_at_maximum(self):
        with tempfile.TemporaryDirectory() as directory:
            protocol = protocol_fixture(Path(directory))
            protocol["decision_rules"]["smallest_effect_of_interest"] = {"absolute_brier_improvement": 0.01}
            protocol["precision"].update(minimum_replications=2, maximum_replications=5,
                                          replication_batch_size=2)
            supplied = iter((0.0, 1.0, 0.0, 1.0, 0.0))

            def executor(worlds, start, count):
                values = tuple(next(supplied) for _ in range(count))
                return BatchResult((), (), values, (), values, tuple(0.12 for _ in range(count)))

            _, summary = collect_batches(protocol, executor)
            self.assertEqual(summary["replications"], 5)
            self.assertEqual(summary["status"], "precision_unresolved")

    def test_executor_batch_size_mismatch_is_a_hard_stop(self):
        with tempfile.TemporaryDirectory() as directory:
            protocol = protocol_fixture(Path(directory))
            protocol["decision_rules"]["smallest_effect_of_interest"] = {"absolute_brier_improvement": 0.01}
            with self.assertRaisesRegex(LockedRunRefusal, "contrast count"):
                collect_batches(protocol, lambda worlds, start, count: BatchResult((), (), (0.1,), (), (0.5,), (0.1,)))

    def test_output_payloads_include_calibration_and_uncertainty(self):
        with tempfile.TemporaryDirectory() as directory:
            protocol = protocol_fixture(Path(directory))
            manifest = tuple({"protocol_sha256": protocol_digest(protocol), "code_sha256": "c", "config_sha256": "f",
                              "seed_manifest_sha256": "s", "world_id": world,
                              "replication_id": 0, "run_id": f"r-{world}", "digest": "d", "status": "locked"}
                             for world in LOCKED_WORLDS)
            robustness = tuple({"configuration_id": f"c{i}", "contrast": "primary", "direction": 1,
                                "reversal": False, "within_plausible_region": True} for i in range(5))
            batch = BatchResult(manifest, item_rows(0), (0.05,), robustness, (0.5,), (0.12,))
            primary = {**precision_summary([0.5, 0.5]), "contrast": "primary_endpoint",
                       "precision_target": 0.01, "precision_resolved": True}
            contrast = {**precision_summary([0.05, 0.05]), "contrast": "proposed_vs_strongest_deployable",
                        "precision_target": 0.001, "precision_resolved": True}
            uncertainty = {"primary": primary, "contrast": contrast, "precision_resolved": True,
                           "status": "resolved", "replications": 2}
            payloads = build_output_payloads(protocol, [batch], uncertainty)
            self.assertEqual(set(payloads), {record["id"] for record in protocol["output_contract"]})
            self.assertTrue(payloads["calibration"])
            self.assertEqual(len(payloads["monte_carlo_uncertainty"]), 2)
            self.assertTrue(payloads["adjudication"]["success_convention"])

    def test_immutable_publication_refuses_existing_target(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol = protocol_fixture(root)
            manifest = tuple({"protocol_sha256": protocol_digest(protocol), "code_sha256": "c", "config_sha256": "f",
                              "seed_manifest_sha256": "s", "world_id": world, "replication_id": 0,
                              "run_id": f"r-{world}", "digest": "d", "status": "locked"} for world in LOCKED_WORLDS)
            robustness = tuple({"configuration_id": f"c{i}", "contrast": "primary", "direction": 1,
                                "reversal": False, "within_plausible_region": True} for i in range(5))
            batch = BatchResult(manifest, item_rows(0), (0.05,), robustness, (0.5,), (0.12,))
            primary = {**precision_summary([0.5, 0.5]), "contrast": "primary_endpoint",
                       "precision_target": 0.01, "precision_resolved": True}
            contrast = {**precision_summary([0.05, 0.05]), "contrast": "proposed_vs_strongest_deployable",
                        "precision_target": 0.001, "precision_resolved": True}
            payloads = build_output_payloads(protocol, [batch], {"primary": primary, "contrast": contrast,
                                             "precision_resolved": True, "status": "resolved", "replications": 2})
            for record in protocol["output_contract"]:
                if record["id"] == "publication_receipt":
                    record["required_fields"] = ["status", "contract_ids", "files",
                                                 "key_reconciliation", "receipt_sha256"]
                else:
                    payload = payloads[record["id"]]
                    record["required_fields"] = list(payload[0] if isinstance(payload, list) else payload)
            locked_digest = protocol_digest(protocol)
            for row in payloads["run_manifest"]:
                row["protocol_sha256"] = locked_digest
            receipt = publish_outputs(protocol, root, payloads)
            self.assertEqual(receipt["status"], "verified")
            for record in protocol["output_contract"]:
                self.assertTrue((root / record["path"]).is_file())
            with self.assertRaisesRegex(LockedRunRefusal, "directory already exists"):
                publish_outputs(protocol, root, payloads)

    def test_publication_failure_leaves_no_partial_output_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol = protocol_fixture(root)
            manifest = tuple({"protocol_sha256": "", "code_sha256": "c", "config_sha256": "f",
                              "seed_manifest_sha256": "s", "world_id": world, "replication_id": 0,
                              "run_id": f"r-{world}", "digest": "d", "status": "locked"} for world in LOCKED_WORLDS)
            robustness = tuple({"configuration_id": f"c{i}", "contrast": "primary", "direction": 1,
                                "reversal": False, "within_plausible_region": True} for i in range(5))
            batch = BatchResult(manifest, item_rows(0), (0.05,), robustness, (0.5,), (0.12,))
            primary = {**precision_summary([0.5, 0.5]), "contrast": "primary_endpoint",
                       "precision_target": 0.01, "precision_resolved": True}
            contrast = {**precision_summary([0.05, 0.05]), "contrast": "proposed_vs_strongest_deployable",
                        "precision_target": 0.001, "precision_resolved": True}
            payloads = build_output_payloads(protocol, [batch], {"primary": primary, "contrast": contrast,
                                             "precision_resolved": True, "status": "resolved", "replications": 2})
            for record in protocol["output_contract"]:
                payload = payloads[record["id"]]
                record["required_fields"] = (["status", "contract_ids", "files", "key_reconciliation", "receipt_sha256"]
                                             if record["id"] == "publication_receipt"
                                             else list(payload[0] if isinstance(payload, list) else payload))
            for row in payloads["run_manifest"]:
                row["protocol_sha256"] = protocol_digest(protocol)
            from simulation import locked_runner
            original = locked_runner._write_payload
            calls = 0

            def fail_second(path, record, payload):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("injected staging failure")
                original(path, record, payload)

            with patch.object(locked_runner, "_write_payload", side_effect=fail_second):
                with self.assertRaisesRegex(OSError, "injected"):
                    publish_outputs(protocol, root, payloads)
            self.assertFalse((root / "simulation/output/locked").exists())

    def test_key_reconciliation_rejects_incomplete_model_grid_before_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol = protocol_fixture(root)
            manifest = tuple({"protocol_sha256": "", "code_sha256": "c", "config_sha256": "f",
                              "seed_manifest_sha256": "s", "world_id": world, "replication_id": 0,
                              "run_id": f"r-{world}", "digest": "d", "status": "locked"} for world in LOCKED_WORLDS)
            robustness = ({"configuration_id": "c0", "contrast": "primary", "direction": 1,
                           "reversal": False, "within_plausible_region": True},)
            batch = BatchResult(manifest, item_rows(0), (0.05,), robustness, (0.5,), (0.12,))
            primary = {**precision_summary([0.5, 0.5]), "contrast": "primary_endpoint",
                       "precision_target": 0.01, "precision_resolved": True}
            contrast = {**precision_summary([0.05, 0.05]), "contrast": "proposed_vs_strongest_deployable",
                        "precision_target": 0.001, "precision_resolved": True}
            payloads = build_output_payloads(protocol, [batch], {"primary": primary, "contrast": contrast,
                                             "precision_resolved": True, "status": "resolved", "replications": 2})
            payloads["item_forecasts"] = [row for row in payloads["item_forecasts"]
                                          if not (row["world_id"] == LOCKED_WORLDS[0]
                                                  and row["model"] == "hie_compatible")]
            for record in protocol["output_contract"]:
                payload = payloads[record["id"]]
                record["required_fields"] = (["status", "contract_ids", "files", "key_reconciliation", "receipt_sha256"]
                                             if record["id"] == "publication_receipt"
                                             else list(payload[0] if isinstance(payload, list) else payload))
            for row in payloads["run_manifest"]: row["protocol_sha256"] = protocol_digest(protocol)
            with self.assertRaisesRegex(LockedRunRefusal, "model grid"):
                publish_outputs(protocol, root, payloads)
            self.assertFalse((root / "simulation/output/locked").exists())

    def test_readiness_builder_uses_protocol_metadata_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol = protocol_fixture(root)
            # Point at a deliberately missing seed artifact: readiness generation
            # must not accept, open, or parse a seed path.
            protocol["artifacts"]["seed_manifest"]["path"] = "missing/sealed.bin"
            runner = root / "runner.py"
            runner.write_text("LOCKED_EVALUATION_RUNNER=True\n", encoding="utf-8")
            record = build_readiness_record(protocol, runner)
            self.assertFalse(record["evaluation_seed_values_accessed"])
            self.assertEqual(record["locked_world_ids"], LOCKED_WORLDS)
            self.assertNotIn("seed_values", record)
            self.assertNotIn("seed_artifact_path", record)


if __name__ == "__main__":
    unittest.main()
