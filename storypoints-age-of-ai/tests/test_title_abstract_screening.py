import json
from pathlib import Path
import tempfile
import unittest

from gate2.title_abstract_screening import ScreeningControlError, prepare, validate_pass, verify_packet


class TitleAbstractScreeningTests(unittest.TestCase):
    def test_packet_is_complete_deterministic_and_immutable(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "d08"
            manifest = prepare(output)
            self.assertEqual(manifest["family_count"], 3930)
            self.assertEqual(manifest["shard_count"], 40)
            self.assertEqual(sum(row["row_count"] for row in manifest["shards"]), 3930)
            self.assertEqual(manifest, verify_packet(output))
            with self.assertRaises(ScreeningControlError):
                prepare(output)

    def test_pass_validation_rejects_incomplete_decisions(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "d08"
            manifest = prepare(output)
            shard = manifest["shards"][0]
            packet = json.loads((output / shard["path"]).read_text(encoding="utf-8").splitlines()[0])
            decision = {
                "family_id": packet["family_id"], "record_id": packet["record_id"],
                "stage": "title_abstract", "review_pass_id": "pass-a", "reviewer_type": "ai_agent",
                "reviewer_id": "test-a", "model_prompt_version": "screening-agent-a/1.1.0",
                "review_context_id": "isolated-a", "prior_screening_decisions_visible": False,
                "input_checksum": shard["sha256"], "decision": "exclude", "reason": "Fails frozen I1.",
                "confidence": 0.9, "source_locator": "packet title and abstract",
                "evidence_stratum": "peer_reviewed_scholarly",
                "independence_attestation": "Separate test context; no pass B decisions were visible.",
            }
            path = Path(directory) / "pass.jsonl"
            path.write_text(json.dumps(decision) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ScreeningControlError, "incomplete"):
                validate_pass(path, "pass-a", output)


if __name__ == "__main__":
    unittest.main()
