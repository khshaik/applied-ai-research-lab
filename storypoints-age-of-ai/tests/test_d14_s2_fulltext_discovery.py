import unittest

from gate2.d14_s2_fulltext_discovery import _public_oa_pdf


class D14SemanticScholarLocationTests(unittest.TestCase):
    def test_only_explicit_credential_free_https_pdf_is_accepted(self):
        record = {"paperId": "p1", "openAccessPdf": {"url": "https://example.org/paper.pdf", "status": "GREEN", "license": "CCBY"}}
        self.assertEqual(_public_oa_pdf(record)["basis"], "semantic_scholar_explicit_openAccessPdf")
        self.assertIsNone(_public_oa_pdf({"openAccessPdf": None}))
        self.assertIsNone(_public_oa_pdf({"openAccessPdf": {"url": "http://example.org/paper.pdf"}}))
        credential_bearing_url = "https://" + "user:secret@" + "example.org/paper.pdf"
        self.assertIsNone(_public_oa_pdf({"openAccessPdf": {"url": credential_bearing_url}}))


if __name__ == "__main__":
    unittest.main()
