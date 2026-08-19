"""Pre-lock readiness audit for the synthetic evaluation.

This checker validates documentary commitments only.  It never executes the
simulation or prints seed values.  A failure is a hard stop: evaluation seeds
must remain unopened and untuned until every item passes.
"""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass, asdict
from datetime import datetime
from hashlib import sha256
import json
import os
from pathlib import Path
import re
from typing import Any, Mapping, Sequence

from .parameter_registry import ParameterProvenanceError, audit_by_intended_use


PLACEHOLDER = re.compile(r"(?:\bTBD\b|\bTODO\b|\bPENDING\b|<[^>]+>)", re.IGNORECASE)
SHA256 = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_OUTPUTS = {
    "run_manifest",
    "item_forecasts",
    "comparator_scores",
    "calibration",
    "monte_carlo_uncertainty",
    "robustness",
    "adjudication",
    "provenance",
    "hard_stop_report",
    "publication_receipt",
    "conditional_completion_inclusive",
}


@dataclass(frozen=True)
class ReadinessCheck:
    check_id: str
    passed: bool
    detail: str


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def _flatten_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, Mapping):
        return [text for child in value.values() for text in _flatten_strings(child)]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [text for child in value for text in _flatten_strings(child)]
    return []


def _valid_timestamp(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def _timestamp(value: Any) -> datetime | None:
    if not _valid_timestamp(value):
        return None
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def _file_under(root: Path, value: Any) -> Path | None:
    """Resolve a regular file without allowing absolute paths or root escape."""
    if not isinstance(value, str) or not value.strip():
        return None
    relative = Path(value)
    if relative.is_absolute():
        return None
    try:
        root_resolved = root.resolve()
        candidate = (root_resolved / relative).resolve(strict=True)
        candidate.relative_to(root_resolved)
    except (FileNotFoundError, OSError, ValueError):
        return None
    return candidate if candidate.is_file() else None


def _matches_file(root: Path, path_value: Any, digest_value: Any) -> tuple[bool, Path | None]:
    path = _file_under(root, path_value)
    expected = str(digest_value or "")
    valid = path is not None and bool(SHA256.fullmatch(expected))
    return (bool(valid and sha256(path.read_bytes()).hexdigest() == expected), path)


def _json_record(path: Path | None) -> Mapping[str, Any] | None:
    if path is None:
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, Mapping) else None


def _runner_source_ready(path: Path | None) -> bool:
    if path is None or path.suffix != ".py":
        return False
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, SyntaxError):
        return False
    has_main = any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "main" for node in tree.body)
    production_marker = any(
        isinstance(node, (ast.Assign, ast.AnnAssign))
        and any(
            isinstance(target, ast.Name) and target.id == "LOCKED_EVALUATION_RUNNER"
            for target in (node.targets if isinstance(node, ast.Assign) else [node.target])
        )
        and isinstance(node.value, ast.Constant)
        and node.value.value is True
        for node in tree.body
    )
    return has_main and production_marker


def check_protocol(protocol: Mapping[str, Any], root: Path) -> list[ReadinessCheck]:
    checks: list[ReadinessCheck] = []
    strings = _flatten_strings(protocol)
    checks.append(ReadinessCheck(
        "no_placeholders",
        not any(PLACEHOLDER.search(text) for text in strings),
        "lock-critical text contains no TBD/TODO/PENDING/angle-bracket placeholder",
    ))

    checks.append(ReadinessCheck(
        "protocol_locked",
        protocol.get("status") == "locked" and _valid_timestamp(protocol.get("locked_at_utc")),
        "status is locked and locked_at_utc is an ISO-8601 timestamp",
    ))

    artifacts = protocol.get("artifacts", {})
    artifact_ok = isinstance(artifacts, Mapping) and bool(artifacts)
    for record in artifacts.values() if isinstance(artifacts, Mapping) else ():
        matched, _ = _matches_file(root, record.get("path"), record.get("sha256"))
        artifact_ok = artifact_ok and matched
    checks.append(ReadinessCheck(
        "artifact_checksums",
        artifact_ok,
        "all frozen artifacts exist and match declared SHA-256 checksums",
    ))

    parameter_record = artifacts.get("parameter_registry", {}) if isinstance(artifacts, Mapping) else {}
    parameter_match, parameter_path = _matches_file(
        root, parameter_record.get("path"), parameter_record.get("sha256")
    )
    parameter_registry = _json_record(parameter_path) if parameter_match else None
    parameter_ok = False
    parameter_detail = "parameter registry is absent, invalid, or contains unsupported production calibration"
    try:
        config_record_for_parameters = artifacts.get("simulation_configuration", {}) if isinstance(artifacts, Mapping) else {}
        config_match_for_parameters, config_path_for_parameters = _matches_file(
            root, config_record_for_parameters.get("path"), config_record_for_parameters.get("sha256")
        )
        frozen_parameter_config = _json_record(config_path_for_parameters) if config_match_for_parameters else None
        if parameter_registry is not None and frozen_parameter_config is not None:
            evidence_record = artifacts.get("evidence_review_bundle", {}) if isinstance(artifacts, Mapping) else {}
            evidence_match, evidence_path = _matches_file(root, evidence_record.get("path"), evidence_record.get("sha256"))
            evidence_bundle = _json_record(evidence_path) if evidence_match else None
            audit = audit_by_intended_use(frozen_parameter_config, parameter_registry, evidence_bundle)
            parameter_ok = audit["production_calibration_status"] == "eligible"
            parameter_detail = (
                "all active parameters are registry-covered and production calibration is eligible"
                if parameter_ok else
                "unsupported production calibration records: "
                + ", ".join(audit["production_blocking_registry_ids"])
            )
    except ParameterProvenanceError as error:
        parameter_detail = str(error)
    checks.append(ReadinessCheck("parameter_provenance", parameter_ok, parameter_detail))

    code = protocol.get("code_release", {})
    code_manifest_match, code_manifest_path = _matches_file(
        root, code.get("manifest_path"), code.get("manifest_sha256")
    ) if isinstance(code, Mapping) else (False, None)
    code_artifact_match, code_artifact_path = _matches_file(
        root, code.get("artifact_path"), code.get("artifact_sha256")
    ) if isinstance(code, Mapping) else (False, None)
    release_record = _json_record(code_manifest_path) if code_manifest_match else None
    code_ok = (
        isinstance(code, Mapping)
        and code.get("dirty_worktree") is False
        and isinstance(code.get("identifier"), str)
        and bool(str(code.get("identifier")).strip())
        and not PLACEHOLDER.search(str(code.get("identifier")))
        and code_manifest_match
        and code_artifact_match
        and code_manifest_path != code_artifact_path
        and release_record is not None
        and release_record.get("status") == "frozen"
        and release_record.get("identifier") == code.get("identifier")
        and release_record.get("artifact_path") == code.get("artifact_path")
        and release_record.get("artifact_sha256") == code.get("artifact_sha256")
    )
    checks.append(ReadinessCheck(
        "code_release",
        code_ok,
        "real code-release manifest and artifact exist, hash-match, cross-reference, and are declared clean",
    ))

    seed = protocol.get("seed_policy", {})
    precision = protocol.get("precision", {})
    seal_match, seal_path = _matches_file(
        root, seed.get("seal_record_path"), seed.get("seal_record_sha256")
    ) if isinstance(seed, Mapping) else (False, None)
    seal_record = _json_record(seal_path) if seal_match else None
    seed_artifact_record = artifacts.get("seed_manifest", {}) if isinstance(artifacts, Mapping) else {}
    seal_time = _timestamp(seal_record.get("sealed_at_utc")) if seal_record else None
    review_time = _timestamp(protocol.get("independent_review", {}).get("completed_at_utc")) \
        if isinstance(protocol.get("independent_review"), Mapping) else None
    release_time = _timestamp(release_record.get("frozen_at_utc")) if release_record else None
    freshness_ok = (
        seal_time is not None and review_time is not None and release_time is not None
        and seal_time >= max(review_time, release_time)
    )
    try:
        seed_capacity_ok = int(seed.get("evaluation_replication_capacity", -1)) >= int(
            precision.get("maximum_replications", 0)
        ) > 0
    except (TypeError, ValueError):
        seed_capacity_ok = False
    seed_ok = (
        isinstance(seed, Mapping)
        and seed.get("manifest_status") == "production_locked_do_not_tune"
        and seed.get("namespace") == "locked_evaluation"
        and isinstance(seed.get("generation_method"), str)
        and bool(str(seed.get("generation_method")).strip())
        and not PLACEHOLDER.search(str(seed.get("generation_method")))
        and seed.get("manifest_artifact_id") == "seed_manifest"
        and isinstance(artifacts, Mapping)
        and seed.get("manifest_artifact_id") in artifacts
        and seed_capacity_ok
        and seed.get("evaluation_values_opened") is False
        and seed.get("tuning_on_evaluation") is False
        and seed.get("common_random_numbers") is True
        and seed.get("development_namespace_only_until_ready") is True
        and seed.get("access_control") == "sealed_until_prelock_pass"
        and seal_match
        and seal_record is not None
        and seal_record.get("status") == "externally_sealed"
        and seal_record.get("independently_generated") is True
        and seal_record.get("evaluation_values_disclosed") is False
        and seal_record.get("namespace") == seed.get("namespace")
        and seal_record.get("replication_capacity") == seed.get("evaluation_replication_capacity")
        and seal_record.get("seed_artifact_path") == seed_artifact_record.get("path")
        and seal_record.get("seed_artifact_sha256") == seed_artifact_record.get("sha256")
        and freshness_ok
    )
    checks.append(ReadinessCheck(
        "seed_policy",
        seed_ok,
        "fresh externally sealed production seed artifact is cross-referenced; values remain undisclosed",
    ))

    review = protocol.get("independent_review", {})
    review_match, review_path = _matches_file(
        root, review.get("review_record_path"), review.get("review_record_sha256")
    ) if isinstance(review, Mapping) else (False, None)
    review_record = _json_record(review_path) if review_match else None
    review_ok = (
        isinstance(review, Mapping)
        and review.get("status") == "approved"
        and isinstance(review.get("reviewer_id"), str)
        and bool(str(review.get("reviewer_id")).strip())
        and not PLACEHOLDER.search(str(review.get("reviewer_id")))
        and _valid_timestamp(review.get("completed_at_utc"))
        and review_match
        and review_record is not None
        and review_record.get("status") == "approved"
        and review_record.get("reviewer_id") == review.get("reviewer_id")
        and review_record.get("completed_at_utc") == review.get("completed_at_utc")
        and review_record.get("independence_attestation") is True
        and review_record.get("evaluation_seed_values_accessed") is False
        and review_record.get("code_release_identifier") == code.get("identifier")
        and review_record.get("code_artifact_sha256") == code.get("artifact_sha256")
        and set(review_record.get("scope", [])) >= {"code", "protocol", "hard_stops"}
    )
    checks.append(ReadinessCheck(
        "independent_review",
        review_ok,
        "a hash-matched independent review record approves the same code release and hard stops",
    ))

    precision_ok = False
    if isinstance(precision, Mapping):
        try:
            precision_ok = (
                0 < float(precision["primary_ci_half_width_max"]) <= 0.01
                and 0 < float(precision["contrast_ci_half_width_fraction_of_seoi"]) <= 0.10
                and int(precision["minimum_replications"]) >= 2
                and int(precision["maximum_replications"]) >= int(precision["minimum_replications"])
                and int(precision["replication_batch_size"]) > 0
                and precision.get("unresolved_at_max_action") == "report_unresolved_no_advantage_claim"
            )
        except (KeyError, TypeError, ValueError):
            precision_ok = False
    checks.append(ReadinessCheck(
        "precision_rule",
        precision_ok,
        "precision targets, batching, maximum, and unresolved-at-maximum action are declared",
    ))

    outputs = protocol.get("output_contract", [])
    output_ids: list[str] = []
    output_paths: list[str] = []
    output_ok = isinstance(outputs, list) and bool(outputs)
    for record in outputs if isinstance(outputs, list) else ():
        output_ids.append(str(record.get("id", "")))
        output_paths.append(str(record.get("path", "")))
        output_ok = output_ok and all(
            isinstance(record.get(field), str) and bool(record.get(field).strip())
            for field in ("id", "path", "format")
        )
        columns = record.get("required_fields")
        output_ok = output_ok and isinstance(columns, list) and bool(columns) and len(columns) == len(set(columns))
    output_ok = (
        output_ok
        and REQUIRED_OUTPUTS <= set(output_ids)
        and len(output_ids) == len(set(output_ids))
        and len(output_paths) == len(set(output_paths))
    )
    checks.append(ReadinessCheck(
        "output_contract",
        output_ok,
        "all mandatory outputs have unique paths and non-empty field contracts",
    ))

    # Locked worlds must be exactly those frozen in the simulation configuration.
    design = protocol.get("evaluation_design", {})
    config_record = artifacts.get("simulation_configuration", {}) if isinstance(artifacts, Mapping) else {}
    _, config_path = _matches_file(root, config_record.get("path"), config_record.get("sha256"))
    frozen_config = _json_record(config_path)
    protocol_worlds = design.get("locked_world_ids", []) if isinstance(design, Mapping) else []
    config_design = frozen_config.get("experimental_design", {}) if frozen_config else {}
    config_locked = config_design.get("locked_evaluation_world_ids", []) if isinstance(config_design, Mapping) else []
    config_development = config_design.get("development_world_ids", []) if isinstance(config_design, Mapping) else []
    declared_worlds = {
        record.get("id") for record in frozen_config.get("data_generating_worlds", [])
    } if frozen_config else set()
    world_ok = (
        isinstance(protocol_worlds, list) and bool(protocol_worlds)
        and len(protocol_worlds) == len(set(protocol_worlds))
        and set(protocol_worlds) == set(config_locked)
        and not set(protocol_worlds) & set(config_development)
        and set(protocol_worlds) <= declared_worlds
        and design.get("paired_common_random_numbers") is True
        and design.get("no_post_opening_tuning") is True
        and design.get("retain_null_and_adverse_results") is True
    )
    checks.append(ReadinessCheck(
        "locked_world_consistency", world_ok,
        "protocol locked worlds exactly match the frozen configuration and exclude development worlds",
    ))

    terminal_states = {"completed", "completed_with_residual_risk", "failed", "dependency_failed", "censored"}
    primary_mapping = design.get("primary_outcome_mapping", {}) if isinstance(design, Mapping) else {}
    sensitivity_mapping = design.get("conditional_completion_sensitivity", {}) if isinstance(design, Mapping) else {}
    mapping_ok = (
        set(primary_mapping.get("event", [])) == {"completed"}
        and set(primary_mapping.get("non_event", [])) == terminal_states - {"completed"}
        and sensitivity_mapping.get("analysis_id") == "conditional_completion_inclusive"
        and sensitivity_mapping.get("mandatory_report") is True
        and set(sensitivity_mapping.get("event", [])) == {"completed", "completed_with_residual_risk"}
        and set(sensitivity_mapping.get("non_event", []))
        == terminal_states - {"completed", "completed_with_residual_risk"}
        and "conditional_completion_inclusive" in set(output_ids)
    )
    checks.append(ReadinessCheck(
        "outcome_mappings", mapping_ok,
        "strict primary and mandatory conditional-inclusive sensitivity mappings are complete and contracted",
    ))

    runner = protocol.get("production_runner", {})
    runner_match, runner_path = _matches_file(
        root, runner.get("path"), runner.get("sha256")
    ) if isinstance(runner, Mapping) else (False, None)
    readiness_match, readiness_path = _matches_file(
        root, runner.get("readiness_record_path"), runner.get("readiness_record_sha256")
    ) if isinstance(runner, Mapping) else (False, None)
    readiness = _json_record(readiness_path) if readiness_match else None
    output_id_set = set(output_ids)
    runner_ok = (
        isinstance(runner, Mapping)
        and runner_match and _runner_source_ready(runner_path)
        and runner.get("entrypoint") not in {"simulation.test_runner", "simulation.development_pipeline"}
        and readiness_match and readiness is not None
        and readiness.get("status") == "production_ready"
        and readiness.get("verification_mode") == "contract_only_no_evaluation_seeds"
        and readiness.get("evaluation_seed_values_accessed") is False
        and readiness.get("runner_sha256") == runner.get("sha256")
        and set(readiness.get("locked_world_ids", [])) == set(protocol_worlds)
        and set(readiness.get("output_ids", [])) == output_id_set == REQUIRED_OUTPUTS
    )
    checks.append(ReadinessCheck(
        "production_runner", runner_ok,
        "hash-matched production runner and no-seed readiness record cover every locked world/output",
    ))

    output_paths_ready = True
    root_resolved = root.resolve()
    for value in output_paths:
        relative = Path(value)
        try:
            candidate = (root_resolved / relative).resolve()
            candidate.relative_to(root_resolved)
        except (OSError, ValueError):
            output_paths_ready = False
            continue
        output_paths_ready = (
            output_paths_ready
            and not relative.is_absolute()
            and not candidate.exists()
            and any(os.access(parent, os.W_OK) for parent in [candidate.parent, *candidate.parents] if parent.exists())
        )
    checks.append(ReadinessCheck(
        "output_readiness",
        output_ok and output_paths_ready and runner_ok,
        "output targets are unique, root-contained, absent before the run, writable, and covered by runner readiness",
    ))

    decisions = protocol.get("decision_rules", {})
    decision_ok = isinstance(decisions, Mapping) and all(
        key in decisions for key in (
            "primary_endpoint", "strongest_deployable_selection",
            "smallest_effect_of_interest", "success_convention",
            "equivalence_convention", "instability_convention", "claim_boundary",
        )
    )
    checks.append(ReadinessCheck(
        "decision_rules",
        decision_ok,
        "endpoint, comparator selection, thresholds, and claim boundary are prespecified",
    ))
    return checks


def load_and_check(path: str | Path, root: str | Path | None = None) -> list[ReadinessCheck]:
    protocol_path = Path(path)
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    return check_protocol(protocol, Path(root) if root else protocol_path.resolve().parents[2])


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("protocol", nargs="?", default="simulation/preregistration/locked_evaluation_protocol.json")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    checks = load_and_check(args.protocol, args.root)
    ready = all(check.passed for check in checks)
    payload = {"status": "ready_to_open" if ready else "hard_stop_not_ready", "checks": [asdict(c) for c in checks]}
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for check in checks:
            print(f"{'PASS' if check.passed else 'FAIL'} {check.check_id}: {check.detail}")
        print(payload["status"])
    return 0 if ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
