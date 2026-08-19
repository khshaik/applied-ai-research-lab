import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCOPE_PATH = ROOT / "gate2" / "minimum_route_scope.draft.json"
AMENDMENT_PATH = ROOT / "research/design/02d_minimum_route_protocol_amendment_draft.md"
REVIEW_PATH = ROOT / "research/design/02e_b05_accountable_author_review.md"


class MinimumRouteScopeTests(unittest.TestCase):
    def setUp(self):
        self.scope = json.loads(SCOPE_PATH.read_text(encoding="utf-8"))

    def test_scope_approval_and_later_protocol_freeze_are_distinct(self):
        self.assertEqual(
            self.scope["status"], "approved_effective_protocol_reconciliation_pending"
        )
        self.assertIs(self.scope["effective"], True)
        self.assertEqual(self.scope["approval"]["decision"], "approve")
        self.assertEqual(self.scope["approval"]["accountable_author_id"], "accountable_user")
        self.assertEqual(self.scope["approval"]["decided_at"], "2026-08-16T08:06:17+05:30")
        frozen = json.loads((ROOT / "gate2/frozen_protocol_package_v1.3.json").read_text(encoding="utf-8"))
        self.assertEqual(frozen["status"], "frozen")
        self.assertEqual(frozen["approval_decision"], "approve")
        self.assertEqual(frozen["next_gate"], "D05")

    def test_source_family_allocation_is_exact_and_non_cartesian(self):
        expected = {
            "S1": ["Semantic Scholar Academic Graph"],
            "S2": ["OpenAlex"],
            "S3": ["OpenAlex", "Semantic Scholar Academic Graph"],
            "S4_S5R": [
                "OpenAlex",
                "Semantic Scholar Academic Graph",
                "arXiv",
            ],
            "S5T": ["OpenAlex", "arXiv"],
            "S5S": ["OpenAlex", "arXiv"],
            "S6": ["OpenAlex", "arXiv"],
            "S7": ["OpenAlex", "Semantic Scholar Academic Graph", "arXiv"],
            "S8": ["OpenAlex", "Semantic Scholar Academic Graph"],
        }
        actual = {
            item["family_id"]: item["discovery_sources"]
            for item in self.scope["family_source_allocation"]
        }
        self.assertEqual(actual, expected)
        self.assertTrue(any(len(sources) == 1 for sources in actual.values()))
        self.assertFalse(
            any("Crossref REST API" in sources for sources in actual.values())
        )

    def test_claim_and_crossref_boundaries_are_locked_in_draft(self):
        self.assertEqual(
            self.scope["crossref_role"],
            "doi_and_bibliographic_metadata_verification_only",
        )
        prohibited = set(self.scope["prohibited_claim_classes"])
        self.assertTrue(
            {
                "exhaustive_literature_coverage",
                "validated_human_cognitive_load_measurement",
                "empirical_organizational_superiority",
                "completed_prospective_multi_team_validation",
            }.issubset(prohibited)
        )

    def test_human_approval_evidence_and_freeze_boundary_are_present(self):
        text = AMENDMENT_PATH.read_text(encoding="utf-8")
        self.assertIn("**Effective:** Yes", text)
        self.assertIn("Approve minimum-route protocol amendment v0.1.", text)
        self.assertIn("accountable-author confirmation", text)
        self.assertIn("instructed **“Continue”** twice", text)
        self.assertIn("does not freeze the protocol", text)

    def test_review_record_preserves_decision_and_claim_boundaries(self):
        text = REVIEW_PATH.read_text(encoding="utf-8")
        self.assertIn("**Decision status:** `approved`", text)
        self.assertIn("Approve minimum-route protocol amendment v0.1.", text)
        for criterion in ("I1–I7", "E1–E10"):
            self.assertIn(criterion, text)
        for boundary in (
            "exhaustive retrieval",
            "validated human cognition",
            "organizational ROI",
            "universal superiority",
        ):
            self.assertIn(boundary, text)
        self.assertEqual(len(self.scope["inaccessible_subscription_sources"]), 6)
        self.assertIn("does not constitute D03", text)


if __name__ == "__main__":
    unittest.main()
