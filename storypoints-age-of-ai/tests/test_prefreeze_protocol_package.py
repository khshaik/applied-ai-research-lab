import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "gate2" / "prefreeze_protocol_package_v1.3.json"
CONTROL = ROOT / "gate2" / "search_control_prefreeze_v1.3.json"
MATRIX = ROOT / "gate2" / "final_source_family_acceptance_matrix.json"
PROMPT_MANIFEST = ROOT / "evidence_review" / "prompts" / "prefreeze_prompt_manifest_v1.1.0.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PrefreezeProtocolPackageTests(unittest.TestCase):
    def test_package_is_reconciled_but_not_approved_or_frozen(self):
        package = load(PACKAGE)
        self.assertEqual(package["protocol_version"], "1.3")
        self.assertEqual(package["status"], "prefreeze_reconciled_awaiting_D03_approval")
        self.assertTrue(package["D01_reconciliation_complete"])
        self.assertTrue(package["D02_cutoff_and_access_limitations_complete"])
        self.assertIsNone(package["D03_accountable_author_approval"])
        self.assertFalse(package["D04_frozen"])
        self.assertFalse(package["systematic_corpus_created"])

    def test_all_package_artifact_hashes_match(self):
        for row in load(PACKAGE)["artifacts"]:
            path = ROOT / row["path"]
            self.assertTrue(path.is_file(), row["path"])
            self.assertEqual(digest(path), row["sha256"], row["path"])

    def test_search_control_matches_all_and_only_c09_pairs(self):
        control = load(CONTROL)
        matrix = load(MATRIX)
        expected = {(r["family_id"], r["source"]) for r in matrix["rows"]}
        actual = {(r["family_id"], r["source"]) for r in control["required_source_family_pairs"]}
        self.assertEqual(len(actual), 18)
        self.assertEqual(actual, expected)
        self.assertEqual(control["initial_search_cutoff_date"], "2026-08-16")
        self.assertFalse(control["systematic_corpus_created"])
        self.assertFalse(control["developmental_outputs_are_prisma_eligible"])
        self.assertIsNone(control["D03_approval"])

    def test_access_constrained_boundary_is_exact(self):
        package = load(PACKAGE)
        control = load(CONTROL)
        blocked = {row["source"] for row in control["source_access"]
                   if row["status"] == "blocked_authentication"}
        self.assertEqual(blocked, set(package["inaccessible_subscription_sources"]))
        self.assertEqual(len(blocked), 6)
        self.assertIn("within seven days", " ".join(package["required_post_freeze_controls"]))
        self.assertIn("No substantively duplicative framework", package["maximum_novelty_statement"])

    def test_v1_3_prompts_are_hash_bound_and_preserve_agent_boundaries(self):
        manifest = load(PROMPT_MANIFEST)
        self.assertEqual(manifest["protocol_version"], "1.3")
        self.assertEqual(len(manifest["artifacts"]), 3)
        for row in manifest["artifacts"]:
            path = ROOT / row["path"]
            text = path.read_text(encoding="utf-8")
            self.assertEqual(digest(path), row["sha256"])
            self.assertIn("protocol version `1.3`", text)
            self.assertNotIn("protocol version `1.2`", text)
            self.assertEqual(text.count("{{INPUT_PACKET_JSON}}"), 1)
        contract = manifest["screening_contract"]
        self.assertTrue(contract["two_isolated_passes"])
        self.assertTrue(contract["separate_adjudication"])
        self.assertTrue(contract["accountable_author_material_citation_confirmation_required"])


if __name__ == "__main__":
    unittest.main()
