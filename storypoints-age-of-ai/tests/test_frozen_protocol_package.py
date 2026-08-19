import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "gate2" / "frozen_protocol_package_v1.3.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FrozenProtocolPackageTests(unittest.TestCase):
    def test_freeze_binds_exact_approval_and_prefreeze_package(self):
        package = json.loads(FROZEN.read_text(encoding="utf-8"))
        self.assertEqual(package["status"], "frozen")
        self.assertEqual(package["protocol_version"], "1.3")
        self.assertEqual(package["approval_decision"], "approve")
        self.assertEqual(
            package["approval_exact_phrase"],
            "Approve protocol v1.3 pre-freeze package and proceed to D04 freeze.",
        )
        for key in ("approved_prefreeze_package", "approval_record"):
            row = package[key]
            path = ROOT / row["path"]
            self.assertEqual(sha256(path), row["sha256"])

    def test_every_approved_artifact_remains_byte_exact(self):
        package = json.loads(FROZEN.read_text(encoding="utf-8"))
        prefreeze_path = ROOT / package["approved_prefreeze_package"]["path"]
        prefreeze = json.loads(prefreeze_path.read_text(encoding="utf-8"))
        for row in prefreeze["artifacts"]:
            path = ROOT / row["path"]
            self.assertEqual(sha256(path), row["sha256"], row["path"])

    def test_freeze_does_not_promote_developmental_outputs(self):
        package = json.loads(FROZEN.read_text(encoding="utf-8"))
        self.assertTrue(package["systematic_execution_authorized"])
        self.assertFalse(package["systematic_corpus_created"])
        self.assertFalse(package["developmental_outputs_are_systematic_records"])
        self.assertTrue(package["S2_fresh_execution_required"])
        self.assertEqual(package["submission_update_search_required_within_days"], 7)
        self.assertEqual(package["next_gate"], "D05")

    def test_package_and_record_sidecars_verify(self):
        checks = [
            (FROZEN, ROOT / "gate2/frozen_protocol_package_v1.3.json.sha256"),
            (ROOT / "02f_d03_d04_protocol_freeze_record.md", ROOT / "02f_d03_d04_protocol_freeze_record.md.sha256"),
        ]
        for artifact, sidecar in checks:
            expected = sidecar.read_text(encoding="utf-8").split()[0]
            self.assertEqual(sha256(artifact), expected)


if __name__ == "__main__":
    unittest.main()
