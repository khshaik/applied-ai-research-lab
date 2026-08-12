#!/usr/bin/env python3
"""Prospective RAER v2 design-only evaluation on the 72 exposed v1 cases."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "evaluation/v2"
RESULTS = V2 / "results_design_v1.0"
sys.path.insert(0, str(ROOT / "evaluation"))
import raer_benchmark as v1

LAMBDA_A = (0.25, 0.50, 0.75, 1.00, 1.50)
LAMBDA_C = (0.02, 0.05, 0.10, 0.20)
DELTAS = (0.00, 0.05)
AUTH_THRESHOLDS = (0.08, 0.12)
CONFIGS = tuple(
    {"lambda_h": 1.0, "lambda_a": la, "lambda_c": lc, "delta": delta, "theta_auth": auth, "lambda_slack": 1.0}
    for la, lc, delta, auth in itertools.product(LAMBDA_A, LAMBDA_C, DELTAS, AUTH_THRESHOLDS)
)
COMPARATORS = ("STATIC", "CONTRACT_ONLY", "FIXED_0.10", "FIXED_0.20", "FIXED_0.35", "FIXED_0.50", "ALWAYS_REFRESH", "RAER_V1")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assert_heldout_sealed() -> None:
    path = ROOT / "evaluation/restricted/held_out_test_labels_v1.1.json"
    if path.exists():
        raise RuntimeError(f"Forbidden held-out label release exists: {path}")


def safe_probability(scenario: dict, checked: set[str]) -> float:
    probability = 1.0
    for item in scenario["evidence"]:
        q = v1.VERIFIER_FLOOR if item["evidence_id"] in checked else item["q"]
        probability *= 1.0 - q
    return probability


def triggered_authorization(scenario: dict, theta_auth: float) -> list[dict]:
    if scenario["authorization_sensitivity"] < 4:
        return []
    return [
        item for item in scenario["evidence"]
        if item["kind"] == "authorization" and item["q"] * item["w"] >= theta_auth - 1e-12
    ]


def choose_v2(scenario: dict, config: dict, *, rho: float = v1.RHO, authorization_safeguard: bool = True) -> dict:
    allowed = scenario["budget"] + config["delta"]
    required = triggered_authorization(scenario, config["theta_auth"]) if authorization_safeguard else []
    required_ids = {item["evidence_id"] for item in required}
    if sum(item["cost"] for item in required) > allowed + 1e-12:
        return {
            "checks": [], "planned_decision": "ABSTAIN", "authorization_infeasible": True,
            "objective": config["lambda_a"] * safe_probability(scenario, set()),
            "residual_risk": v1.residual_risk(scenario, set(), rho), "safe_probability": safe_probability(scenario, set()),
            "slack": 0.0,
        }
    candidates = []
    for size in range(len(scenario["evidence"]) + 1):
        for subset_tuple in itertools.combinations(scenario["evidence"], size):
            subset = list(subset_tuple); ids = {item["evidence_id"] for item in subset}
            cost = sum(item["cost"] for item in subset)
            if cost > allowed + 1e-12 or not required_ids <= ids:
                continue
            residual = v1.residual_risk(scenario, ids, rho)
            p_safe = safe_probability(scenario, ids)
            act_loss = config["lambda_h"] * residual
            abstain_loss = config["lambda_a"] * p_safe
            decision = "ACT" if act_loss <= abstain_loss + 1e-12 else "ABSTAIN"
            slack = max(0.0, cost - scenario["budget"])
            objective = config["lambda_c"] * cost + config["lambda_slack"] * slack + min(act_loss, abstain_loss)
            candidates.append((objective, cost, residual, len(subset), tuple(sorted(ids)), subset, decision, p_safe, slack))
    if not candidates:
        raise RuntimeError(f"No v2 candidate subset: {scenario['scenario_id']}")
    chosen = min(candidates, key=lambda row: row[:5])
    return {
        "checks": chosen[5], "planned_decision": chosen[6], "authorization_infeasible": False,
        "objective": chosen[0], "residual_risk": chosen[2], "safe_probability": chosen[7], "slack": chosen[8],
    }


def run_v2(scenario: dict, config: dict, *, rho: float = v1.RHO, authorization_safeguard: bool = True, policy="RAER_V2") -> dict:
    plan = choose_v2(scenario, config, rho=rho, authorization_safeguard=authorization_safeguard)
    checks = plan["checks"]; checked_ids = {item["evidence_id"] for item in checks}
    invalid_checked = [item for item in checks if not item["actual_valid"]]
    if invalid_checked:
        decision = "ASK" if any(item["kind"] == "authorization" for item in invalid_checked) else "REFRESH"
    else:
        decision = plan["planned_decision"]
    safe = all(item["actual_valid"] for item in scenario["evidence"])
    if decision == "ACT" and safe: outcome = "safe_success"
    elif decision == "ACT": outcome = "harmful_action"
    elif safe: outcome = "false_block"
    else: outcome = "protected_block"
    triggered_ids = {item["evidence_id"] for item in triggered_authorization(scenario, config["theta_auth"])}
    missed_triggered_invalid = [
        item for item in scenario["evidence"]
        if item["evidence_id"] in triggered_ids and not item["actual_valid"] and item["evidence_id"] not in checked_ids
    ]
    cost = sum(item["cost"] for item in checks)
    return {
        "scenario_id": scenario["scenario_id"], "domain": scenario["domain"], "partition": scenario["partition"],
        "construction_stratum": scenario["construction_stratum"], "challenge_family": scenario["challenge_family"],
        "policy": policy, "decision": decision, "outcome": outcome, "checked": ";".join(sorted(checked_ids)),
        "check_count": len(checks), "check_cost": cost, "budget": scenario["budget"], "slack": plan["slack"],
        "positive_slack": plan["slack"] > 1e-12, "budget_exceeded": cost > scenario["budget"] + 1e-12,
        "safe_to_act": safe, "planned_decision": plan["planned_decision"],
        "authorization_infeasible": plan["authorization_infeasible"],
        "triggered_authorization_count": len(triggered_ids),
        "triggered_authorization_harm": outcome == "harmful_action" and bool(missed_triggered_invalid),
        "risk_before": v1.residual_risk(scenario, set(), rho), "risk_after": plan["residual_risk"],
        "safe_probability_proxy": plan["safe_probability"], "objective": plan["objective"],
        "realized_harm": scenario["h"] if outcome == "harmful_action" else 0.0,
    }


def run_comparator(scenario: dict, policy: str) -> dict:
    source_policy = "RAER" if policy == "RAER_V1" else policy
    row = v1.run_policy(scenario, source_policy)
    row.update({"partition": scenario["partition"], "construction_stratum": scenario["construction_stratum"], "challenge_family": scenario["challenge_family"]})
    row["policy"] = policy; row["slack"] = 0.0; row["positive_slack"] = False
    row["triggered_authorization_count"] = 0; row["triggered_authorization_harm"] = False
    row["authorization_infeasible"] = False; row["planned_decision"] = row["decision"]
    row["safe_probability_proxy"] = None; row["objective"] = None
    return row


def summarize(rows: list[dict]) -> dict:
    valid = [row for row in rows if row["safe_to_act"]]; invalid = [row for row in rows if not row["safe_to_act"]]
    return {
        "n": len(rows), "valid_n": len(valid), "invalid_n": len(invalid),
        "safe_successes": sum(row["outcome"] == "safe_success" for row in rows),
        "protected_blocks": sum(row["outcome"] == "protected_block" for row in rows),
        "harmful_actions": sum(row["outcome"] == "harmful_action" for row in rows),
        "false_blocks": sum(row["outcome"] == "false_block" for row in rows),
        "safe_completion_rate_on_valid": sum(row["outcome"] == "safe_success" for row in valid) / len(valid) if valid else None,
        "harmful_action_rate_on_invalid": sum(row["outcome"] == "harmful_action" for row in invalid) / len(invalid) if invalid else None,
        "mean_check_cost": sum(row["check_cost"] for row in rows) / len(rows),
        "total_check_cost": sum(row["check_cost"] for row in rows),
        "positive_slack_rate": sum(row["positive_slack"] for row in rows) / len(rows),
        "mean_slack": sum(row["slack"] for row in rows) / len(rows),
        "maximum_slack": max((row["slack"] for row in rows), default=0.0),
        "triggered_authorization_harmful_actions": sum(row["triggered_authorization_harm"] for row in rows),
        "total_realized_harm": sum(row["realized_harm"] for row in rows),
    }


def comparator_outcomes(scenarios: list[dict]) -> tuple[dict[str, list[dict]], dict[str, dict]]:
    outcomes = {policy: [run_comparator(scenario, policy) for scenario in scenarios] for policy in COMPARATORS}
    return outcomes, {policy: summarize(rows) for policy, rows in outcomes.items()}


def eligible(summary: dict, comparator_summaries: dict[str, dict]) -> tuple[bool, list[str]]:
    best_safe = max(row["safe_completion_rate_on_valid"] for row in comparator_summaries.values())
    fixed = comparator_summaries["FIXED_0.20"]
    failures = []
    if summary["safe_completion_rate_on_valid"] + 1e-12 < best_safe - 0.05: failures.append("safe_completion")
    if summary["harmful_action_rate_on_invalid"] > fixed["harmful_action_rate_on_invalid"] + 1e-12: failures.append("harmful_action")
    if summary["triggered_authorization_harmful_actions"] != 0: failures.append("authorization")
    if summary["positive_slack_rate"] > 0.25 + 1e-12: failures.append("slack_rate")
    if summary["mean_slack"] > 0.025 + 1e-12: failures.append("mean_slack")
    if summary["maximum_slack"] > 0.05 + 1e-12: failures.append("maximum_slack")
    return not failures, failures


def config_key(config: dict) -> tuple:
    return (config["lambda_a"], -config["lambda_c"], config["delta"], -config["theta_auth"])


def choose_config(scenarios: list[dict]) -> dict:
    _, comparator_summaries = comparator_outcomes(scenarios)
    candidates = []
    for config in CONFIGS:
        rows = [run_v2(scenario, config) for scenario in scenarios]
        summary = summarize(rows); ok, failures = eligible(summary, comparator_summaries)
        candidates.append({"config": config, "summary": summary, "eligible": ok, "failures": failures})
    pool = [row for row in candidates if row["eligible"]]
    if pool:
        chosen = min(pool, key=lambda row: (
            row["summary"]["harmful_action_rate_on_invalid"], row["summary"]["mean_check_cost"],
            -row["summary"]["safe_completion_rate_on_valid"], row["summary"]["positive_slack_rate"], config_key(row["config"])
        ))
    else:
        chosen = min(candidates, key=lambda row: (
            -row["summary"]["safe_completion_rate_on_valid"], row["summary"]["harmful_action_rate_on_invalid"],
            row["summary"]["mean_check_cost"], row["summary"]["positive_slack_rate"], config_key(row["config"])
        ))
    return {"chosen": chosen, "all": candidates}


def load_design_scenarios() -> list[dict]:
    assert_heldout_sealed()
    label_paths = [ROOT / "evaluation/restricted/development_labels_v1.1.json", ROOT / "evaluation/restricted/validation_labels_v1.1.json"]
    documents = [json.loads(path.read_text(encoding="utf-8")) for path in label_paths]
    if {doc["partition"] for doc in documents} != {"development", "validation"}:
        raise ValueError("Design label partitions are incorrect")
    scenarios = [scenario for document in documents for scenario in v1.build_scenarios(document)]
    if len(scenarios) != 72 or len({row["scenario_id"] for row in scenarios}) != 72:
        raise ValueError("Expected 72 unique design scenarios")
    scores = json.loads((ROOT / "calibration/benchmark/release_v1.1/adjudicated_master_scores.json").read_text(encoding="utf-8"))
    sensitivity = {row["scenario_id"]: row["adjudicated_scores"]["authorization_sensitivity_score_1_5"] for row in scores["scenario_rows"]}
    for scenario in scenarios: scenario["authorization_sensitivity"] = sensitivity[scenario["scenario_id"]]
    return sorted(scenarios, key=lambda row: row["scenario_id"])


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)


def bootstrap(rows_by_policy: dict[str, list[dict]], replicates=10000, seed=20260812) -> dict:
    rng = random.Random(seed); domains = sorted({row["domain"] for rows in rows_by_policy.values() for row in rows})
    indexed = {policy: {row["scenario_id"]: row for row in rows} for policy, rows in rows_by_policy.items()}
    domain_ids = {domain: sorted({row["scenario_id"] for rows in rows_by_policy.values() for row in rows if row["domain"] == domain}) for domain in domains}
    values = {policy: defaultdict(list) for policy in rows_by_policy}
    for _ in range(replicates):
        sample_ids = [rng.choice(domain_ids[domain]) for domain in domains for _ in range(len(domain_ids[domain]))]
        for policy in rows_by_policy:
            summary = summarize([indexed[policy][scenario_id] for scenario_id in sample_ids])
            for metric in ("safe_completion_rate_on_valid", "harmful_action_rate_on_invalid", "mean_check_cost", "positive_slack_rate"):
                if summary[metric] is not None: values[policy][metric].append(summary[metric])
    result = {}
    for policy, metrics in values.items():
        result[policy] = {}
        for metric, observed in metrics.items():
            observed.sort(); n = len(observed)
            result[policy][metric] = {"lower_95": observed[int(0.025 * (n - 1))], "upper_95": observed[int(0.975 * (n - 1))], "replicates": n}
    return result


def main() -> None:
    assert_heldout_sealed()
    lock_path = V2 / "RAER_V2_PRE_EXECUTION_LOCK_v1.0.json"
    if not lock_path.is_file(): raise FileNotFoundError("Pre-execution lock is required")
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    for name, expected in lock["files"].items():
        if sha256(ROOT / name) != expected: raise ValueError(f"Pre-execution hash mismatch: {name}")
    if RESULTS.exists(): raise FileExistsError(f"Design results are immutable: {RESULTS}")
    scenarios = load_design_scenarios(); domains = sorted({row["domain"] for row in scenarios})
    outer_rows, fold_records = [], []
    for domain in domains:
        training = [row for row in scenarios if row["domain"] != domain]
        outer = [row for row in scenarios if row["domain"] == domain]
        selection = choose_config(training); chosen = selection["chosen"]
        outer_outcomes = [run_v2(scenario, chosen["config"]) for scenario in outer]
        outer_rows.extend(outer_outcomes)
        fold_records.append({
            "outer_domain": domain, "training_n": len(training), "outer_n": len(outer),
            "eligible_configuration_selected": chosen["eligible"], "selection_failures": ";".join(chosen["failures"]),
            **chosen["config"], **{f"training_{key}": value for key, value in chosen["summary"].items()}
        })
    comparator_rows, comparator_summaries = comparator_outcomes(scenarios)
    v2_summary = summarize(outer_rows); all_summaries = {**comparator_summaries, "RAER_V2_OUT_OF_FOLD": v2_summary}
    best_safe = max(row["safe_completion_rate_on_valid"] for row in comparator_summaries.values())
    fixed = comparator_summaries["FIXED_0.20"]
    comparable = {name: row for name, row in comparator_summaries.items() if row["safe_completion_rate_on_valid"] + 1e-12 >= best_safe - 0.05}
    dominators = []
    for name, row in comparable.items():
        no_worse_harm = row["harmful_action_rate_on_invalid"] <= v2_summary["harmful_action_rate_on_invalid"] + 1e-12
        no_worse_cost = row["mean_check_cost"] <= v2_summary["mean_check_cost"] + 1e-12
        strict = row["harmful_action_rate_on_invalid"] < v2_summary["harmful_action_rate_on_invalid"] - 1e-12 or row["mean_check_cost"] < v2_summary["mean_check_cost"] - 1e-12
        if no_worse_harm and no_worse_cost and strict: dominators.append(name)
    criteria = {
        "safe_completion": v2_summary["safe_completion_rate_on_valid"] + 1e-12 >= best_safe - 0.05,
        "harmful_action": v2_summary["harmful_action_rate_on_invalid"] <= fixed["harmful_action_rate_on_invalid"] + 1e-12,
        "authorization": v2_summary["triggered_authorization_harmful_actions"] == 0,
        "non_dominance": not dominators,
        "slack_rate": v2_summary["positive_slack_rate"] <= 0.25 + 1e-12,
        "mean_slack": v2_summary["mean_slack"] <= 0.025 + 1e-12,
        "maximum_slack": v2_summary["maximum_slack"] <= 0.05 + 1e-12,
        "fold_stability": sum(row["eligible_configuration_selected"] for row in fold_records) >= 5,
    }
    gate_pass = all(criteria.values())
    final_selection = choose_config(scenarios); final = final_selection["chosen"]
    final_rows = [run_v2(scenario, final["config"], policy="RAER_V2_FINAL_DESIGN_FIT") for scenario in scenarios]
    ablations = []
    variants = {
        "V2_FULL": (final["config"], v1.RHO, True),
        "V2_NO_ABSTENTION_LOSS": ({**final["config"], "lambda_a": 0.0}, v1.RHO, True),
        "V2_NO_AUTHORIZATION_SAFEGUARD": (final["config"], v1.RHO, False),
        "V2_NO_SLACK": ({**final["config"], "delta": 0.0}, v1.RHO, True),
        "V2_NO_CORRELATION_UPLIFT": (final["config"], 0.0, True),
    }
    for name, (config, rho, safeguard) in variants.items():
        summary = summarize([run_v2(scenario, config, rho=rho, authorization_safeguard=safeguard, policy=name) for scenario in scenarios])
        ablations.append({"variant": name, **config, **summary})
    RESULTS.mkdir(parents=True)
    write_csv(RESULTS / "outer_fold_selection.csv", fold_records)
    write_csv(RESULTS / "oof_policy_outcomes.csv", [*sum(comparator_rows.values(), []), *outer_rows])
    write_csv(RESULTS / "oof_policy_summary.csv", [{"policy": name, **row} for name, row in all_summaries.items()])
    grid_rows = []
    for row in final_selection["all"]: grid_rows.append({**row["config"], "eligible": row["eligible"], "failures": ";".join(row["failures"]), **row["summary"]})
    write_csv(RESULTS / "all_design_configuration_summary.csv", grid_rows)
    write_csv(RESULTS / "final_design_fit_outcomes.csv", final_rows)
    write_csv(RESULTS / "ablations.csv", ablations)
    gate = {
        "decision": "PASS_PROSPECTIVE_GATE" if gate_pass else "FAIL_KEEP_HELD_OUT_SEALED",
        "interpretation": "Design-only evidence; not a held-out effectiveness result.",
        "criteria": criteria, "dominating_comparators": dominators,
        "eligible_outer_folds": sum(row["eligible_configuration_selected"] for row in fold_records),
        "outer_fold_count": len(fold_records), "oof_raer_v2_summary": v2_summary,
        "fixed_0_20_summary": fixed, "best_comparator_safe_completion": best_safe,
        "final_configuration": final["config"], "final_configuration_eligible_on_all_design_data": final["eligible"],
        "held_out_status": "SEALED_NOT_RELEASED",
        "next_action": "Request explicit approval before held-out label release" if gate_pass else "Prepare methods/negative-results manuscript; do not access held-out labels",
    }
    (RESULTS / "v2_design_gate.json").write_text(json.dumps(gate, indent=2) + "\n", encoding="utf-8")
    (RESULTS / "bootstrap_intervals.json").write_text(json.dumps(bootstrap({**comparator_rows, "RAER_V2_OUT_OF_FOLD": outer_rows}), indent=2) + "\n", encoding="utf-8")
    outputs = sorted(path for path in RESULTS.iterdir() if path.is_file())
    manifest = {
        "design_run_id": "RAER-V2-DESIGN-1.0", "decision": gate["decision"],
        "pre_execution_lock_sha256": sha256(lock_path), "randomness": "bootstrap only; seed 20260812",
        "external_calls": "none", "held_out_labels_accessed": False,
        "outputs": {str(path.relative_to(ROOT)): sha256(path) for path in outputs},
    }
    (RESULTS / "design_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(gate, indent=2))


if __name__ == "__main__":
    main()
