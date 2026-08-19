import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from simulation.prelock import REQUIRED_OUTPUTS, check_protocol


LOCKED_WORLDS = ["world_readiness", "world_mixed", "world_adversarial"]


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")


def protocol_fixture(root: Path) -> dict:
    config = root / "frozen/config.json"
    _write_json(config, {
        "experimental_design": {
            "development_world_ids": ["world_sp"],
            "locked_evaluation_world_ids": LOCKED_WORLDS,
        },
        "data_generating_worlds": [{"id": name} for name in ["world_sp", *LOCKED_WORLDS]],
    })
    seed_manifest = root / "sealed/seed-manifest.bin"
    seed_manifest.parent.mkdir(parents=True)
    seed_manifest.write_bytes(b"opaque sealed production manifest")
    parameter_registry = root / "frozen/parameter-registry.json"
    _write_json(parameter_registry, {
        "records": [{"id": "design", "path_pattern": "evaluation_rules.*",
                     "provenance_class": "I", "parameter_kind": "design_control",
                     "source_id": "protocol", "source_locator": "fixture",
                     "original_measure": "none", "transformation": "none",
                     "applicability_limits": "test fixture",
                     "permitted_uses": ["development_simulation", "production_decision_rule"],
                     "approval_status": "preregistered"}]
    })

    code_artifact = root / "release/source-release.bin"
    code_artifact.parent.mkdir(parents=True)
    code_artifact.write_bytes(b"frozen source release")
    code_hash = _digest(code_artifact)
    release_manifest = root / "release/release-manifest.json"
    _write_json(release_manifest, {
        "status": "frozen", "identifier": "release-1",
        "frozen_at_utc": "2026-08-13T12:15:00Z",
        "artifact_path": "release/source-release.bin", "artifact_sha256": code_hash,
    })

    review_record = root / "review/independent-review.json"
    _write_json(review_record, {
        "status": "approved", "reviewer_id": "review-agent-2",
        "completed_at_utc": "2026-08-13T12:30:00Z",
        "independence_attestation": True, "evaluation_seed_values_accessed": False,
        "code_release_identifier": "release-1", "code_artifact_sha256": code_hash,
        "scope": ["code", "protocol", "hard_stops"],
    })

    runner = root / "simulation/locked_runner.py"
    runner.parent.mkdir(parents=True)
    runner.write_text("LOCKED_EVALUATION_RUNNER = True\n\ndef main():\n    return 0\n", encoding="utf-8")
    runner_hash = _digest(runner)
    readiness_record = root / "release/runner-readiness.json"
    _write_json(readiness_record, {
        "status": "production_ready", "verification_mode": "contract_only_no_evaluation_seeds",
        "evaluation_seed_values_accessed": False, "runner_sha256": runner_hash,
        "locked_world_ids": LOCKED_WORLDS, "output_ids": sorted(REQUIRED_OUTPUTS),
    })
    seal_record = root / "sealed/external-seal.json"
    _write_json(seal_record, {
        "status": "externally_sealed", "sealed_at_utc": "2026-08-13T13:00:00Z",
        "independently_generated": True, "evaluation_values_disclosed": False,
        "namespace": "locked_evaluation", "replication_capacity": 50000,
        "seed_artifact_path": "sealed/seed-manifest.bin",
        "seed_artifact_sha256": _digest(seed_manifest),
    })

    outputs = [
        {"id": name, "path": f"simulation/output/locked/{name}.json", "format": "json",
         "required_fields": ["status"]}
        for name in sorted(REQUIRED_OUTPUTS)
    ]
    return {
        "status": "locked",
        "locked_at_utc": "2026-08-13T12:00:00Z",
        "artifacts": {
            "simulation_configuration": {"path": "frozen/config.json", "sha256": _digest(config)},
            "seed_manifest": {"path": "sealed/seed-manifest.bin", "sha256": _digest(seed_manifest)},
            "parameter_registry": {"path": "frozen/parameter-registry.json",
                                   "sha256": _digest(parameter_registry)},
        },
        "code_release": {
            "identifier": "release-1", "dirty_worktree": False,
            "manifest_path": "release/release-manifest.json", "manifest_sha256": _digest(release_manifest),
            "artifact_path": "release/source-release.bin", "artifact_sha256": code_hash,
        },
        "seed_policy": {
            "manifest_status": "production_locked_do_not_tune", "namespace": "locked_evaluation",
            "generation_method": "cryptographic_offline_manifest_v1", "manifest_artifact_id": "seed_manifest",
            "evaluation_replication_capacity": 50000, "evaluation_values_opened": False,
            "tuning_on_evaluation": False, "common_random_numbers": True,
            "development_namespace_only_until_ready": True, "access_control": "sealed_until_prelock_pass",
            "seal_record_path": "sealed/external-seal.json", "seal_record_sha256": _digest(seal_record),
        },
        "independent_review": {
            "status": "approved", "reviewer_id": "review-agent-2",
            "completed_at_utc": "2026-08-13T12:30:00Z",
            "review_record_path": "review/independent-review.json",
            "review_record_sha256": _digest(review_record),
        },
        "precision": {
            "primary_ci_half_width_max": 0.01, "contrast_ci_half_width_fraction_of_seoi": 0.1,
            "minimum_replications": 24, "maximum_replications": 50000,
            "replication_batch_size": 24,
            "unresolved_at_max_action": "report_unresolved_no_advantage_claim",
        },
        "evaluation_design": {
            "locked_world_ids": LOCKED_WORLDS, "paired_common_random_numbers": True,
            "no_post_opening_tuning": True, "retain_null_and_adverse_results": True,
            "primary_outcome_mapping": {
                "event": ["completed"],
                "non_event": ["completed_with_residual_risk", "failed", "dependency_failed", "censored"],
                "rationale": "strict verified completion",
            },
            "conditional_completion_sensitivity": {
                "analysis_id": "conditional_completion_inclusive",
                "event": ["completed", "completed_with_residual_risk"],
                "non_event": ["failed", "dependency_failed", "censored"],
                "method": "mandatory sensitivity without primary adjudication changes",
                "mandatory_report": True,
            },
        },
        "production_runner": {
            "path": "simulation/locked_runner.py", "sha256": runner_hash,
            "entrypoint": "simulation.locked_runner",
            "readiness_record_path": "release/runner-readiness.json",
            "readiness_record_sha256": _digest(readiness_record),
        },
        "output_contract": outputs,
        "decision_rules": {
            "primary_endpoint": "paired_brier", "strongest_deployable_selection": "lowest_brier",
            "smallest_effect_of_interest": {"absolute_brier_improvement": 0.01},
            "success_convention": {"relative_brier_skill_min": 0.05,
                                   "paired_95pct_interval_excludes_zero": True,
                                   "positive_configuration_fraction_min": 0.8,
                                   "bottleneck_accuracy_gain_min": 0.1},
            "equivalence_convention": "prefer_simpler_below_seoi",
            "instability_convention": "reversals_above_limit",
            "instability_reversal_fraction_max": 0.2,
            "claim_boundary": "synthetic_only",
        },
    }


def failed_ids(protocol: dict, root: Path) -> set[str]:
    return {check.check_id for check in check_protocol(protocol, root) if not check.passed}


class PrelockTests(unittest.TestCase):
    def test_complete_contract_is_ready(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            checks = check_protocol(protocol_fixture(root), root)
            self.assertTrue(all(check.passed for check in checks), checks)

    def test_placeholder_and_missing_review_are_hard_stops(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol = protocol_fixture(root)
            protocol["code_release"]["identifier"] = "PENDING-CODE"
            protocol["independent_review"]["status"] = "pending"
            failed = failed_ids(protocol, root)
            self.assertIn("no_placeholders", failed)
            self.assertIn("code_release", failed)
            self.assertIn("independent_review", failed)

    def test_invented_release_and_review_hashes_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol = protocol_fixture(root)
            protocol["code_release"]["manifest_sha256"] = "a" * 64
            protocol["independent_review"]["review_record_sha256"] = "b" * 64
            failed = failed_ids(protocol, root)
            self.assertIn("code_release", failed)
            self.assertIn("independent_review", failed)

    def test_release_manifest_content_must_cross_reference_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol = protocol_fixture(root)
            manifest = root / protocol["code_release"]["manifest_path"]
            record = json.loads(manifest.read_text(encoding="utf-8"))
            record["artifact_sha256"] = "c" * 64
            _write_json(manifest, record)
            protocol["code_release"]["manifest_sha256"] = _digest(manifest)
            self.assertIn("code_release", failed_ids(protocol, root))

    def test_prototype_or_undersized_seed_policy_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol = protocol_fixture(root)
            protocol["seed_policy"]["manifest_status"] = "prototype_locked_do_not_tune"
            protocol["seed_policy"]["evaluation_replication_capacity"] = 24
            self.assertIn("seed_policy", failed_ids(protocol, root))

    def test_external_seed_seal_must_be_fresh_and_match_opaque_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol = protocol_fixture(root)
            seal = root / protocol["seed_policy"]["seal_record_path"]
            record = json.loads(seal.read_text(encoding="utf-8"))
            record["sealed_at_utc"] = "2026-08-13T12:00:00Z"
            record["seed_artifact_sha256"] = "d" * 64
            _write_json(seal, record)
            protocol["seed_policy"]["seal_record_sha256"] = _digest(seal)
            self.assertIn("seed_policy", failed_ids(protocol, root))

    def test_locked_world_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol = protocol_fixture(root)
            protocol["evaluation_design"]["locked_world_ids"] = ["world_readiness"]
            failed = failed_ids(protocol, root)
            self.assertIn("locked_world_consistency", failed)
            self.assertIn("production_runner", failed)

    def test_missing_conditional_sensitivity_mapping_is_a_hard_stop(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol = protocol_fixture(root)
            protocol["evaluation_design"]["conditional_completion_sensitivity"]["mandatory_report"] = False
            self.assertIn("outcome_mappings", failed_ids(protocol, root))

    def test_runner_readiness_must_cover_outputs_and_same_binary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol = protocol_fixture(root)
            readiness = root / protocol["production_runner"]["readiness_record_path"]
            record = json.loads(readiness.read_text(encoding="utf-8"))
            record["output_ids"] = record["output_ids"][:-1]
            _write_json(readiness, record)
            protocol["production_runner"]["readiness_record_sha256"] = _digest(readiness)
            failed = failed_ids(protocol, root)
            self.assertIn("production_runner", failed)
            self.assertIn("output_readiness", failed)

    def test_preexisting_output_and_path_escape_are_hard_stops(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol = protocol_fixture(root)
            target = root / protocol["output_contract"][0]["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("stale", encoding="utf-8")
            self.assertIn("output_readiness", failed_ids(protocol, root))
            protocol["artifacts"]["simulation_configuration"]["path"] = "../outside.json"
            self.assertIn("artifact_checksums", failed_ids(protocol, root))

    def test_checksum_mismatch_and_incomplete_output_contract_are_hard_stops(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol = protocol_fixture(root)
            protocol["artifacts"]["simulation_configuration"]["sha256"] = "0" * 64
            protocol["output_contract"] = protocol["output_contract"][:-1]
            failed = failed_ids(protocol, root)
            self.assertIn("artifact_checksums", failed)
            self.assertIn("output_contract", failed)


if __name__ == "__main__":
    unittest.main()
