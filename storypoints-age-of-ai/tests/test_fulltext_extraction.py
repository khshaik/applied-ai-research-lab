import json
from pathlib import Path
import tempfile
import unittest

from gate2.pdf_extract_worker import extract


class FullTextExtractionTests(unittest.TestCase):
    def test_worker_extracts_real_frozen_pdf_without_executing_content(self):
        pdf = next(Path("gate2/output/systematic/v1.3/20260816/d10/pdf").glob("*.pdf"))
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "text.json"
            result = extract(pdf, output)
            self.assertIn(result["status"], {"text_extracted", "no_extractable_text"})
            self.assertGreater(result["page_count"], 0)
            self.assertIn("not executed", result["security_boundary"])
            self.assertEqual(json.loads(output.read_text())["pdf_sha256"], result["pdf_sha256"])


if __name__ == "__main__":
    unittest.main()
