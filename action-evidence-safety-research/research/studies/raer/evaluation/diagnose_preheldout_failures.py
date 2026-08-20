#!/usr/bin/env python3
"""Diagnose frozen development/validation failures without held-out access."""

from __future__ import annotations

import csv
import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evaluation"))
import raer_benchmark as rb


def load_rows(path: Path) -> list[dict]:
    return list(csv.DictReader(path.open(encoding="utf-8")))


def minimum_cost_meeting_threshold(scenario: dict) -> float | None:
    threshold = rb.TAU0 * (1.0 - rb.ALPHA * scenario["h"])
    feasible = []
    for size in range(len(scenario["evidence"]) + 1):
        for subset in itertools.combinations(scenario["evidence"], size):
            risk = rb.residual_risk(scenario, {row["evidence_id"] for row in subset})
            if risk <= threshold + 1e-12:
                feasible.append(sum(row["cost"] for row in subset))
    return min(feasible) if feasible else None


def main() -> None:
    partitions = ("development", "validation")
    all_rows = []
    scenario_map = {}
    for partition in partitions:
        label_path = ROOT / f"evaluation/restricted/{partition}_labels_v1.1.json"
        scenarios = rb.build_scenarios(json.loads(label_path.read_text(encoding="utf-8")))
        scenario_map.update({row["scenario_id"]: row for row in scenarios})
        all_rows.extend(load_rows(ROOT / f"evaluation/results/{partition}_v1.0/policy_outcomes.csv"))
    raer = [row for row in all_rows if row["policy"] == "RAER"]
    false_blocks = [row for row in raer if row["outcome"] == "false_block"]
    harmful = [row for row in raer if row["outcome"] == "harmful_action"]
    protected = [row for row in raer if row["outcome"] == "protected_block"]

    false_block_details = []
    for row in false_blocks:
        scenario = scenario_map[row["scenario_id"]]
        min_cost = minimum_cost_meeting_threshold(scenario)
        false_block_details.append({
            "scenario_id": row["scenario_id"], "partition": row["partition"], "domain": row["domain"],
            "budget": scenario["budget"], "minimum_cost_to_threshold": min_cost,
            "budget_gap": None if min_cost is None else max(0.0, min_cost - scenario["budget"]),
            "risk_before": float(row["risk_before"]), "risk_after": float(row["risk_after"]),
            "risk_threshold": float(row["risk_threshold"]), "decision": row["decision"],
        })

    harmful_details = []
    for row in harmful:
        scenario = scenario_map[row["scenario_id"]]
        checked = set(filter(None, row["checked"].split(";")))
        missed = [item for item in scenario["evidence"] if not item["actual_valid"] and item["evidence_id"] not in checked]
        harmful_details.append({
            "scenario_id": row["scenario_id"], "partition": row["partition"], "domain": row["domain"],
            "challenge_family": row["challenge_family"], "checked": sorted(checked),
            "missed_invalid": [{"evidence_id": item["evidence_id"], "kind": item["kind"], "q": item["q"], "w": item["w"], "cost": item["cost"]} for item in missed],
            "risk_after": float(row["risk_after"]), "risk_threshold": float(row["risk_threshold"]),
        })

    report = {
        "scope": "development and validation only; held-out labels not accessed",
        "scenario_count": len(raer),
        "outcomes": dict(Counter(row["outcome"] for row in raer)),
        "false_block_count": len(false_blocks),
        "harmful_action_count": len(harmful),
        "protected_block_count": len(protected),
        "false_blocks_by_domain": dict(Counter(row["domain"] for row in false_blocks)),
        "harmful_actions_by_domain": dict(Counter(row["domain"] for row in harmful)),
        "false_block_mechanism": {
            "abstentions": sum(row["decision"] == "ABSTAIN" for row in false_blocks),
            "budget_insufficient_for_threshold": sum(
                item["minimum_cost_to_threshold"] is not None and item["minimum_cost_to_threshold"] > item["budget"] + 1e-12
                for item in false_block_details
            ),
            "threshold_unreachable_even_without_budget": sum(item["minimum_cost_to_threshold"] is None for item in false_block_details)
        },
        "missed_invalid_kinds": dict(Counter(item["kind"] for row in harmful_details for item in row["missed_invalid"])),
        "false_block_details": false_block_details,
        "harmful_action_details": harmful_details,
        "interpretation": "The frozen formulation trades validation cost for both lower harm and frequent abstention; diagnosis is descriptive and cannot justify retrospective retuning."
    }
    out = ROOT / "evaluation/results/PREHELDOUT_FAILURE_DIAGNOSIS_v1.0.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("scope", "scenario_count", "outcomes", "false_blocks_by_domain", "harmful_actions_by_domain", "false_block_mechanism", "missed_invalid_kinds")}, indent=2))


if __name__ == "__main__":
    main()
