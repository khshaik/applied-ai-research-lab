import hashlib
import json
import unittest
from pathlib import Path

from evidence_review.workflow import derive_prisma, validate_bundle


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "evidence_review" / "fixtures"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ScreeningPromptArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((FIXTURES / "synthetic_calibration_manifest.json").read_text())
        cls.bundle = json.loads((FIXTURES / "synthetic_calibration_bundle.json").read_text())

    def test_manifest_hashes_every_versioned_artifact(self):
        self.assertEqual(self.manifest["hash_algorithm"], "sha256")
        roles = {row["role"] for row in self.manifest["artifacts"]}
        self.assertEqual(roles, {"screening_prompt_a", "screening_prompt_b", "adjudicator_prompt",
                                 "identical_input_packet", "synthetic_calibration_bundle"})
        for artifact in self.manifest["artifacts"]:
            path = ROOT / artifact["path"]
            self.assertTrue(path.is_file(), artifact["path"])
            self.assertEqual(sha256(path), artifact["sha256"], artifact["path"])
            self.assertRegex(artifact["version"], r"/1\.0\.0$")

    def test_two_screeners_use_identical_packet_and_are_blinded(self):
        contract = self.manifest["input_packet_contract"]
        packet = FIXTURES / "synthetic_calibration_input.json"
        self.assertEqual(contract["screening_pass_a_sha256"], sha256(packet))
        self.assertEqual(contract["screening_pass_a_sha256"], contract["screening_pass_b_sha256"])
        self.assertTrue(contract["require_identical_bytes"])
        self.assertFalse(contract["prior_screening_decisions_visible"])

        screenings = self.bundle["agent_screenings"]
        self.assertEqual(len(screenings), 2)
        self.assertEqual({row["input_checksum"] for row in screenings}, {sha256(packet)})
        self.assertEqual({row["prior_screening_decisions_visible"] for row in screenings}, {False})
        self.assertEqual(len({row["reviewer_id"] for row in screenings}), 2)
        self.assertEqual(len({row["review_context_id"] for row in screenings}), 2)

    def test_prompts_require_traceable_outputs_and_disclose_interpretation_boundary(self):
        required = set(self.manifest["required_screening_output_fields"])
        for name in ("screening_agent_a_v1.0.0.md", "screening_agent_b_v1.0.0.md"):
            text = (ROOT / "evidence_review" / "prompts" / name).read_text()
            self.assertEqual(text.count("{{INPUT_PACKET_JSON}}"), 1)
            for field in required:
                self.assertIn(f'"{field}"', text)
            self.assertIn("must not be reported as human inter-rater reliability", text)
            self.assertIn("prior_screening_decisions_visible", text)
            for stratum in self.manifest["allowed_evidence_strata"]:
                self.assertIn(stratum, text)

    def test_all_calibration_artifacts_target_protocol_1_2(self):
        packet = json.loads((FIXTURES / "synthetic_calibration_input.json").read_text())
        self.assertEqual(packet["criteria_version"], "protocol-1.2")
        self.assertEqual(self.bundle["metadata"]["protocol_version"], "1.2")
        for name in ("screening_agent_a_v1.0.0.md", "screening_agent_b_v1.0.0.md",
                     "adjudicator_v1.0.0.md"):
            text = (ROOT / "evidence_review" / "prompts" / name).read_text()
            self.assertIn("protocol version `1.2`", text)
            self.assertNotIn("protocol version `1.1`", text)

    def test_adjudicator_is_separate_and_does_not_vote_by_confidence(self):
        adjudication = self.bundle["adjudications"][0]
        screenings = self.bundle["agent_screenings"]
        self.assertNotIn(adjudication["adjudicator_id"], {row["reviewer_id"] for row in screenings})
        self.assertNotIn(adjudication["review_context_id"], {row["review_context_id"] for row in screenings})
        self.assertEqual(adjudication["input_checksum"], screenings[0]["input_checksum"])
        prompt = (ROOT / "evidence_review" / "prompts" / "adjudicator_v1.0.0.md").read_text()
        self.assertIn("do not decide by majority, average confidence", prompt)
        self.assertIn("must not be called human", prompt)

    def test_synthetic_bundle_is_valid_but_never_a_review_count(self):
        self.assertTrue(self.manifest["synthetic_only"])
        self.assertIn("no real records", self.manifest["publication_boundary"].lower())
        self.assertIn("not human inter-rater reliability", self.manifest["interpretation_boundary"])
        validate_bundle(self.bundle)
        self.assertEqual(derive_prisma(self.bundle)["status"], "no_observations")
        self.assertIsNone(derive_prisma(self.bundle)["counts"])
        self.assertEqual({row["evidence_stratum"] for row in self.bundle["agent_screenings"]},
                         {"peer_reviewed_scholarly"})


if __name__ == "__main__":
    unittest.main()
