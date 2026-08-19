"""Production locked-evaluation orchestration with a fail-closed preflight.

This module does not generate seeds.  A caller-supplied batch executor may be
invoked only after the complete protocol passes :mod:`simulation.prelock`.
Unit tests use synthetic summaries and never open the sealed seed artifact.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from math import sqrt
import os
from pathlib import Path
import shutil
from statistics import stdev
import tempfile
from typing import Any, Callable, Mapping, Sequence

from .evaluation import calibration_table, paired_brier_contrast
from .prelock import REQUIRED_OUTPUTS, check_protocol


LOCKED_EVALUATION_RUNNER = True
INTERPRETATION_BOUNDARY = (
    "Synthetic mechanism evaluation only; no human, organizational, or causal AI validity claim."
)


class LockedRunRefusal(RuntimeError):
    """Raised before seed access or output creation when a hard stop fails."""


@dataclass(frozen=True)
class BatchResult:
    """Seed-free interface between orchestration and the sealed executor.

    ``items`` contain one row per item/model with keys required by the locked
    item-forecast contract. ``replication_contrasts`` are independent paired
    Brier improvements (positive favors the proposed model).
    """
    run_manifest: tuple[Mapping[str, Any], ...]
    items: tuple[Mapping[str, Any], ...]
    replication_contrasts: tuple[float, ...]
    robustness: tuple[Mapping[str, Any], ...] = ()
    primary_estimates: tuple[float, ...] = ()
    bottleneck_improvements: tuple[float, ...] = ()


BatchExecutor = Callable[[Sequence[str], int, int], BatchResult]


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def _hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def protocol_digest(protocol: Mapping[str, Any]) -> str:
    return sha256(_canonical(protocol)).hexdigest()


def require_prelock_ready(protocol: Mapping[str, Any], root: Path) -> None:
    """Validate readiness before a seed-capable dependency is called."""
    failed = [check.check_id for check in check_protocol(protocol, root) if not check.passed]
    if failed:
        raise LockedRunRefusal(f"prelock hard stop; failed checks: {', '.join(failed)}")


def precision_summary(values: Sequence[float], confidence_multiplier: float = 1.96) -> dict[str, Any]:
    if len(values) < 2:
        return {"estimate": None, "standard_error": None, "ci_lower": None,
                "ci_upper": None, "half_width": None, "replications": len(values)}
    estimate = sum(float(value) for value in values) / len(values)
    standard_error = stdev(float(value) for value in values) / sqrt(len(values))
    half_width = confidence_multiplier * standard_error
    return {"estimate": estimate, "standard_error": standard_error,
            "ci_lower": estimate - half_width, "ci_upper": estimate + half_width,
            "half_width": half_width, "replications": len(values)}


def collect_batches(protocol: Mapping[str, Any], executor: BatchExecutor) -> tuple[list[BatchResult], dict[str, Any]]:
    """Collect batches until distinct primary and contrast rules both resolve."""
    precision = protocol["precision"]
    minimum = int(precision["minimum_replications"])
    maximum = int(precision["maximum_replications"])
    batch_size = int(precision["replication_batch_size"])
    primary_target = float(precision["primary_ci_half_width_max"])
    seoi = float(protocol["decision_rules"]["smallest_effect_of_interest"]["absolute_brier_improvement"])
    contrast_target = float(precision["contrast_ci_half_width_fraction_of_seoi"]) * seoi
    worlds = tuple(protocol["evaluation_design"]["locked_world_ids"])
    batches: list[BatchResult] = []
    contrasts: list[float] = []
    primaries: list[float] = []
    start = 0
    resolved = False
    while start < maximum:
        count = min(batch_size, maximum - start)
        batch = executor(worlds, start, count)
        if len(batch.replication_contrasts) != count:
            raise LockedRunRefusal("executor returned a contrast count inconsistent with the requested batch")
        if len(batch.primary_estimates) != count:
            raise LockedRunRefusal("executor returned a primary-estimate count inconsistent with the requested batch")
        if len(batch.bottleneck_improvements) != count:
            raise LockedRunRefusal("executor returned a bottleneck-improvement count inconsistent with the requested batch")
        batches.append(batch)
        contrasts.extend(float(value) for value in batch.replication_contrasts)
        primaries.extend(float(value) for value in batch.primary_estimates)
        start += count
        primary_summary = precision_summary(primaries)
        contrast_summary = precision_summary(contrasts)
        primary_resolved = (
            start >= minimum and primary_summary["half_width"] is not None
            and primary_summary["half_width"] <= primary_target
        )
        contrast_resolved = (
            start >= minimum and contrast_summary["half_width"] is not None
            and contrast_summary["half_width"] <= contrast_target
        )
        resolved = primary_resolved and contrast_resolved
        if resolved:
            break
    primary_summary = precision_summary(primaries)
    contrast_summary = precision_summary(contrasts)
    primary_resolved = bool(start >= minimum and primary_summary["half_width"] is not None
                            and primary_summary["half_width"] <= primary_target)
    contrast_resolved = bool(start >= minimum and contrast_summary["half_width"] is not None
                             and contrast_summary["half_width"] <= contrast_target)
    primary_summary.update({"contrast": "primary_endpoint", "precision_target": primary_target,
                            "precision_resolved": primary_resolved})
    contrast_summary.update({"contrast": "proposed_vs_strongest_deployable",
                             "precision_target": contrast_target,
                             "precision_resolved": contrast_resolved})
    return batches, {
        "primary": primary_summary, "contrast": contrast_summary,
        "precision_resolved": primary_resolved and contrast_resolved,
        "status": "resolved" if primary_resolved and contrast_resolved else "precision_unresolved",
        "replications": start,
    }


def _rows(batches: Sequence[BatchResult], attribute: str) -> list[dict[str, Any]]:
    return [dict(row) for batch in batches for row in getattr(batch, attribute)]


TERMINAL_STATES = {"completed", "completed_with_residual_risk", "failed", "dependency_failed", "censored"}


def _outcome_mappings(protocol: Mapping[str, Any]) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    design = protocol.get("evaluation_design", {})
    primary = design.get("primary_outcome_mapping", {})
    sensitivity = design.get("conditional_completion_sensitivity", {})
    primary_ok = (set(primary.get("event", [])) == {"completed"}
                  and set(primary.get("non_event", [])) == TERMINAL_STATES - {"completed"})
    sensitivity_ok = (
        sensitivity.get("analysis_id") == "conditional_completion_inclusive"
        and sensitivity.get("mandatory_report") is True
        and set(sensitivity.get("event", [])) == {"completed", "completed_with_residual_risk"}
        and set(sensitivity.get("non_event", [])) == TERMINAL_STATES - {
            "completed", "completed_with_residual_risk"
        }
    )
    if not primary_ok or not sensitivity_ok:
        raise LockedRunRefusal("primary and conditional-inclusive outcome mappings must be complete and exact")
    return primary, sensitivity


def _map_outcomes(protocol: Mapping[str, Any], items: Sequence[Mapping[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    primary, sensitivity = _outcome_mappings(protocol)
    primary_events = set(primary["event"]); sensitivity_events = set(sensitivity["event"])
    primary_rows: list[dict[str, Any]] = []; sensitivity_rows: list[dict[str, Any]] = []
    for source in items:
        state = str(source.get("terminal_state", ""))
        if state not in TERMINAL_STATES:
            raise LockedRunRefusal(f"unknown or missing terminal_state {state!r}")
        primary_outcome = int(state in primary_events)
        supplied = source.get("outcome_completed")
        if supplied not in (0, 1) or int(supplied) != primary_outcome:
            raise LockedRunRefusal("outcome_completed does not match strict primary terminal-state mapping")
        primary_rows.append({**source, "outcome_completed": primary_outcome})
        sensitivity_rows.append({**source, "outcome_completed": int(state in sensitivity_events)})
    return primary_rows, sensitivity_rows


def _score_outputs(items: Sequence[Mapping[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    groups: dict[tuple[str, str], list[tuple[float, int]]] = {}
    for row in items:
        key = (str(row["world_id"]), str(row["model"]))
        groups.setdefault(key, []).append((float(row["probability"]), int(row["outcome_completed"])))
    scores: list[dict[str, Any]] = []
    calibration: list[dict[str, Any]] = []
    for (world, model), values in sorted(groups.items()):
        probabilities, outcomes = zip(*values)
        brier = sum((p - y) ** 2 for p, y in values) / len(values)
        # Log loss is intentionally delegated to the stable evaluation module.
        from .evaluation import expected_calibration_error, log_loss
        scores.append({"world_id": world, "model": model, "n": len(values), "brier_score": brier,
                       "log_loss": log_loss(probabilities, outcomes),
                       "ece": expected_calibration_error(probabilities, outcomes)})
        for row in calibration_table(probabilities, outcomes):
            calibration.append({"world_id": world, "model": model, "bin": row["bin"],
                                "n": row["count"], "mean_probability": row["mean_forecast"],
                                "event_rate": row["observed_rate"]})
    return scores, calibration


def _aggregate_brier(items: Sequence[Mapping[str, Any]]) -> dict[str, float]:
    grouped: dict[str, list[tuple[float, int]]] = {}
    for row in items:
        grouped.setdefault(str(row["model"]), []).append(
            (float(row["probability"]), int(row["outcome_completed"]))
        )
    if "proposed_model" not in grouped:
        raise LockedRunRefusal("proposed_model forecasts are absent")
    deployable = [name for name in ("story_points", "hie_compatible", "simple_role_load") if name in grouped]
    if not deployable:
        raise LockedRunRefusal("no deployable comparator forecasts are present")
    return {model: sum((p - y) ** 2 for p, y in values) / len(values)
            for model, values in grouped.items()}


def adjudicate_gate4b(protocol: Mapping[str, Any], *, relative_skill: float,
                      absolute_improvement: float, contrast_ci_lower: float | None,
                      precision_resolved: bool, robustness_fraction: float,
                      bottleneck_improvement: float) -> dict[str, bool]:
    """Apply every prespecified Gate 4B success threshold independently."""
    rules = protocol["decision_rules"]
    convention = rules["success_convention"]
    seoi = float(rules["smallest_effect_of_interest"]["absolute_brier_improvement"])
    return {
        "precision_pass": precision_resolved is True,
        "relative_brier_skill_pass": relative_skill >= float(convention["relative_brier_skill_min"]),
        "absolute_improvement_pass": absolute_improvement >= seoi,
        "ci_excludes_zero_pass": contrast_ci_lower is not None and contrast_ci_lower > 0,
        "robustness_pass": robustness_fraction >= float(convention["positive_configuration_fraction_min"]),
        "bottleneck_improvement_pass": bottleneck_improvement >= float(convention["bottleneck_accuracy_gain_min"]),
    }


def _conditional_sensitivity(protocol: Mapping[str, Any], items: Sequence[Mapping[str, Any]],
                             primary_adjudication: Mapping[str, Any]) -> dict[str, Any]:
    scores, calibration = _score_outputs(items)
    brier = _aggregate_brier(items)
    deployable = [name for name in ("story_points", "hie_compatible", "simple_role_load") if name in brier]
    reference = min(deployable, key=lambda name: (brier[name], name))
    keyed: dict[tuple[str, int, str], dict[str, Any]] = {}
    for row in items:
        key = (str(row["world_id"]), int(row["replication_id"]), str(row["item_id"]))
        group = keyed.setdefault(key, {"outcome": int(row["outcome_completed"]), "forecasts": {}})
        if group["outcome"] != int(row["outcome_completed"]):
            raise LockedRunRefusal("sensitivity outcomes disagree across models")
        group["forecasts"][str(row["model"])] = float(row["probability"])
    proposed = [group["forecasts"]["proposed_model"] for _, group in sorted(keyed.items())]
    references = [group["forecasts"][reference] for _, group in sorted(keyed.items())]
    outcomes = [group["outcome"] for _, group in sorted(keyed.items())]
    contrast = paired_brier_contrast(proposed, references, outcomes)
    absolute = float(contrast["absolute_improvement"])
    relative = float(contrast["relative_skill"])
    rules = protocol["decision_rules"]
    checks = {
        "relative_brier_skill_pass": relative >= float(rules["success_convention"]["relative_brier_skill_min"]),
        "absolute_improvement_pass": absolute >= float(rules["smallest_effect_of_interest"]["absolute_brier_improvement"]),
        "ci_excludes_zero_pass": float(contrast["ci95_lower"]) > 0,
    }
    primary_hash = sha256(_canonical(primary_adjudication)).hexdigest()
    return {
        "analysis_id": "conditional_completion_inclusive",
        "outcome_mapping": protocol["evaluation_design"]["conditional_completion_sensitivity"],
        "strongest_deployable": reference, "brier_scores": brier,
        "absolute_brier_improvement": absolute, "relative_brier_skill": relative,
        "paired_contrast": contrast, "calibration": calibration, "comparator_scores": scores,
        "threshold_checks": checks, "sensitivity_result": "favorable" if all(checks.values()) else "no_advantage",
        "primary_adjudication_unchanged": True, "primary_result_snapshot": primary_adjudication["primary_result"],
        "primary_adjudication_sha256": primary_hash,
        "interpretation_boundary": "Mandatory sensitivity only; cannot alter primary adjudication.",
    }


def build_output_payloads(protocol: Mapping[str, Any], batches: Sequence[BatchResult],
                          uncertainty: Mapping[str, Any]) -> dict[str, Any]:
    raw_items = _rows(batches, "items")
    items, sensitivity_items = _map_outcomes(protocol, raw_items)
    scores, calibration = _score_outputs(items)
    robustness = _rows(batches, "robustness")
    plausible = [row for row in robustness if row.get("within_plausible_region") is True]
    favorable = sum(float(row.get("direction", 0)) > 0 for row in plausible)
    robustness_fraction = favorable / len(plausible) if plausible else 0.0
    reversal_fraction = sum(bool(row.get("reversal")) for row in plausible) / len(plausible) if plausible else 1.0
    brier = _aggregate_brier(items)
    deployable = [name for name in ("story_points", "hie_compatible", "simple_role_load") if name in brier]
    reference_model = min(deployable, key=lambda name: (brier[name], name))
    reference_brier = brier[reference_model]
    proposed_brier = brier["proposed_model"]
    absolute_improvement = reference_brier - proposed_brier
    relative_skill = absolute_improvement / reference_brier if reference_brier > 0 else float("-inf")
    bottleneck_values = [float(value) for batch in batches for value in batch.bottleneck_improvements]
    if not bottleneck_values:
        raise LockedRunRefusal("bottleneck-improvement observations are absent")
    bottleneck_improvement = sum(bottleneck_values) / len(bottleneck_values)
    rules = protocol["decision_rules"]
    convention = rules["success_convention"]
    seoi = float(rules["smallest_effect_of_interest"]["absolute_brier_improvement"])
    contrast = uncertainty["contrast"]
    checks = adjudicate_gate4b(
        protocol, relative_skill=relative_skill, absolute_improvement=absolute_improvement,
        contrast_ci_lower=None if contrast["ci_lower"] is None else float(contrast["ci_lower"]),
        precision_resolved=uncertainty["precision_resolved"] is True,
        robustness_fraction=robustness_fraction, bottleneck_improvement=bottleneck_improvement,
    )
    success = all(checks.values())
    instability_limit = float(rules.get("instability_reversal_fraction_max", 0.20))
    now = datetime.now(timezone.utc).isoformat()
    adjudication = {
        "primary_result": "favorable" if success else "no_advantage_claim",
        "precision_status": uncertainty["status"], "success_convention": success,
        "threshold_checks": checks, "strongest_deployable": reference_model,
        "proposed_brier_score": proposed_brier, "reference_brier_score": reference_brier,
        "relative_brier_skill": relative_skill, "absolute_brier_improvement": absolute_improvement,
        "robustness_fraction": robustness_fraction,
        "bottleneck_accuracy_improvement": bottleneck_improvement,
        "equivalence_convention": protocol["decision_rules"]["equivalence_convention"],
        "instability_status": "stable" if reversal_fraction <= instability_limit else "unstable",
        "claim_boundary": protocol["decision_rules"]["claim_boundary"],
    }
    sensitivity_report = _conditional_sensitivity(protocol, sensitivity_items, adjudication)
    if sha256(_canonical(adjudication)).hexdigest() != sensitivity_report["primary_adjudication_sha256"]:
        raise LockedRunRefusal("conditional sensitivity altered primary adjudication")
    return {
        "run_manifest": _rows(batches, "run_manifest"),
        "item_forecasts": items,
        "comparator_scores": scores,
        "calibration": calibration,
        "monte_carlo_uncertainty": [dict(uncertainty["primary"]), dict(uncertainty["contrast"])],
        "robustness": robustness,
        "adjudication": adjudication,
        "conditional_completion_inclusive": sensitivity_report,
        "provenance": {
            "protocol_sha256": protocol_digest(protocol),
            "artifact_sha256": {key: value["sha256"] for key, value in protocol["artifacts"].items()},
            "environment": "python-stdlib", "started_at_utc": now, "completed_at_utc": now,
        },
        "hard_stop_report": [{"check_id": "prelock", "passed": True,
                              "detail": "all prelock checks passed before executor invocation",
                              "checked_at_utc": now}],
        "publication_receipt": {"status": "pending_staged_checksums"},
    }


def _validate_required_fields(record: Mapping[str, Any], payload: Any) -> None:
    fields = set(record["required_fields"])
    rows = payload if isinstance(payload, list) else [payload]
    if not rows or any(not isinstance(row, Mapping) or not fields <= set(row) for row in rows):
        raise LockedRunRefusal(f"output {record['id']} does not satisfy required_fields")


def _reconcile_payload_keys(protocol: Mapping[str, Any], payloads: Mapping[str, Any]) -> dict[str, Any]:
    runs = payloads["run_manifest"]
    items = payloads["item_forecasts"]
    scores = payloads["comparator_scores"]
    calibration = payloads["calibration"]
    robustness = payloads["robustness"]
    uncertainty = payloads["monte_carlo_uncertainty"]
    sensitivity = payloads["conditional_completion_inclusive"]
    run_keys = [(str(row["world_id"]), int(row["replication_id"])) for row in runs]
    if len(run_keys) != len(set(run_keys)):
        raise LockedRunRefusal("duplicate world/replication key in run_manifest")
    expected_worlds = set(protocol["evaluation_design"]["locked_world_ids"])
    if {world for world, _ in run_keys} != expected_worlds:
        raise LockedRunRefusal("run_manifest worlds do not exactly reconcile to locked worlds")
    item_keys = [(str(row["world_id"]), int(row["replication_id"]), str(row["item_id"]),
                  str(row["model"])) for row in items]
    if len(item_keys) != len(set(item_keys)):
        raise LockedRunRefusal("duplicate item/model forecast key")
    if not {(world, replication) for world, replication, _, _ in item_keys} <= set(run_keys):
        raise LockedRunRefusal("item forecast references an absent run")
    item_groups: dict[tuple[str, int, str], dict[str, int]] = {}
    for row in items:
        key = (str(row["world_id"]), int(row["replication_id"]), str(row["item_id"]))
        item_groups.setdefault(key, {})[str(row["model"])] = int(row["outcome_completed"])
    required_models = {"story_points", "hie_compatible", "simple_role_load", "proposed_model"}
    for key, outcomes in item_groups.items():
        if not required_models <= set(outcomes) or len(set(outcomes.values())) != 1:
            raise LockedRunRefusal(f"forecast model grid/outcome mismatch at item {key}")
    forecast_groups = {(world, model) for world, _, _, model in item_keys}
    score_keys = [(str(row["world_id"]), str(row["model"])) for row in scores]
    if len(score_keys) != len(set(score_keys)) or set(score_keys) != forecast_groups:
        raise LockedRunRefusal("comparator score keys do not reconcile to item forecasts")
    calibration_groups = {(str(row["world_id"]), str(row["model"])) for row in calibration}
    if calibration_groups != forecast_groups:
        raise LockedRunRefusal("calibration keys do not reconcile to item forecasts")
    robustness_keys = [(str(row["configuration_id"]), str(row["contrast"])) for row in robustness]
    if not robustness_keys or len(robustness_keys) != len(set(robustness_keys)):
        raise LockedRunRefusal("robustness configuration/contrast keys are empty or duplicated")
    if {str(row["contrast"]) for row in uncertainty} != {
        "primary_endpoint", "proposed_vs_strongest_deployable"
    }:
        raise LockedRunRefusal("primary and contrast uncertainty rows do not reconcile")
    expected_protocol = protocol_digest(protocol)
    if any(str(row["protocol_sha256"]) != expected_protocol for row in runs):
        raise LockedRunRefusal("run manifest protocol hashes do not reconcile to the locked protocol")
    if (sensitivity.get("analysis_id") != "conditional_completion_inclusive"
            or sensitivity.get("primary_adjudication_unchanged") is not True
            or sensitivity.get("primary_result_snapshot") != payloads["adjudication"]["primary_result"]
            or sensitivity.get("primary_adjudication_sha256")
            != sha256(_canonical(payloads["adjudication"])).hexdigest()):
        raise LockedRunRefusal("conditional sensitivity does not reconcile to immutable primary adjudication")
    return {"run_keys": len(run_keys), "item_model_keys": len(item_keys),
            "forecast_groups": len(forecast_groups), "status": "reconciled"}


def _write_payload(path: Path, record: Mapping[str, Any], payload: Any) -> None:
    if record["format"] == "json":
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif record["format"] == "csv":
        rows = payload
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    else:
        raise LockedRunRefusal(f"unsupported immutable output format: {record['format']}")


def publish_outputs(protocol: Mapping[str, Any], root: Path, payloads: Mapping[str, Any]) -> dict[str, Any]:
    """Validate, checksum, and atomically publish one previously absent directory."""
    contracts = protocol["output_contract"]
    if set(payloads) != {record["id"] for record in contracts}:
        raise LockedRunRefusal("payload IDs do not exactly match the immutable output contract")
    root = root.resolve()
    reconciliation = _reconcile_payload_keys(protocol, payloads)
    targets: list[tuple[Mapping[str, Any], Path]] = []
    for record in contracts:
        target = (root / record["path"]).resolve()
        try:
            target.relative_to(root)
        except ValueError as error:
            raise LockedRunRefusal("output path escapes project root") from error
        if record["id"] != "publication_receipt":
            _validate_required_fields(record, payloads[record["id"]])
        targets.append((record, target))
    output_dirs = {target.parent for _, target in targets}
    if len(output_dirs) != 1:
        raise LockedRunRefusal("fail-clean publication requires one common output directory")
    output_dir = next(iter(output_dirs))
    if output_dir.exists():
        raise LockedRunRefusal(f"immutable output directory already exists: {output_dir.relative_to(root)}")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.staging-", dir=output_dir.parent))
    contract_by_id = {record["id"]: record for record in contracts}
    try:
        files: list[dict[str, Any]] = []
        for record, target in targets:
            if record["id"] == "publication_receipt":
                continue
            temporary = staging / target.name
            payload = payloads[record["id"]]
            _write_payload(temporary, record, payload)
            files.append({"output_id": record["id"], "path": str(Path(record["path"]).name),
                          "sha256": _hash(temporary),
                          "row_count": len(payload) if isinstance(payload, list) else 1})
        receipt_core = {"status": "verified", "contract_ids": sorted(contract_by_id),
                        "files": files, "key_reconciliation": reconciliation}
        receipt = {**receipt_core, "receipt_sha256": sha256(_canonical(receipt_core)).hexdigest()}
        receipt_record = contract_by_id["publication_receipt"]
        _validate_required_fields(receipt_record, receipt)
        receipt_path = staging / Path(receipt_record["path"]).name
        _write_payload(receipt_path, receipt_record, receipt)
        for file_record in files:
            if _hash(staging / file_record["path"]) != file_record["sha256"]:
                raise LockedRunRefusal(f"staged checksum mismatch for {file_record['output_id']}")
        os.replace(staging, output_dir)
        return receipt
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        raise


def execute_locked(protocol_path: str | Path, root: str | Path, executor: BatchExecutor) -> dict[str, Any]:
    protocol = json.loads(Path(protocol_path).read_text(encoding="utf-8"))
    root_path = Path(root)
    require_prelock_ready(protocol, root_path)
    batches, uncertainty = collect_batches(protocol, executor)
    payloads = build_output_payloads(protocol, batches, uncertainty)
    publish_outputs(protocol, root_path, payloads)
    return {"status": uncertainty["status"], "replications": uncertainty["replications"]}


def build_readiness_record(protocol: Mapping[str, Any], runner_path: str | Path) -> dict[str, Any]:
    """Build public metadata only; neither accepts nor reads a seed path."""
    path = Path(runner_path)
    return {
        "status": "production_ready", "verification_mode": "contract_only_no_evaluation_seeds",
        "evaluation_seed_values_accessed": False, "runner_sha256": _hash(path),
        "locked_world_ids": list(protocol["evaluation_design"]["locked_world_ids"]),
        "output_ids": sorted(record["id"] for record in protocol["output_contract"]),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", default="simulation/preregistration/locked_evaluation_protocol.json")
    parser.add_argument("--root", default=".")
    parser.add_argument("--readiness-record", action="store_true")
    args = parser.parse_args(argv)
    protocol = json.loads(Path(args.protocol).read_text(encoding="utf-8"))
    if args.readiness_record:
        print(json.dumps(build_readiness_record(protocol, Path(__file__)), indent=2, sort_keys=True))
        return 0
    # CLI refuses before an external sealed-executor adapter is deliberately installed.
    require_prelock_ready(protocol, Path(args.root))
    raise LockedRunRefusal("no sealed seed executor is installed; locked worlds were not executed")


if __name__ == "__main__":
    raise SystemExit(main())
