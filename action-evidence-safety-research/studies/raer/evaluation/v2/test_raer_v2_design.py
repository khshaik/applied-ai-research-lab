#!/usr/bin/env python3

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import raer_v2_design as v2


def evidence(evidence_id, *, kind="state", q=0.2, w=1.0, cost=0.2, valid=True):
    return {"evidence_id": evidence_id, "kind": kind, "q": q, "w": w, "cost": cost, "actual_valid": valid}


def scenario(items, *, budget=0.4, h=0.8, sensitivity=4, group=()):
    return {"scenario_id": "T", "domain": "test", "partition": "development", "budget": budget, "h": h,
            "authorization_sensitivity": sensitivity, "construction_stratum": "test", "challenge_family": "test",
            "correlation_group": list(group), "evidence": items}


CONFIG = {"lambda_h": 1.0, "lambda_a": 1.0, "lambda_c": 0.05, "delta": 0.05, "theta_auth": 0.08, "lambda_slack": 1.0}


class V2Tests(unittest.TestCase):
    def test_grid_is_frozen_at_eighty(self):
        self.assertEqual(len(v2.CONFIGS), 80)
        self.assertEqual(len({tuple(sorted(x.items())) for x in v2.CONFIGS}), 80)

    def test_deterministic_selection(self):
        s = scenario([evidence("A", q=0.3), evidence("B", q=0.4)])
        self.assertEqual(v2.choose_v2(s, CONFIG), v2.choose_v2(s, CONFIG))

    def test_slack_boundary_allows_exact_point_zero_five(self):
        auth = evidence("AUTH", kind="authorization", q=0.5, w=1.0, cost=0.6)
        s = scenario([auth], budget=0.55)
        plan = v2.choose_v2(s, CONFIG)
        self.assertEqual([x["evidence_id"] for x in plan["checks"]], ["AUTH"])
        self.assertAlmostEqual(plan["slack"], 0.05)

    def test_slack_does_not_allow_more_than_point_zero_five(self):
        auth = evidence("AUTH", kind="authorization", q=0.5, w=1.0, cost=0.61)
        s = scenario([auth], budget=0.55)
        plan = v2.choose_v2(s, CONFIG)
        self.assertTrue(plan["authorization_infeasible"])
        self.assertEqual(plan["planned_decision"], "ABSTAIN")

    def test_authorization_safeguard_requires_triggered_item(self):
        auth = evidence("AUTH", kind="authorization", q=0.2, w=0.5, cost=0.2)
        state = evidence("STATE", q=0.9, w=1.0, cost=0.2)
        s = scenario([auth, state], budget=0.4)
        ids = {x["evidence_id"] for x in v2.choose_v2(s, CONFIG)["checks"]}
        self.assertIn("AUTH", ids)

    def test_invalid_authorization_overrides_planned_action(self):
        auth = evidence("AUTH", kind="authorization", q=0.5, w=1.0, cost=0.2, valid=False)
        s = scenario([auth], budget=0.2)
        outcome = v2.run_v2(s, CONFIG)
        self.assertEqual(outcome["decision"], "ASK")
        self.assertEqual(outcome["outcome"], "protected_block")

    def test_high_abstention_price_encourages_action_on_low_risk_case(self):
        low = evidence("LOW", q=0.02, w=0.2, cost=0.2)
        s = scenario([low], sensitivity=1)
        plan = v2.choose_v2(s, {**CONFIG, "lambda_a": 1.5})
        self.assertEqual(plan["planned_decision"], "ACT")

    def test_summary_denominators(self):
        rows = [
            {"safe_to_act": True, "outcome": "safe_success", "check_cost": 0.1, "positive_slack": False, "slack": 0.0, "triggered_authorization_harm": False, "realized_harm": 0.0},
            {"safe_to_act": False, "outcome": "harmful_action", "check_cost": 0.2, "positive_slack": True, "slack": 0.05, "triggered_authorization_harm": True, "realized_harm": 0.8},
        ]
        summary = v2.summarize(rows)
        self.assertEqual(summary["safe_completion_rate_on_valid"], 1.0)
        self.assertEqual(summary["harmful_action_rate_on_invalid"], 1.0)
        self.assertEqual(summary["positive_slack_rate"], 0.5)


if __name__ == "__main__": unittest.main()
