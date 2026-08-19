"""Machine-verifiable provenance boundary for active simulation parameters."""
from __future__ import annotations

import fnmatch
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


class ParameterProvenanceError(ValueError):
    pass


@dataclass(frozen=True)
class ParameterCheck:
    path: str
    registry_id: str
    provenance_class: str
    parameter_kind: str
    permitted: bool


def active_parameter_paths(config: Mapping[str, Any]) -> tuple[str, ...]:
    """Enumerate inputs that affect execution, comparators, or adjudication."""
    paths: list[str] = []
    for field in ("horizon", "warmup"):
        if field in config.get("time_model", {}):
            paths.append(f"time_model.{field}")
    for record in config.get("role_pools", []):
        for field in ("concurrent_servers", "initial_backlog"):
            paths.append(f"role_pools.{record['id']}.{field}")
    for record in config.get("arrival_models", []):
        for field in ("count", "start", "spacing", "template_ids"):
            if field in record.get("parameters", {}):
                paths.append(f"arrival_models.{record['id']}.parameters.{field}")
    for record in config.get("demand_models", []):
        dist = record["base_distribution"]
        paths.append(f"demand_models.{record['id']}.base_distribution.family")
        for field in sorted(dist.get("parameters", {})):
            paths.append(f"demand_models.{record['id']}.base_distribution.parameters.{field}")
        if "truncation" in dist:
            paths.append(f"demand_models.{record['id']}.base_distribution.truncation")
        paths.append(f"demand_models.{record['id']}.base_distribution.independence_declared")
    for calendar in config.get("capacity_calendars", []):
        paths.append(f"capacity_calendars.{calendar['id']}.concurrency")
        for index, _ in enumerate(calendar.get("intervals", [])):
            for field in ("start", "end", "gross_hours", "absence_hours", "nonproject_hours", "effective_hours"):
                paths.append(f"capacity_calendars.{calendar['id']}.intervals.{index}.{field}")
        for index, _ in enumerate(calendar.get("blackout_periods", [])):
            paths.extend((f"capacity_calendars.{calendar['id']}.blackout_periods.{index}.start",
                          f"capacity_calendars.{calendar['id']}.blackout_periods.{index}.end"))
    for record in config.get("rework_models", []):
        paths.append(f"rework_models.{record['id']}.maximum_loops")
        for index, _ in enumerate(record.get("routes", [])):
            paths.append(f"rework_models.{record['id']}.routes.{index}.probability")
    for world in config.get("data_generating_worlds", []):
        for field in sorted(world.get("truth_parameters", {})):
            paths.append(f"data_generating_worlds.{world['id']}.truth_parameters.{field}")
    for template in config.get("work_item_templates", []):
        paths.append(f"work_item_templates.{template['id']}.story_points")
        for field in sorted(template.get("hie_compatible_fields", {})):
            paths.append(f"work_item_templates.{template['id']}.hie_compatible_fields.{field}")
        for construct in sorted(template.get("pdd_profile", {})):
            paths.append(f"work_item_templates.{template['id']}.pdd_profile.{construct}.level")
    for field in sorted(config.get("evaluation_rules", {})):
        paths.append(f"evaluation_rules.{field}")
    return tuple(sorted(paths))


def load_registry(path: str | Path) -> Mapping[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise ParameterProvenanceError("parameter registry root must be an object")
    return value


def check_parameter_registry(config: Mapping[str, Any], registry: Mapping[str, Any], *,
                             use: str, evidence_bundle: Mapping[str, Any] | None = None) -> tuple[ParameterCheck, ...]:
    if use not in {"development_simulation", "production_calibration", "production_decision_rule"}:
        raise ParameterProvenanceError(f"unsupported parameter use {use!r}")
    records = registry.get("records")
    if not isinstance(records, list) or not records:
        raise ParameterProvenanceError("parameter registry has no records")
    required = {"id", "path_pattern", "provenance_class", "parameter_kind", "source_id",
                "source_locator", "original_measure", "transformation", "applicability_limits",
                "permitted_uses", "approval_status"}
    for record in records:
        if not isinstance(record, Mapping) or not required <= set(record):
            raise ParameterProvenanceError("parameter registry record is incomplete")
    results: list[ParameterCheck] = []
    failures: list[str] = []
    for path in active_parameter_paths(config):
        matches = [record for record in records if fnmatch.fnmatchcase(path, str(record["path_pattern"]))]
        if len(matches) != 1:
            failures.append(f"{path}: expected exactly one registry match, got {len(matches)}")
            continue
        record = matches[0]
        provenance = str(record["provenance_class"])
        kind = str(record["parameter_kind"])
        permitted = use in record["permitted_uses"]
        if use == "production_calibration":
            permitted = (permitted and kind == "calibration" and provenance in {"E1", "E2"}
                         and record["approval_status"] == "verified_executable"
                         and _evidence_link_verified(record, evidence_bundle))
        elif use == "production_decision_rule":
            permitted = permitted and kind == "design_control" and record["approval_status"] == "preregistered"
        if not permitted:
            failures.append(f"{path}: class={provenance}, kind={kind}, approval={record['approval_status']} forbids {use}")
        results.append(ParameterCheck(path, str(record["id"]), provenance, kind, permitted))
    if failures:
        raise ParameterProvenanceError("parameter provenance hard stop:\n" + "\n".join(failures))
    return tuple(results)


def _evidence_link_verified(record: Mapping[str, Any], bundle: Mapping[str, Any] | None) -> bool:
    """Require a final evidence bundle and accountable transformation audit."""
    if bundle is None:
        return False
    try:
        from evidence_review.workflow import validate_bundle
        validate_bundle(dict(bundle), require_complete=True)
    except Exception:
        return False
    extraction_id = record.get("evidence_extraction_id")
    extraction = next((x for x in bundle.get("extractions", []) if x.get("extraction_id") == extraction_id), None)
    if not extraction or extraction.get("verification_status") != "verified":
        return False
    confirmations = [x for x in bundle.get("citation_confirmations", [])
                     if x.get("extraction_id") == extraction_id and x.get("status") == "confirmed"
                     and x.get("supports_claim") is True]
    audit = record.get("transformation_audit")
    authors = set(bundle.get("metadata", {}).get("accountable_author_ids", []))
    return bool(confirmations and isinstance(audit, Mapping)
                and audit.get("status") == "confirmed"
                and audit.get("accountable_author_id") in authors
                and audit.get("formula") and audit.get("input_unit") and audit.get("output_unit")
                and audit.get("verifier_agent_id"))


def audit_by_intended_use(config: Mapping[str, Any], registry: Mapping[str, Any],
                          evidence_bundle: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Return development coverage and an explicit production blocker list."""
    development = check_parameter_registry(config, registry, use="development_simulation")
    blockers: list[str] = []
    for record in registry["records"]:
        kind = record["parameter_kind"]
        if kind in {"calibration", "comparator_input"} and not (
                record["provenance_class"] in {"E1", "E2"}
                and record["approval_status"] == "verified_executable"
                and "production_calibration" in record["permitted_uses"]
                and _evidence_link_verified(record, evidence_bundle)):
            blockers.append(str(record["id"]))
        elif kind == "design_control" and not (
                record["approval_status"] == "preregistered"
                and "production_decision_rule" in record["permitted_uses"]):
            blockers.append(str(record["id"]))
    return {"development_parameter_count": len(development),
            "development_status": "permitted_illustrative",
            "production_calibration_status": "hard_stop" if blockers else "eligible",
            "production_blocking_registry_ids": sorted(blockers)}
