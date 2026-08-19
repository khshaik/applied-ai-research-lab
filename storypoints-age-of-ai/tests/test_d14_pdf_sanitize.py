import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from gate2.d14_secure_fulltext import active_indicators
from gate2.d14_pdf_sanitize import _replace_invalid_surrogates


ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".pdf-venv" / "bin" / "python"


@unittest.skipUnless(PYTHON.exists(), "project-local PDF environment not installed")
class D14PdfSanitizeTests(unittest.TestCase):
    def test_invalid_surrogate_is_replaced_and_counted(self):
        value, count = _replace_invalid_surrogates("valid\ud83dtext")
        self.assertEqual(value, "valid\ufffdtext")
        self.assertEqual(count, 1)

    def test_uri_annotation_is_removed_and_text_is_static(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = base / "source.pdf"
            derivative = base / "derivative.pdf"
            text = base / "text.json"
            create = (
                "from pypdf import PdfWriter; from pypdf.generic import RectangleObject; "
                f"w=PdfWriter(); w.add_blank_page(width=200,height=200); "
                "w.add_uri(0,'https://example.org',RectangleObject([0,0,100,20])); "
                f"w.write(r'{source}')"
            )
            subprocess.run([str(PYTHON), "-c", create], cwd=ROOT, check=True)
            self.assertIn("/S /URI", active_indicators(source.read_bytes()))
            run = subprocess.run(
                [str(PYTHON), "-m", "gate2.d14_pdf_sanitize", "worker", str(source), str(derivative), str(text)],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                check=True,
            )
            result = json.loads(run.stdout)
            self.assertEqual(result["status"], "sanitized_static_extraction_verified")
            self.assertEqual(active_indicators(derivative.read_bytes()), [])
            payload = json.loads(text.read_text())
            self.assertEqual(payload["page_count"], 1)


if __name__ == "__main__":
    unittest.main()
