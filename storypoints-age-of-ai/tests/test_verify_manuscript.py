import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "verify_manuscript", ROOT / "scripts/verify_manuscript.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ManuscriptVerificationTests(unittest.TestCase):
    def test_current_scientific_draft_passes_after_d17_confirmation(self):
        result = MODULE.validate(release=False, root=ROOT)
        self.assertTrue(result["ready"], result["errors"])
        self.assertEqual(result["figures"], 6)
        self.assertEqual(result["material_claims"], 10)
        self.assertFalse(any("B05" in item for item in result["warnings"]))
        self.assertFalse(any("protocol is not frozen" in item for item in result["warnings"]))
        self.assertEqual(result["confirmed_claims"], 10)
        self.assertFalse(any("unresolved manuscript markers" in item for item in result["warnings"]))

    def test_release_content_gate_passes_after_d17_confirmation(self):
        result = MODULE.validate(release=True, root=ROOT)
        self.assertTrue(result["ready"], result["errors"])
        self.assertEqual(result["confirmed_claims"], 10)
        self.assertEqual(result["warnings"], [])


if __name__ == "__main__":
    unittest.main()
