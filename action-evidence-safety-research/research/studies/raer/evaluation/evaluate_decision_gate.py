#!/usr/bin/env python3
"""Apply the frozen non-dominance and safe-completion gate to a policy summary."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def as_float(row: dict, key: str) -> float:
    value = row[key]
    if value in ("", "None"):
        raise ValueError(f"Undefined registered metric {key} for {row['policy']}")
    return float(value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("summary", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--phase", required=True, choices=("development", "validation", "held_out_test"))
    args = parser.parse_args()
    rows = {row["policy"]: row for row in csv.DictReader(args.summary.open(encoding="utf-8"))}
    raer = rows["RAER"]
    best_safe = max(as_float(row, "safe_completion_rate_on_valid") for row in rows.values())
    comparable = {
        name: row for name, row in rows.items()
        if name != "RAER" and as_float(row, "safe_completion_rate_on_valid") + 1e-12 >= best_safe - 0.05
    }
    dominators = []
    for name, row in comparable.items():
        no_worse_harm = as_float(row, "harmful_action_rate_on_invalid") <= as_float(raer, "harmful_action_rate_on_invalid") + 1e-12
        no_worse_cost = as_float(row, "mean_check_cost") <= as_float(raer, "mean_check_cost") + 1e-12
        strict = (
            as_float(row, "harmful_action_rate_on_invalid") < as_float(raer, "harmful_action_rate_on_invalid") - 1e-12
            or as_float(row, "mean_check_cost") < as_float(raer, "mean_check_cost") - 1e-12
        )
        if no_worse_harm and no_worse_cost and strict:
            dominators.append(name)
    safe_gate = as_float(raer, "safe_completion_rate_on_valid") + 1e-12 >= best_safe - 0.05
    if args.phase == "development":
        decision = "DEVELOPMENT_PASS" if safe_gate and not dominators else "DEVELOPMENT_WARNING"
    elif args.phase == "validation":
        decision = "PROCEED_TO_EVALUATION_LOCK" if safe_gate and not dominators else "STOP_BEFORE_HELD_OUT"
    else:
        decision = "GO" if safe_gate and not dominators else "STOP_PIVOT"
    result = {
        "phase": args.phase,
        "decision": decision,
        "safe_completion_gate_passed": safe_gate,
        "best_safe_completion": best_safe,
        "raer_safe_completion": as_float(raer, "safe_completion_rate_on_valid"),
        "raer_harmful_action_rate": as_float(raer, "harmful_action_rate_on_invalid"),
        "raer_mean_validation_cost": as_float(raer, "mean_check_cost"),
        "dominating_comparators": dominators,
        "interpretation": "Development is diagnostic only." if args.phase == "development" else "Apply the frozen phase boundary without parameter retuning.",
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
