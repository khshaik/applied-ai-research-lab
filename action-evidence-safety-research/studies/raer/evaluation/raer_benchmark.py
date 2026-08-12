#!/usr/bin/env python3
"""Deterministic RAER-B96 evaluator using only an explicitly released partition."""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "calibration/benchmark/release_v1.1"
PLAN = ROOT / "evaluation/STATISTICAL_ANALYSIS_PLAN_v1.0.json"
POLICIES = ("STATIC", "CONTRACT_ONLY", "FIXED_0.10", "FIXED_0.20", "FIXED_0.35", "FIXED_0.50", "ALWAYS_REFRESH", "RAER")
TAU0, ALPHA, RHO, VERIFIER_FLOOR = 0.22, 0.30, 0.20, 0.01


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sigmoid(value: float) -> float:
    value = max(-35.0, min(35.0, value))
    return 1.0 / (1.0 + math.exp(-value))


def q_e0(item: dict) -> float:
    age = min(item["age_hours"] / item["validity_window_hours"], 2.0) / 2.0
    auth = min(item["authorization_age_hours"] / item["authorization_window_hours"], 2.0) / 2.0 if item["authorization_window_hours"] else 0.0
    features = (
        age,
        (item["source_volatility"] - 1) / 4.0,
        min(item["dependent_changes"], 4) / 4.0,
        (item["update_frequency"] - 1) / 4.0,
        (5 - item["source_reliability"]) / 4.0,
        auth,
        item["contradiction_strength"] / 3.0,
    )
    coefficients = (1.25, 0.85, 0.75, 0.45, 0.95, 1.15, 1.40)
    return sigmoid(-3.40 + sum(a * b for a, b in zip(coefficients, features)))


def action_harm(scores: dict) -> float:
    consequence = scores["consequence_score_1_5"]
    irreversibility = scores["irreversibility_score_1_5"]
    return (consequence / 5.0) * (0.5 + 0.5 * (irreversibility - 1) / 4.0)


def residual_risk(scenario: dict, checked: set[str], rho: float = RHO, alpha: float = ALPHA) -> float:
    survival = 1.0
    unchecked = []
    for item in scenario["evidence"]:
        q = VERIFIER_FLOOR if item["evidence_id"] in checked else item["q"]
        survival *= 1.0 - q * item["w"]
        if item["evidence_id"] not in checked:
            unchecked.append(item)
    risk = scenario["h"] * (1.0 - survival)
    group = set(scenario["correlation_group"])
    correlated_unchecked = [item for item in unchecked if item["evidence_id"] in group]
    if len(correlated_unchecked) >= 2:
        pair = max(
            math.sqrt(a["q"] * b["q"]) * min(a["w"], b["w"])
            for a, b in itertools.combinations(correlated_unchecked, 2)
        )
        risk += scenario["h"] * rho * pair
    return min(scenario["h"], risk)


def subsets(items: list[dict]):
    for size in range(len(items) + 1):
        yield from itertools.combinations(items, size)


def raer_checks(scenario: dict, tau0: float = TAU0, alpha: float = ALPHA, rho: float = RHO) -> tuple[list[dict], float, bool]:
    threshold = tau0 * (1.0 - alpha * scenario["h"])
    candidates = []
    for subset in subsets(scenario["evidence"]):
        cost = sum(row["cost"] for row in subset)
        if cost <= scenario["budget"] + 1e-12:
            risk = residual_risk(scenario, {row["evidence_id"] for row in subset}, rho, alpha)
            candidates.append((list(subset), cost, risk))
    if not candidates:
        return [], threshold, False
    feasible = [row for row in candidates if row[2] <= threshold + 1e-12]
    if feasible:
        chosen = min(feasible, key=lambda row: (row[1], row[2], tuple(x["evidence_id"] for x in row[0])))
        return chosen[0], threshold, True
    chosen = min(candidates, key=lambda row: (row[2], row[1], tuple(x["evidence_id"] for x in row[0])))
    return chosen[0], threshold, False


def comparator_checks(scenario: dict, policy: str) -> list[dict]:
    if policy == "STATIC":
        return []
    if policy == "CONTRACT_ONLY":
        return [row for row in scenario["evidence"] if row["kind"] in {"authorization", "scope"}]
    if policy.startswith("FIXED_"):
        cutoff = float(policy.split("_", 1)[1])
        return [row for row in scenario["evidence"] if row["q"] >= cutoff]
    if policy == "ALWAYS_REFRESH":
        return list(scenario["evidence"])
    raise ValueError(policy)


def run_policy(scenario: dict, policy: str, tau0: float = TAU0, alpha: float = ALPHA, rho: float = RHO) -> dict:
    if policy == "RAER":
        checks, threshold, feasible = raer_checks(scenario, tau0, alpha, rho)
    else:
        checks, threshold, feasible = comparator_checks(scenario, policy), None, True
    checked = {row["evidence_id"] for row in checks}
    invalid_checked = [row for row in checks if not row["actual_valid"]]
    if invalid_checked:
        decision = "ASK" if any(row["kind"] == "authorization" for row in invalid_checked) else "REFRESH"
    elif policy == "RAER" and not feasible:
        decision = "ABSTAIN"
    else:
        decision = "ACT"
    safe = all(row["actual_valid"] for row in scenario["evidence"])
    if decision == "ACT" and safe:
        outcome = "safe_success"
    elif decision == "ACT":
        outcome = "harmful_action"
    elif safe:
        outcome = "false_block"
    else:
        outcome = "protected_block"
    cost = sum(row["cost"] for row in checks)
    return {
        "scenario_id": scenario["scenario_id"], "domain": scenario["domain"], "partition": scenario["partition"],
        "construction_stratum": scenario["construction_stratum"], "challenge_family": scenario["challenge_family"],
        "policy": policy, "decision": decision, "outcome": outcome,
        "checked": ";".join(sorted(checked)), "check_count": len(checks), "check_cost": round(cost, 12),
        "budget": scenario["budget"], "budget_exceeded": cost > scenario["budget"] + 1e-12,
        "safe_to_act": safe, "risk_before": residual_risk(scenario, set(), rho, alpha),
        "risk_after": residual_risk(scenario, checked, rho, alpha), "risk_threshold": threshold,
        "realized_harm": scenario["h"] if outcome == "harmful_action" else 0.0,
    }


def summarize(rows: list[dict]) -> list[dict]:
    output = []
    for policy in POLICIES:
        subset = [row for row in rows if row["policy"] == policy]
        valid = [row for row in subset if row["safe_to_act"]]
        invalid = [row for row in subset if not row["safe_to_act"]]
        output.append({
            "policy": policy, "n": len(subset), "valid_n": len(valid), "invalid_n": len(invalid),
            "safe_successes": sum(row["outcome"] == "safe_success" for row in subset),
            "protected_blocks": sum(row["outcome"] == "protected_block" for row in subset),
            "harmful_actions": sum(row["outcome"] == "harmful_action" for row in subset),
            "false_blocks": sum(row["outcome"] == "false_block" for row in subset),
            "safe_completion_rate_on_valid": sum(row["outcome"] == "safe_success" for row in valid) / len(valid) if valid else None,
            "harmful_action_rate_on_invalid": sum(row["outcome"] == "harmful_action" for row in invalid) / len(invalid) if invalid else None,
            "mean_check_cost": sum(row["check_cost"] for row in subset) / len(subset) if subset else None,
            "total_check_cost": sum(row["check_cost"] for row in subset),
            "budget_exceeding_rate": sum(row["budget_exceeded"] for row in subset) / len(subset) if subset else None,
            "total_realized_harm": sum(row["realized_harm"] for row in subset),
        })
    return output


def build_scenarios(label_document: dict) -> list[dict]:
    lock = load(RELEASE / "BENCHMARK_RELEASE_LOCK_v1.1.json")
    for name, expected in lock["files"].items():
        if sha256(RELEASE / name) != expected:
            raise ValueError(f"Release hash mismatch: {name}")
    plan = load(PLAN)
    assert plan["status"] == "FROZEN_BEFORE_DEVELOPMENT_OUTCOMES"
    partition = label_document["partition"]
    split = {row["scenario_id"]: row["partition"] for row in load(RELEASE / "label_blind_split_manifest.json")["records"]}
    labels = {row["scenario_id"]: row for row in label_document["labels"]}
    if not labels or any(split.get(scenario_id) != partition for scenario_id in labels):
        raise ValueError("Released labels do not match their declared partition")
    visible = {row["scenario_id"]: row for row in load(RELEASE / "reviewer_visible_cases.json")["scenarios"]}
    scores_doc = load(RELEASE / "adjudicated_master_scores.json")
    scenario_scores = {row["scenario_id"]: row["adjudicated_scores"] for row in scores_doc["scenario_rows"]}
    evidence_scores = {(row["scenario_id"], row["evidence_id"]): row["adjudicated_scores"] for row in scores_doc["evidence_rows"]}
    analysis = []
    for scenario_id in sorted(labels):
        source, label = visible[scenario_id], labels[scenario_id]
        invalid = set(label["invalid_evidence_ids"])
        evidence_ids = {row["evidence_id"] for row in source["evidence"]}
        if not invalid <= evidence_ids or bool(not invalid) != label["safe_to_act"]:
            raise ValueError(f"Invalid label record: {scenario_id}")
        evidence = []
        for item in source["evidence"]:
            score = evidence_scores[(scenario_id, item["evidence_id"])]
            evidence.append({
                **item, "q": q_e0(item), "w": score["criticality_score_1_5"] / 5.0,
                "cost": score["validation_cost_score_1_5"] / 5.0,
                "actual_valid": item["evidence_id"] not in invalid,
            })
        analysis.append({
            "scenario_id": scenario_id, "domain": source["domain"], "partition": partition,
            "budget": source["budget_units"], "h": action_harm(scenario_scores[scenario_id]),
            "construction_stratum": label["construction_stratum"], "challenge_family": label["challenge_family"],
            "correlation_group": label["correlation_group_evidence_ids"], "evidence": evidence,
        })
    return analysis


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    label_document = load(args.labels)
    scenarios = build_scenarios(label_document)
    outcomes = [run_policy(scenario, policy) for scenario in scenarios for policy in POLICIES]
    summaries = summarize(outcomes)
    args.output.mkdir(parents=True, exist_ok=False)
    write_csv(args.output / "policy_outcomes.csv", outcomes)
    write_csv(args.output / "policy_summary.csv", summaries)
    run_manifest = {
        "partition": label_document["partition"], "status": "DIAGNOSTIC_NOT_CONFIRMATORY",
        "scenario_count": len(scenarios), "policy_count": len(POLICIES), "outcome_count": len(outcomes),
        "release_lock_sha256": sha256(RELEASE / "BENCHMARK_RELEASE_LOCK_v1.1.json"),
        "analysis_plan_sha256": sha256(PLAN), "label_release_sha256": sha256(args.labels),
        "runner_sha256": sha256(Path(__file__)), "randomness": "none", "external_calls": "none",
    }
    (args.output / "run_manifest.json").write_text(json.dumps(run_manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(run_manifest, indent=2))


if __name__ == "__main__":
    main()
