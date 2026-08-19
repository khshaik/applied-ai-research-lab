"""Configuration loading and a dependency-free validator for the frozen schema.

The validator implements the structural and numeric JSON Schema keywords used
by ``research/design/03b_simulation_schema.json``. Cross-reference invariants are checked in a
second pass. Full standards validation remains a preregistration hard stop.
"""
from __future__ import annotations

import json
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Any

try:  # PyYAML is convenient but deliberately not required by the prototype.
    import yaml  # type: ignore
except ImportError:  # JSON is a strict subset of YAML 1.2.
    yaml = None


class ConfigError(ValueError):
    pass


def load_config(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        value = yaml.safe_load(handle) if yaml is not None else json.load(handle)
    if not isinstance(value, dict):
        raise ConfigError("configuration root must be an object")
    return value


def validate_config(config: dict[str, Any], schema_path: str | Path) -> None:
    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    errors: list[str] = []

    def resolve(ref: str) -> dict[str, Any]:
        if not ref.startswith("#/"):
            raise ConfigError(f"unsupported external $ref: {ref}")
        node: Any = schema
        try:
            for part in ref[2:].split("/"):
                node = node[part.replace("~1", "/").replace("~0", "~")]
        except (KeyError, TypeError) as exc:
            raise ConfigError(f"unresolvable local $ref: {ref}") from exc
        if not isinstance(node, dict):
            raise ConfigError(f"$ref does not resolve to a schema object: {ref}")
        return node

    def valid_datetime(value: str) -> bool:
        """Accept RFC 3339 date-times with an explicit UTC offset."""
        try:
            parsed = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
        except ValueError:
            return False
        return "T" in value and parsed.tzinfo is not None

    def check(value: Any, rule: dict[str, Any], loc: str) -> None:
        if "$ref" in rule:
            check(value, resolve(rule["$ref"]), loc)
            return
        if "oneOf" in rule:
            hits = 0
            for choice in rule["oneOf"]:
                before = len(errors)
                check(value, choice, loc)
                if len(errors) == before:
                    hits += 1
                else:
                    del errors[before:]
            if hits != 1:
                errors.append(f"{loc}: expected exactly one oneOf match, got {hits}")
            return
        allowed_types = rule.get("type")
        if allowed_types:
            allowed_types = [allowed_types] if isinstance(allowed_types, str) else allowed_types
            predicates = {
                "object": lambda x: isinstance(x, dict), "array": lambda x: isinstance(x, list),
                "string": lambda x: isinstance(x, str), "number": lambda x: isinstance(x, (int, float)) and not isinstance(x, bool),
                "integer": lambda x: isinstance(x, int) and not isinstance(x, bool), "boolean": lambda x: isinstance(x, bool),
                "null": lambda x: x is None,
            }
            if not any(predicates[t](value) for t in allowed_types):
                errors.append(f"{loc}: expected {allowed_types}, got {type(value).__name__}")
                return
        if "const" in rule and value != rule["const"]:
            errors.append(f"{loc}: expected constant {rule['const']!r}")
        if "enum" in rule and value not in rule["enum"]:
            errors.append(f"{loc}: {value!r} is not in {rule['enum']!r}")
        if isinstance(value, dict):
            for key in rule.get("required", []):
                if key not in value:
                    errors.append(f"{loc}: missing required property {key!r}")
            props = rule.get("properties", {})
            if rule.get("additionalProperties") is False:
                for key in value.keys() - props.keys():
                    errors.append(f"{loc}: unexpected property {key!r}")
            for key, item in value.items():
                if key in props:
                    check(item, props[key], f"{loc}.{key}")
        if isinstance(value, list):
            if len(value) < rule.get("minItems", 0): errors.append(f"{loc}: too few items")
            if "maxItems" in rule and len(value) > rule["maxItems"]: errors.append(f"{loc}: too many items")
            if "items" in rule:
                for i, item in enumerate(value): check(item, rule["items"], f"{loc}[{i}]")
        if isinstance(value, str):
            if len(value) < rule.get("minLength", 0): errors.append(f"{loc}: string too short")
            if "pattern" in rule and re.fullmatch(rule["pattern"], value) is None: errors.append(f"{loc}: pattern mismatch")
            if rule.get("format") == "date-time" and not valid_datetime(value):
                errors.append(f"{loc}: invalid RFC 3339 date-time")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if not math.isfinite(value): errors.append(f"{loc}: number must be finite")
            if "minimum" in rule and value < rule["minimum"]: errors.append(f"{loc}: below minimum")
            if "maximum" in rule and value > rule["maximum"]: errors.append(f"{loc}: above maximum")
            if "exclusiveMinimum" in rule and value <= rule["exclusiveMinimum"]: errors.append(f"{loc}: below exclusive minimum")
            if "exclusiveMaximum" in rule and value >= rule["exclusiveMaximum"]: errors.append(f"{loc}: above exclusive maximum")

    check(config, schema, "$")
    if errors:
        raise ConfigError("configuration does not conform:\n" + "\n".join(errors))


def cross_validate(config: dict[str, Any]) -> None:
    """Validate references and semantic invariants not expressed by the schema."""
    ids: dict[str, set[str]] = {}
    id_fields = (
        "provenance_registry", "role_pools", "lifecycle_stages", "gate_definitions",
        "evidence_definitions", "work_item_templates", "arrival_models", "dependency_models",
        "demand_models", "capacity_calendars", "readiness_models", "rework_models",
        "quality_models", "mechanisms", "data_generating_worlds", "comparators",
        "verification_tests",
    )
    for field in id_fields:
        records = config.get(field, [])
        ids[field] = {x["id"] for x in records}
        if len(ids[field]) != len(records):
            raise ConfigError(f"duplicate id in {field}")

    def require(ref: str | None, valid: set[str], context: str) -> None:
        if ref is not None and ref not in valid:
            raise ConfigError(f"unknown reference {ref!r} in {context}")

    def require_all(refs: list[str], valid: set[str], context: str) -> None:
        for ref in refs:
            require(ref, valid, context)

    provenance = ids["provenance_registry"]
    stages, roles = ids["lifecycle_stages"], ids["role_pools"]
    gates, evidence = ids["gate_definitions"], ids["evidence_definitions"]
    templates, dependencies = ids["work_item_templates"], ids["dependency_models"]
    calendars, worlds = ids["capacity_calendars"], ids["data_generating_worlds"]

    distributions: set[str] = set()
    for demand in config["demand_models"]:
        dist_id = demand["base_distribution"]["id"]
        if dist_id in distributions:
            raise ConfigError(f"duplicate distribution id {dist_id!r}")
        distributions.add(dist_id)

    if config["time_model"]["warmup"] > config["time_model"]["horizon"]:
        raise ConfigError("time_model.warmup cannot exceed horizon")
    if config["time_model"]["unit"] != "hours":
        raise ConfigError("minimum production scope requires time_model.unit='hours'")

    for role in config["role_pools"]:
        require(role["capacity_calendar_id"], calendars, f"role pool {role['id']}")
        require_all(role["stage_eligibility"], stages, f"role pool {role['id']} stage_eligibility")
        require(role.get("setup_penalty_distribution_id"), distributions, f"role pool {role['id']}")
        if role["queue_discipline"] != "FIFO":
            raise ConfigError(f"role pool {role['id']}: only FIFO is supported")
        if role.get("preemption_policy", "none") != "none":
            raise ConfigError(f"role pool {role['id']}: preemption is unsupported")
        if role.get("setup_penalty_distribution_id") is not None:
            raise ConfigError(f"role pool {role['id']}: setup penalties are unsupported")
        if role["initial_backlog"] != 0:
            raise ConfigError(f"role pool {role['id']}: initial_backlog must be zero")
    for stage_index, stage in enumerate(config["lifecycle_stages"]):
        require_all(stage["eligible_role_pool_ids"], roles, f"stage {stage['id']}")
        require_all(stage["entry_prerequisite_ids"], stages, f"stage {stage['id']} prerequisites")
        require(stage.get("gate_id"), gates, f"stage {stage['id']}")
        if stage["parallelization_policy"] != "single_role":
            raise ConfigError(f"stage {stage['id']}: only single_role is supported")
        expected_prerequisites = [] if stage_index == 0 else [config["lifecycle_stages"][stage_index - 1]["id"]]
        if stage["entry_prerequisite_ids"] != expected_prerequisites:
            raise ConfigError(f"stage {stage['id']}: prerequisites must encode the sequential stage order")
        expected_release = "none" if stage_index == 0 else "after_predecessor"
        if stage.get("dependency_release_rule", expected_release) != expected_release:
            raise ConfigError(f"stage {stage['id']}: unsupported dependency_release_rule")

    stages_by_id = {stage["id"]: stage for stage in config["lifecycle_stages"]}
    gates_by_id = {gate["id"]: gate for gate in config["gate_definitions"]}
    for stage in config["lifecycle_stages"]:
        gate_id = stage.get("gate_id")
        if gate_id is not None and gates_by_id[gate_id]["stage_id"] != stage["id"]:
            raise ConfigError(
                f"stage {stage['id']} gate_id {gate_id!r} points to gate assigned to "
                f"stage {gates_by_id[gate_id]['stage_id']!r}"
            )

    for gate in config["gate_definitions"]:
        require(gate["stage_id"], stages, f"gate {gate['id']}")
        owning_stage = stages_by_id[gate["stage_id"]]
        if owning_stage.get("gate_id") != gate["id"]:
            raise ConfigError(
                f"gate {gate['id']} is assigned to stage {gate['stage_id']!r}, but that "
                f"stage declares gate_id {owning_stage.get('gate_id')!r}"
            )
        require(gate["accountable_role_pool_id"], roles, f"gate {gate['id']}")
        require_all(gate["required_evidence_ids"], evidence, f"gate {gate['id']} evidence")
        require(gate["evaluation_demand_distribution_id"], distributions, f"gate {gate['id']}")
        allowed_states = gate["allowed_states"]
        if not allowed_states or len(set(allowed_states)) != len(allowed_states):
            raise ConfigError(f"gate {gate['id']} allowed_states must be nonempty and unique")
        missing_transitions = set(allowed_states) - set(gate["transitions"])
        if missing_transitions:
            raise ConfigError(
                f"gate {gate['id']} lacks transitions for allowed states "
                f"{sorted(missing_transitions)}"
            )
        for decision, destination in gate["transitions"].items():
            if decision not in gate["allowed_states"]:
                raise ConfigError(f"gate {gate['id']} transition {decision!r} is not an allowed state")
            if destination not in {
                "next", "advance", "rework", "terminal", "terminal_with_risk", "terminal_failure"
            }:
                require(destination, stages, f"gate {gate['id']} transition {decision}")

    for template in config["work_item_templates"]:
        require_all(template["required_gate_ids"], gates, f"work item template {template['id']}")
        require_all(template["dependency_ids"], dependencies, f"work item template {template['id']}")
        for name, rating in template["pdd_profile"].items():
            require_all(rating["evidence_ids"], evidence, f"work item template {template['id']} PDD {name}")

    for dependency in config["dependency_models"]:
        expected_policy = {
            "cycles_allowed_for_test": False,
            "release_rule": "all_predecessor_items_completed_successfully",
            "failure_policy": "block_successor",
            "scope": "template_all_to_all",
        }
        for field, expected in expected_policy.items():
            if dependency.get(field) != expected:
                raise ConfigError(
                    f"dependency model {dependency['id']}: {field} must equal {expected!r}"
                )
        for edge_number, edge in enumerate(dependency["edges"]):
            require_all(
                edge,
                templates,
                f"dependency model {dependency['id']} edge {edge_number} endpoints",
            )
            successor = edge[1]
            successor_template = next(t for t in config["work_item_templates"] if t["id"] == successor)
            if dependency["id"] not in successor_template["dependency_ids"]:
                raise ConfigError(
                    f"dependency model {dependency['id']} edge {edge_number} would be ignored by successor {successor}"
                )
    incoming_models = {
        (dependency["id"], edge[1])
        for dependency in config["dependency_models"]
        for edge in dependency["edges"]
    }
    for template in config["work_item_templates"]:
        for dependency_id in template["dependency_ids"]:
            if (dependency_id, template["id"]) not in incoming_models:
                raise ConfigError(
                    f"template {template['id']} references dependency model {dependency_id} without an incoming edge"
                )
    graph = {template_id: set() for template_id in templates}
    for dependency in config["dependency_models"]:
        for predecessor, successor in dependency["edges"]:
            graph[successor].add(predecessor)
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit_dependency(node: str) -> None:
        if node in visiting:
            raise ConfigError("dependency graph contains a cycle")
        if node in visited:
            return
        visiting.add(node)
        for predecessor in graph[node]:
            visit_dependency(predecessor)
        visiting.remove(node)
        visited.add(node)

    for template_id in sorted(graph):
        visit_dependency(template_id)

    for demand in config["demand_models"]:
        require(demand["stage_id"], stages, f"demand {demand['id']}")
        require(demand["role_pool_id"], roles, f"demand {demand['id']}")
        require(demand["work_item_selector"], templates, f"demand {demand['id']}")
        require(demand["provenance_id"], provenance, f"demand {demand['id']}")
        require(demand["base_distribution"]["provenance_id"], provenance, f"distribution {demand['base_distribution']['id']}")
        _validate_distribution(demand["base_distribution"], demand["id"])
        if demand["base_distribution"]["family"] == "mixture":
            raise ConfigError(f"demand {demand['id']}: mixture distributions are unsupported")

    for calendar in config["capacity_calendars"]:
        require(calendar["provenance_id"], provenance, f"capacity calendar {calendar['id']}")
        parsed_intervals: list[tuple[datetime, datetime]] = []
        for i, interval in enumerate(calendar["intervals"]):
            total_unavailable = interval["absence_hours"] + interval["nonproject_hours"]
            if total_unavailable > interval["gross_hours"]:
                raise ConfigError(f"capacity calendar {calendar['id']} interval {i}: unavailable hours exceed gross hours")
            if interval["effective_hours"] > interval["gross_hours"]:
                raise ConfigError(f"capacity calendar {calendar['id']} interval {i}: effective hours exceed gross hours")
            expected_effective = interval["gross_hours"] - total_unavailable
            if abs(interval["effective_hours"] - expected_effective) > 1e-12:
                raise ConfigError(
                    f"capacity calendar {calendar['id']} interval {i}: effective_hours must equal "
                    "gross_hours - absence_hours - nonproject_hours"
                )
            start = _parse_datetime(interval["start"], f"capacity calendar {calendar['id']} interval {i} start")
            end = _parse_datetime(interval["end"], f"capacity calendar {calendar['id']} interval {i} end")
            if end <= start:
                raise ConfigError(f"capacity calendar {calendar['id']} interval {i}: end must follow start")
            elapsed_hours = (end - start).total_seconds() / 3600.0
            if (abs(interval["gross_hours"] - elapsed_hours) > 1e-9
                    or abs(interval["effective_hours"] - elapsed_hours) > 1e-9
                    or interval["absence_hours"] != 0
                    or interval["nonproject_hours"] != 0):
                raise ConfigError(
                    f"capacity calendar {calendar['id']} interval {i}: must be an explicit fully "
                    "available window; encode closures as blackouts"
                )
            parsed_intervals.append((start, end))
        parsed_intervals.sort()
        if any(current[0] < prior[1] for prior, current in zip(parsed_intervals, parsed_intervals[1:])):
            raise ConfigError(f"capacity calendar {calendar['id']}: intervals must not overlap")
        for i, blackout in enumerate(calendar.get("blackout_periods", [])):
            start = _parse_datetime(blackout["start"], f"capacity calendar {calendar['id']} blackout {i} start")
            end = _parse_datetime(blackout["end"], f"capacity calendar {calendar['id']} blackout {i} end")
            if end <= start:
                raise ConfigError(f"capacity calendar {calendar['id']} blackout {i}: end must follow start")
            if not any(interval_start <= start and end <= interval_end
                       for interval_start, interval_end in parsed_intervals):
                raise ConfigError(f"capacity calendar {calendar['id']} blackout {i}: must be contained in one availability window")

    for field in ("readiness_models", "mechanisms"):
        for record in config.get(field, []):
            require(record["provenance_id"], provenance, f"{field} {record['id']}")

    for model in config["rework_models"]:
        require(model["from_gate_id"], gates, f"rework model {model['id']}")
        require(model["provenance_id"], provenance, f"rework model {model['id']}")
        total = sum(route["probability"] for route in model["routes"])
        if not math.isfinite(total) or abs(total - 1.0) > 1e-12:
            raise ConfigError(f"rework probabilities for {model['id']} sum to {total}")
        for route in model["routes"]:
            require(route["destination_stage_id"], stages, f"rework model {model['id']} destination")
            require_all(route["additional_demand_distribution_ids"], distributions, f"rework model {model['id']} additional demand")

    for world in config["data_generating_worlds"]:
        truth = world["truth_parameters"]
        for key in ("gate_fail_probability", "gate_conditional_probability"):
            if key in truth and (not _finite_number(truth[key]) or not 0 <= truth[key] <= 1):
                raise ConfigError(f"world {world['id']} {key} must be a probability in [0, 1]")
        failure = truth.get("gate_fail_probability", 0)
        conditional = truth.get("gate_conditional_probability", 0)
        if failure + conditional > 1:
            raise ConfigError(f"world {world['id']} gate outcome probabilities exceed 1")
        if "service_multiplier" in truth and (not _finite_number(truth["service_multiplier"]) or truth["service_multiplier"] <= 0):
            raise ConfigError(f"world {world['id']} service_multiplier must be positive")

    design = config["experimental_design"]
    require_all(design["development_world_ids"], worlds, "experimental_design.development_world_ids")
    require_all(design["locked_evaluation_world_ids"], worlds, "experimental_design.locked_evaluation_world_ids")
    overlap = set(design["development_world_ids"]) & set(design["locked_evaluation_world_ids"])
    if overlap:
        raise ConfigError(f"development and locked evaluation worlds overlap: {sorted(overlap)}")

    streams = config["randomization"]["child_streams"]
    if any(not isinstance(seed, int) or isinstance(seed, bool) or seed < 0 for seed in streams.values()):
        raise ConfigError("randomization.child_streams must contain nonnegative integer seeds")
    if len(set(streams.values())) != len(streams):
        raise ConfigError("randomization.child_streams seeds must be unique")

    for arrival in config["arrival_models"]:
        if arrival["type"] != "fixed_portfolio":
            raise ConfigError(f"arrival model {arrival['id']}: only fixed_portfolio is supported")
        if arrival["initial_wip"]:
            raise ConfigError(f"arrival model {arrival['id']}: initial_wip is unsupported")
        parameters = arrival["parameters"]
        if "count" in parameters and (not isinstance(parameters["count"], int) or isinstance(parameters["count"], bool) or parameters["count"] < 0):
            raise ConfigError(f"arrival model {arrival['id']} count must be a nonnegative integer")
        for key in ("start", "spacing", "interarrival", "duration"):
            if key in parameters and (not _finite_number(parameters[key]) or parameters[key] < 0):
                raise ConfigError(f"arrival model {arrival['id']} {key} must be nonnegative")


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _parse_datetime(value: str, context: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"{context}: invalid RFC 3339 date-time") from exc
    if parsed.tzinfo is None:
        raise ConfigError(f"{context}: date-time must include a UTC offset")
    return parsed


def _validate_distribution(distribution: dict[str, Any], context: str) -> None:
    """Reject invalid duration domains before they reach the sampler."""
    family = distribution["family"]
    parameters = distribution["parameters"]

    def number(name: str, *, positive: bool = False, nonnegative: bool = False) -> float:
        if name not in parameters or not _finite_number(parameters[name]):
            raise ConfigError(f"distribution {distribution['id']} in {context}: {name} must be finite numeric")
        value = float(parameters[name])
        if positive and value <= 0:
            raise ConfigError(f"distribution {distribution['id']} in {context}: {name} must be positive")
        if nonnegative and value < 0:
            raise ConfigError(f"distribution {distribution['id']} in {context}: {name} must be nonnegative")
        return value

    if family == "fixed":
        number("value", nonnegative=True)
    elif family == "triangular":
        low = number("low", nonnegative=True)
        mode = number("mode", nonnegative=True)
        high = number("high", nonnegative=True)
        if not low <= mode <= high:
            raise ConfigError(f"distribution {distribution['id']} in {context}: require low <= mode <= high")
    elif family == "lognormal":
        number("mu")
        number("sigma", nonnegative=True)
    elif family in {"gamma", "weibull"}:
        number("shape", positive=True)
        number("scale", positive=True)

    for domain_name in ("support", "truncation"):
        if domain_name in distribution:
            domain = distribution[domain_name]
            if any(not _finite_number(value) for value in domain) or domain[0] < 0 or domain[0] > domain[1]:
                raise ConfigError(f"distribution {distribution['id']} in {context}: invalid nonnegative {domain_name}")


def load_and_validate(path: str | Path, schema_path: str | Path) -> dict[str, Any]:
    config = load_config(path)
    validate_config(config, schema_path)
    cross_validate(config)
    return config
