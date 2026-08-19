"""Development-only synthetic scenario pipeline.

This module deliberately derives only ``development`` seed streams.  It never
loads or accepts the locked-evaluation seed manifest.  Outputs are synthetic
engineering evidence, not validation of human cognition or organizational use.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean
from typing import Any, Iterable, Mapping, Sequence

from .comparators import ComparatorSuite
from .config import load_and_validate
from .engine import SimulationResult, run_truth
from .evaluation import bottleneck_accuracy, evaluate_forecasts
from .scheduling import compile_capacity_calendars
from .seeds import derive_seed


INTERPRETATION_BOUNDARY = (
    "Developmental synthetic mechanism evidence only; not empirical validation "
    "of human cognitive load, organizational delivery, or causal AI effects."
)

PROVENANCE_SOURCE_FILES = (
    "comparators.py",
    "config.py",
    "development_pipeline.py",
    "engine.py",
    "evaluation.py",
    "scheduling.py",
    "seeds.py",
)


@dataclass(frozen=True)
class DevelopmentScenario:
    scenario_id: str
    world_id: str
    family: str
    changes: Mapping[str, Any]
    purpose: str


def development_scenarios() -> tuple[DevelopmentScenario, ...]:
    """Prespecified development, sensitivity, recovery, and edge fixtures.

    All fixtures use worlds declared as development worlds in the example
    configuration.  No locked-evaluation world is referenced.
    """
    return (
        DevelopmentScenario("baseline_sp", "world_sp", "development", {}, "SP-sufficient sanity world"),
        DevelopmentScenario("baseline_hie", "world_hie", "development", {}, "task/oversight sanity world"),
        DevelopmentScenario("baseline_bottleneck", "world_bottleneck", "development", {}, "cross-role queue world"),
        DevelopmentScenario("review_capacity_low", "world_bottleneck", "sensitivity", {"reviewer_servers": 1, "arrival_count": 24}, "review queue stress"),
        DevelopmentScenario("review_capacity_high", "world_bottleneck", "sensitivity", {"reviewer_servers": 3, "arrival_count": 24}, "review capacity relief"),
        DevelopmentScenario("load_low", "world_bottleneck", "sensitivity", {"arrival_count": 6}, "portfolio-load lower bound"),
        DevelopmentScenario("load_high", "world_bottleneck", "sensitivity", {"arrival_count": 36}, "portfolio-load upper bound"),
        DevelopmentScenario("recovery_service_low", "world_bottleneck", "parameter_recovery", {"service_multiplier": 0.75}, "recover low service multiplier"),
        DevelopmentScenario("recovery_service_high", "world_bottleneck", "parameter_recovery", {"service_multiplier": 1.75}, "recover high service multiplier"),
        DevelopmentScenario("edge_no_rework", "world_sp", "edge", {"gate_fail_probability": 0.0, "gate_conditional_probability": 0.0}, "zero gate-rework boundary"),
        DevelopmentScenario("edge_severe_queue", "world_bottleneck", "adversarial_development", {"reviewer_servers": 1, "arrival_count": 48, "service_multiplier": 2.0}, "severe queue without locked adversarial world"),
    )


def _distribution_mean(dist: Mapping[str, Any]) -> float:
    family, p = dist["family"], dist["parameters"]
    if family == "fixed":
        value = float(p["value"])
    elif family == "triangular":
        value = (float(p["low"]) + float(p["mode"]) + float(p["high"])) / 3.0
    elif family == "lognormal":
        value = math.exp(float(p["mu"]) + float(p["sigma"]) ** 2 / 2.0)
    elif family == "gamma":
        value = float(p["shape"]) * float(p["scale"])
    elif family == "weibull":
        value = float(p["scale"]) * math.gamma(1.0 + 1.0 / float(p["shape"]))
    elif family == "empirical_discrete":
        values = [float(x) for x in p["values"]]
        weights = [float(x) for x in p.get("weights", [1.0] * len(values))]
        value = sum(x * w for x, w in zip(values, weights)) / sum(weights)
    else:
        raise ValueError(f"unsupported distribution family: {family}")
    if "truncation" in dist:
        value = max(float(dist["truncation"][0]), min(value, float(dist["truncation"][1])))
    return value


def configure_scenario(base: Mapping[str, Any], scenario: DevelopmentScenario) -> dict[str, Any]:
    config = copy.deepcopy(base)
    development_worlds = set(config["experimental_design"]["development_world_ids"])
    if scenario.world_id not in development_worlds:
        raise ValueError(f"scenario {scenario.scenario_id} references non-development world {scenario.world_id}")
    changes = dict(scenario.changes)
    config["arrival_models"][0]["parameters"]["count"] = int(
        changes.get("arrival_count", config["arrival_models"][0]["parameters"]["count"])
    )
    parameters = config["arrival_models"][0]["parameters"]
    if "template_ids" in parameters:
        count = int(parameters["count"])
        template_ids = [template["id"] for template in config["work_item_templates"]]
        parameters["template_ids"] = [template_ids[index % len(template_ids)] for index in range(count)]
    for role in config["role_pools"]:
        if role["id"] == "reviewers" and "reviewer_servers" in changes:
            role["concurrent_servers"] = int(changes["reviewer_servers"])
    world = next(w for w in config["data_generating_worlds"] if w["id"] == scenario.world_id)
    for key in ("service_multiplier", "gate_fail_probability", "gate_conditional_probability"):
        if key in changes:
            world["truth_parameters"][key] = float(changes[key])
    # Explicitly declared t0 estimates: permitted comparator information, not
    # runtime outcomes.  Deliberate shrinkage avoids an oracle-equivalent model.
    truth = world["truth_parameters"]
    world["comparator_information_policy"] = {
        "readiness_probability": max(0.05, 1.0 - 0.75 * float(truth.get("gate_fail_probability", 0.0))),
        "rework_probability": min(0.95, 0.75 * float(truth.get("gate_fail_probability", 0.0))),
        "status": "developmental_t0_proxy",
    }
    return config


def _actual_role_load(result: SimulationResult) -> dict[str, float]:
    loads: dict[str, float] = {}
    for row in result.services:
        loads[row.role_pool_id] = loads.get(row.role_pool_id, 0.0) + row.demand
    return loads


def comparator_input(config: Mapping[str, Any], world_id: str, result: SimulationResult,
                     true_completion_probability: float) -> dict[str, Any]:
    """Adapt t0 configuration plus oracle-only realized fields.

    Non-oracle fields are derived solely from the configuration.  Runtime data
    appears only in ``true_*`` fields and is consumed only by the oracle or
    scoring code.
    """
    templates = {template["id"]: template for template in config["work_item_templates"]}
    count = int(config["arrival_models"][0]["parameters"]["count"])
    horizon = float(config["time_model"]["horizon"])
    calendars = compile_capacity_calendars(config["capacity_calendars"], config["time_model"]["unit"])
    role_capacity: dict[str, float] = {}
    for role in config["role_pools"]:
        calendar = calendars[role["capacity_calendar_id"]]
        open_time = sum(max(0.0, min(window.end, horizon) - max(window.start, 0.0))
                        for window in calendar.windows)
        role_capacity[str(role["id"])] = (
            float(role["concurrent_servers"]) * float(calendar.concurrency) * open_time
        )
    if any(capacity <= 0 for capacity in role_capacity.values()):
        raise ValueError("all comparator role capacities must be positive within the horizon")

    parameters = config["arrival_models"][0]["parameters"]
    template_ids = parameters.get("template_ids")
    if template_ids is None:
        template_counts = {template["id"]: (count if index == 0 else 0)
                           for index, template in enumerate(config["work_item_templates"])}
    else:
        if len(template_ids) != count:
            raise ValueError("template_ids must contain one t0 template identifier per item")
        template_counts = {template_id: template_ids.count(template_id) for template_id in templates}
    role_demand = {role: 0.0 for role in role_capacity}
    role_stage_demand: dict[str, dict[str, float]] = {role: {} for role in role_capacity}
    for demand in config["demand_models"]:
        role = str(demand["role_pool_id"])
        stage = str(demand["stage_id"])
        modeled_count = template_counts.get(str(demand["work_item_selector"]), 0)
        total = modeled_count * _distribution_mean(demand["base_distribution"])
        role_demand[role] += total
        role_stage_demand[role][stage] = role_stage_demand[role].get(stage, 0.0) + total
    # Gate evaluation is distinct human touch demand at the accountable role.
    distributions = {d["base_distribution"]["id"]: d["base_distribution"]
                     for d in config["demand_models"]}
    for gate in config["gate_definitions"]:
        applicable_count = sum(
            template_counts[template_id]
            for template_id, record in templates.items()
            if record["risk_class"] in gate["risk_classes"]
            and (gate.get("mandatory", False) or gate["id"] in record["required_gate_ids"])
        )
        role = str(gate["accountable_role_pool_id"])
        stage = str(gate["stage_id"])
        total = applicable_count * _distribution_mean(
            distributions[gate["evaluation_demand_distribution_id"]]
        )
        role_demand[role] += total
        role_stage_demand[role][stage] = role_stage_demand[role].get(stage, 0.0) + total
    role_stage_demand = {role: stages for role, stages in role_stage_demand.items() if stages}
    role_stage_capacity = {
        role: {stage: role_capacity[role] for stage in stages}
        for role, stages in role_stage_demand.items()
    }
    points = sum(float(templates[template_id]["story_points"]) * template_count
                 for template_id, template_count in template_counts.items())
    implementation_demand = sum(
        template_counts.get(str(demand["work_item_selector"]), 0)
        * _distribution_mean(demand["base_distribution"])
        for demand in config["demand_models"]
        if demand["stage_id"] == "implementation"
    )
    if implementation_demand <= 0 or points <= 0:
        raise ValueError("Story Points comparator requires positive t0 points and implementation demand")
    developer_role = next(
        role for role in config["role_pools"] if "implementation" in role["stage_eligibility"]
    )["id"]
    point_budget = role_capacity[developer_role] * points / implementation_demand

    def weighted_template_field(extractor) -> float:
        if count == 0:
            return 0.0
        return sum(template_counts[template_id] * float(extractor(record))
                   for template_id, record in templates.items()) / count

    hie_context_load = weighted_template_field(lambda record: record["pdd_profile"]["iu"]["level"]) / 20.0
    hie_interaction_load = weighted_template_field(
        lambda record: record.get("hie_compatible_fields", {}).get("interaction_count", 0)
    ) / 20.0
    hie_oversight_load = weighted_template_field(
        lambda record: record.get("hie_compatible_fields", {}).get("oversight_level", 0)
    ) / 20.0
    policy = next(w for w in config["data_generating_worlds"] if w["id"] == world_id)["comparator_information_policy"]
    readiness = float(policy.get("readiness_probability", 0.85))
    rework = float(policy.get("rework_probability", 0.10))
    dependent_items = sum(
        template_counts[template_id]
        for template_id, record in templates.items()
        if record.get("dependency_ids")
    )
    dependency_exposure = dependent_items / count if count else 0.0
    dependency_block_probability = dependency_exposure * (1.0 - readiness * (1.0 - rework))
    return {
        "story_points": points,
        "story_point_budget": point_budget,
        "hie_context_load": hie_context_load,
        "hie_interaction_load": hie_interaction_load,
        "hie_oversight_load": hie_oversight_load,
        "role_demand": role_demand,
        "role_capacity": role_capacity,
        "role_stage_demand": role_stage_demand,
        "role_stage_capacity": role_stage_capacity,
        "readiness_probability": readiness,
        "rework_probability": rework,
        "dependency_block_probability": dependency_block_probability,
        "true_completion_probability": float(true_completion_probability),
        "true_role_load": _actual_role_load(result),
    }


def _write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _development_provenance(config: Mapping[str, Any]) -> dict[str, Any]:
    """Return deterministic code/config provenance without VCS assumptions."""
    package = Path(__file__).resolve().parent
    source_hashes = {
        name: hashlib.sha256((package / name).read_bytes()).hexdigest()
        for name in PROVENANCE_SOURCE_FILES
    }
    implementation_payload = json.dumps(
        source_hashes, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    config_payload = json.dumps(
        config, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return {
        "configuration_sha256": hashlib.sha256(config_payload).hexdigest(),
        "implementation_sha256": hashlib.sha256(implementation_payload).hexdigest(),
        "source_file_sha256": source_hashes,
    }


def run_development_pipeline(config: Mapping[str, Any], output_dir: str | Path,
                             *, replications: int = 24,
                             scenarios: Iterable[DevelopmentScenario] | None = None) -> dict[str, Any]:
    if replications < 2:
        raise ValueError("replications must be >= 2")
    selected = tuple(scenarios or development_scenarios())
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    suite = ComparatorSuite()
    master = int(config["randomization"]["master_seed"])
    seeds = tuple(derive_seed(master, "development", i) for i in range(replications))
    run_rows: list[dict[str, Any]] = []
    item_rows: list[dict[str, Any]] = []
    score_rows: list[dict[str, Any]] = []
    recovery_rows: list[dict[str, Any]] = []

    for scenario in selected:
        scenario_config = configure_scenario(config, scenario)
        results = [run_truth(scenario_config, scenario.world_id, seed) for seed in seeds]
        all_items = [item for result in results for item in result.items]
        completion_rate = sum(item.terminal_state == "completed" for item in all_items) / len(all_items)
        forecasts: dict[str, list[float]] = {name: [] for name in suite.names}
        outcomes: list[int] = []
        bottlenecks: dict[str, list[str | None]] = {name: [] for name in suite.names}
        actual_bottlenecks: list[str] = []
        for result in results:
            adapter = comparator_input(scenario_config, scenario.world_id, result, completion_rate)
            prediction = suite.forecast(adapter)
            actual_role = suite.predicted_bottleneck(adapter, "oracle")
            completed = sum(item.terminal_state == "completed" for item in result.items)
            run_rows.append({
                "status": "developmental_synthetic", "scenario_id": scenario.scenario_id,
                "family": scenario.family, "world_id": scenario.world_id,
                "seed_namespace": "development", "seed": result.metadata["seed"],
                "run_id": result.run_id, "digest": result.digest(),
                "items": len(result.items), "completed": completed,
                "failed": sum(item.terminal_state == "failed" for item in result.items),
                "censored": sum(item.terminal_state == "censored" for item in result.items),
            })
            for item in result.items:
                outcome = int(item.terminal_state == "completed")
                outcomes.append(outcome)
                actual_bottlenecks.append(str(actual_role))
                row = {"status": "developmental_synthetic", "scenario_id": scenario.scenario_id,
                       "run_id": result.run_id, "item_id": item.item_id, "outcome_completed": outcome}
                for model, probability in prediction.items():
                    forecasts[model].append(probability)
                    row[model] = probability
                    bottlenecks[model].append(suite.predicted_bottleneck(adapter, model))
                item_rows.append(row)
        scores = evaluate_forecasts(forecasts, outcomes, strongest_deployable="story_points", bins=5)
        for model, values in scores.items():
            bn = bottleneck_accuracy(bottlenecks[model], actual_bottlenecks)
            score_rows.append({
                "status": "developmental_synthetic", "scenario_id": scenario.scenario_id,
                "family": scenario.family, "model": model,
                "n": len(outcomes), "brier_score": values["brier_score"],
                "log_loss": values["log_loss"], "ece": values["ece"],
                "relative_brier_skill_vs_story_points": values["relative_brier_skill"],
                "bottleneck_accuracy": bn["accuracy"], "bottleneck_eligible_n": bn["eligible_n"],
                "bottleneck_abstained_n": bn["abstained_n"],
            })
        if scenario.family == "parameter_recovery":
            base_mean = mean(_distribution_mean(d["base_distribution"]) for d in scenario_config["demand_models"])
            observed_mean = mean(row.demand for result in results for row in result.services if row.kind == "service")
            expected = float(next(w for w in scenario_config["data_generating_worlds"] if w["id"] == scenario.world_id)["truth_parameters"]["service_multiplier"])
            recovery_rows.append({"status": "developmental_synthetic", "scenario_id": scenario.scenario_id,
                                  "target_multiplier": expected, "recovered_multiplier": observed_mean / base_mean,
                                  "absolute_error": abs(observed_mean / base_mean - expected)})

    _write_csv(output / "run_manifest.csv", run_rows)
    _write_csv(output / "item_forecasts.csv", item_rows)
    _write_csv(output / "comparator_scores.csv", score_rows)
    _write_csv(output / "parameter_recovery.csv", recovery_rows)
    output_names = ["run_manifest.csv", "item_forecasts.csv", "comparator_scores.csv", "parameter_recovery.csv"]
    output_checksums = {
        name: hashlib.sha256((output / name).read_bytes()).hexdigest()
        for name in output_names
    }
    manifest_core = {
        "manifest_version": "0.2.0-development", "status": "developmental_synthetic",
        "interpretation_boundary": INTERPRETATION_BOUNDARY,
        "seed_policy": {"namespace": "development", "count": replications,
                        "locked_evaluation_seeds_accessed": False},
        "scenario_ids": [s.scenario_id for s in selected],
        "scenario_definitions": [asdict(s) for s in selected],
        "outputs": output_names,
        "output_sha256": output_checksums,
        "provenance": _development_provenance(config),
    }
    manifest_core["content_checksum"] = hashlib.sha256(
        json.dumps(manifest_core, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    (output / "development_manifest.json").write_text(json.dumps(manifest_core, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"manifest": manifest_core, "run_rows": run_rows, "score_rows": score_rows,
            "item_rows": item_rows, "recovery_rows": recovery_rows}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="simulation/configs/example.yaml")
    parser.add_argument("--schema", default="research/design/03b_simulation_schema.json")
    parser.add_argument("--output", default="simulation/output/development")
    parser.add_argument("--replications", type=int, default=24)
    args = parser.parse_args(argv)
    config = load_and_validate(args.config, args.schema)
    result = run_development_pipeline(config, args.output, replications=args.replications)
    print(json.dumps({"status": result["manifest"]["status"],
                      "scenarios": len(result["manifest"]["scenario_ids"]),
                      "runs": len(result["run_rows"]), "output": str(Path(args.output))}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
