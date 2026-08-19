"""Development-only Gate 4B mechanism-ablation analysis.

Consumes already generated development observations. It rejects locked worlds
and has no seed-manifest interface.
"""
from __future__ import annotations

import csv
import copy
from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any, Callable, Mapping, Sequence

from .engine import SimulationResult, run_truth
from .seeds import derive_seed


DEVELOPMENT_STATUS = "developmental_synthetic_not_locked_evaluation"
OUTPUT_CONTRACT = {
    "ablation_manifest.json": {"manifest_version", "status", "development_world_ids", "mechanisms",
                               "interpretation_boundary", "pair_count", "effect_count",
                               "implementation_sha256"},
    "ablation_pairs.csv": {"world_id", "configuration_id", "mechanism_id", "mechanism_state",
                           "replication_id", "seed_namespace", "primary_metric", "bottleneck_accuracy",
                           "config_sha256", "changed_paths", "status"},
    "ablation_effects.csv": {"configuration_id", "mechanism_id", "n", "primary_delta", "bottleneck_delta", "status"},
    "ablation_receipt.json": {"status", "files"},
}

MECHANISMS = ("queues", "readiness", "dependencies", "multi_role_structure")


@dataclass(frozen=True)
class MechanismMutation:
    mechanism_id: str
    changed_paths: tuple[str, ...]


def _canonical_hash(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _changed_paths(before: Any, after: Any, prefix: str = "$") -> tuple[str, ...]:
    paths: list[str] = []
    if type(before) is not type(after):
        return (prefix,)
    if isinstance(before, Mapping):
        for key in sorted(set(before) | set(after)):
            path = f"{prefix}.{key}"
            if key not in before or key not in after:
                paths.append(path)
            else:
                paths.extend(_changed_paths(before[key], after[key], path))
    elif isinstance(before, list):
        if len(before) != len(after):
            paths.append(prefix)
        else:
            for index, (left, right) in enumerate(zip(before, after)):
                paths.extend(_changed_paths(left, right, f"{prefix}[{index}]"))
    elif before != after:
        paths.append(prefix)
    return tuple(paths)


def ablate_configuration(config: Mapping[str, Any], mechanism_id: str) -> tuple[dict[str, Any], MechanismMutation]:
    """Return a copy with exactly one logical delivery mechanism disabled."""
    if mechanism_id not in MECHANISMS:
        raise ValueError(f"unsupported Gate 4B mechanism: {mechanism_id}")
    result = copy.deepcopy(config)
    if mechanism_id == "queues":
        count = int(result["arrival_models"][0]["parameters"]["count"])
        for role in result["role_pools"]:
            role["concurrent_servers"] = max(1, count)
    elif mechanism_id == "readiness":
        # Remove evidence-readiness as a release constraint while preserving
        # gates, evaluation work, outcomes, and every other mechanism.
        for gate in result["gate_definitions"]:
            gate["required_evidence_ids"] = []
    elif mechanism_id == "dependencies":
        result["dependency_models"] = []
        for template in result["work_item_templates"]:
            template["dependency_ids"] = []
    else:  # multi_role_structure
        anchor = str(result["role_pools"][0]["id"])
        all_stages = [str(stage["id"]) for stage in result["lifecycle_stages"]]
        anchor_record = next(role for role in result["role_pools"] if role["id"] == anchor)
        anchor_record["stage_eligibility"] = all_stages
        anchor_record["concurrent_servers"] = sum(int(role["concurrent_servers"])
                                                   for role in result["role_pools"])
        result["role_pools"] = [anchor_record]
        for stage in result["lifecycle_stages"]:
            stage["eligible_role_pool_ids"] = [anchor]
        for gate in result["gate_definitions"]:
            gate["accountable_role_pool_id"] = anchor
        for demand in result["demand_models"]:
            demand["role_pool_id"] = anchor
    changes = _changed_paths(config, result)
    if not changes:
        raise ValueError(f"mechanism ablation {mechanism_id} made no configuration change")
    return result, MechanismMutation(mechanism_id, changes)


def _metrics(result: SimulationResult) -> tuple[float, float]:
    if not result.items:
        raise ValueError("ablation run returned no items")
    primary = 1.0 - sum(item.terminal_state == "completed" for item in result.items) / len(result.items)
    loads: dict[str, float] = {}
    for row in result.services:
        loads[row.role_pool_id] = loads.get(row.role_pool_id, 0.0) + float(row.demand)
    total = sum(loads.values())
    concentration = max(loads.values()) / total if total > 0 else 0.0
    return primary, concentration


RunCallable = Callable[[dict[str, Any], str, int], SimulationResult]


def generate_ablation_pairs(config: Mapping[str, Any], *, world_id: str,
                            replications: int, runner: RunCallable = run_truth,
                            seed_namespace: str = "development:g4b_ablation") -> list[dict[str, Any]]:
    """Execute same-seed baseline/ablation pairs in development worlds only."""
    development = set(config["experimental_design"]["development_world_ids"])
    locked = set(config["experimental_design"]["locked_evaluation_world_ids"])
    if world_id in locked or world_id not in development:
        raise ValueError("ablation generator accepts declared development worlds only")
    if not seed_namespace.startswith("development:") or "locked" in seed_namespace.lower() \
            or "evaluation" in seed_namespace.lower():
        raise ValueError("ablation seed namespace must be development-only")
    if replications < 2:
        raise ValueError("replications must be at least two")
    master = int(config["randomization"]["master_seed"])
    rows: list[dict[str, Any]] = []
    for mechanism_id in MECHANISMS:
        ablated, mutation = ablate_configuration(config, mechanism_id)
        for replication in range(replications):
            seed = derive_seed(master, seed_namespace, replication)
            for state, run_config in (("baseline", copy.deepcopy(config)), ("ablated", copy.deepcopy(ablated))):
                result = runner(run_config, world_id, seed)
                primary, bottleneck = _metrics(result)
                rows.append({
                    "world_id": world_id,
                    "configuration_id": f"g4b_development:{world_id}",
                    "mechanism_id": mechanism_id, "mechanism_state": state,
                    "replication_id": replication, "seed_namespace": seed_namespace,
                    "primary_metric": primary, "bottleneck_accuracy": bottleneck,
                    "config_sha256": _canonical_hash(run_config),
                    "changed_paths": json.dumps(mutation.changed_paths), "status": DEVELOPMENT_STATUS,
                })
    return rows


def evaluate_ablations(observations: Sequence[Mapping[str, Any]], *,
                       development_world_ids: Sequence[str],
                       locked_world_ids: Sequence[str]) -> list[dict[str, Any]]:
    development = set(development_world_ids); locked = set(locked_world_ids)
    if not observations:
        raise ValueError("development ablation observations cannot be empty")
    if development & locked:
        raise ValueError("development and locked worlds overlap")
    grouped: dict[tuple[str, str], dict[str, list[tuple[float, float]]]] = {}
    for row in observations:
        world = str(row["world_id"])
        if world in locked or world not in development:
            raise ValueError("ablation input contains a locked or undeclared development world")
        state = str(row["mechanism_state"])
        if state not in {"baseline", "ablated"}:
            raise ValueError("mechanism_state must be baseline or ablated")
        key = (str(row["configuration_id"]), str(row["mechanism_id"]))
        grouped.setdefault(key, {}).setdefault(state, []).append(
            (float(row["primary_metric"]), float(row["bottleneck_accuracy"]))
        )
    effects: list[dict[str, Any]] = []
    for (configuration, mechanism), states in sorted(grouped.items()):
        if set(states) != {"baseline", "ablated"} or len(states["baseline"]) != len(states["ablated"]):
            raise ValueError("every ablation requires paired baseline and ablated observations")
        baseline = states["baseline"]; ablated = states["ablated"]
        effects.append({
            "configuration_id": configuration, "mechanism_id": mechanism, "n": len(baseline),
            "primary_delta": sum(a[0] - b[0] for a, b in zip(ablated, baseline)) / len(baseline),
            "bottleneck_delta": sum(b[1] - a[1] for b, a in zip(baseline, ablated)) / len(baseline),
            "status": DEVELOPMENT_STATUS,
        })
    return effects


def publish_ablation(output_dir: str | Path, effects: Sequence[Mapping[str, Any]], *,
                     development_world_ids: Sequence[str],
                     pairs: Sequence[Mapping[str, Any]] | None = None) -> dict[str, Any]:
    target = Path(output_dir)
    if target.exists():
        raise ValueError("immutable development ablation output directory already exists")
    mechanisms = sorted({str(row["mechanism_id"]) for row in effects})
    pair_rows = list(pairs or [])
    manifest = {"manifest_version": "0.2.0-development",
                "status": DEVELOPMENT_STATUS,
                "development_world_ids": sorted(development_world_ids),
                "mechanisms": mechanisms,
                "pair_count": len(pair_rows), "effect_count": len(effects),
                "implementation_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
                "interpretation_boundary": "Development synthetic mechanism diagnostic only; not locked evidence."}
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{target.name}.staging-", dir=target.parent))
    try:
        manifest_path = staging / "ablation_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        effects_path = staging / "ablation_effects.csv"
        with effects_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=sorted(OUTPUT_CONTRACT["ablation_effects.csv"]))
            writer.writeheader(); writer.writerows(effects)
        pairs_path = staging / "ablation_pairs.csv"
        with pairs_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=sorted(OUTPUT_CONTRACT["ablation_pairs.csv"]))
            writer.writeheader(); writer.writerows(pair_rows)
        files = [{"path": path.name, "sha256": sha256(path.read_bytes()).hexdigest()}
                 for path in (manifest_path, effects_path, pairs_path)]
        receipt = {"status": "verified_developmental", "files": files}
        receipt_path = staging / "ablation_receipt.json"
        receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        os.replace(staging, target)
        return receipt
    except Exception:
        if staging.exists(): shutil.rmtree(staging)
        raise
