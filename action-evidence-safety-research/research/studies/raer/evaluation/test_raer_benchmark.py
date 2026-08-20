#!/usr/bin/env python3

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import raer_benchmark as rb


def evidence(evidence_id, *, kind="state", q=0.2, w=1.0, cost=0.2, valid=True):
    return {"evidence_id": evidence_id, "kind": kind, "q": q, "w": w, "cost": cost, "actual_valid": valid}


def scenario(items, *, budget=1.0, h=0.8, group=()):
    return {"scenario_id": "T", "domain": "test", "partition": "development", "budget": budget, "h": h,
            "construction_stratum": "test", "challenge_family": "test", "correlation_group": list(group), "evidence": items}


class EvaluatorTests(unittest.TestCase):
    def test_e0_is_deterministic_and_bounded(self):
        item = {"age_hours": 12, "validity_window_hours": 24, "source_volatility": 3, "dependent_changes": 2,
                "update_frequency": 4, "source_reliability": 4, "authorization_age_hours": 0,
                "authorization_window_hours": 0, "contradiction_strength": 1}
        self.assertEqual(rb.q_e0(item), rb.q_e0(item))
        self.assertGreater(rb.q_e0(item), 0)
        self.assertLess(rb.q_e0(item), 1)

    def test_budget_boundary_is_inclusive(self):
        s = scenario([evidence("A", q=0.9, cost=0.5)], budget=0.5)
        checks, _, _ = rb.raer_checks(s, tau0=0.01)
        self.assertEqual([row["evidence_id"] for row in checks], ["A"])

    def test_tie_break_is_lexicographic(self):
        s = scenario([evidence("B", q=0.5), evidence("A", q=0.5)], budget=0.2)
        checks, _, _ = rb.raer_checks(s, tau0=0.01)
        self.assertEqual([row["evidence_id"] for row in checks], ["A"])

    def test_correlated_risk_exceeds_independent_risk(self):
        s = scenario([evidence("A"), evidence("B")], group=("A", "B"))
        self.assertGreater(rb.residual_risk(s, set(), rho=0.2), rb.residual_risk(s, set(), rho=0.0))

    def test_invalid_authorization_yields_ask(self):
        s = scenario([evidence("A", kind="authorization", q=0.9, valid=False)], budget=1.0)
        out = rb.run_policy(s, "FIXED_0.20")
        self.assertEqual(out["decision"], "ASK")
        self.assertEqual(out["outcome"], "protected_block")

    def test_empty_affordable_selection_abstains_when_infeasible(self):
        s = scenario([evidence("A", q=0.9, cost=1.0)], budget=0.0, h=1.0)
        out = rb.run_policy(s, "RAER", tau0=0.01)
        self.assertEqual(out["checked"], "")
        self.assertEqual(out["decision"], "ABSTAIN")

    def test_repeat_run_is_identical(self):
        s = scenario([evidence("A", q=0.3), evidence("B", q=0.4)], budget=0.4)
        self.assertEqual(rb.run_policy(s, "RAER"), rb.run_policy(s, "RAER"))


if __name__ == "__main__":
    unittest.main()
