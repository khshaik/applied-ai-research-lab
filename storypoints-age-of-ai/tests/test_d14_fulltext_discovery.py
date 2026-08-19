import unittest

from gate2.d14_fulltext_discovery import eligible_locations


class D14FulltextDiscoveryTests(unittest.TestCase):
    def test_only_publicly_marked_https_pdf_locations_are_retained(self):
        record = {
            "best_oa_location": {"is_oa": True, "pdf_url": "https://example.org/a.pdf", "license": "cc-by"},
            "primary_location": {"is_oa": False, "pdf_url": "https://example.org/closed.pdf"},
            "locations": [
                {"is_oa": True, "pdf_url": "http://example.org/insecure.pdf"},
                {"is_oa": True, "pdf_url": "https://example.org/a.pdf"},
                {"is_oa": True, "pdf_url": "https://example.net/b.pdf"},
            ],
        }
        rows = eligible_locations(record)
        self.assertEqual([r["url"] for r in rows], ["https://example.org/a.pdf", "https://example.net/b.pdf"])


if __name__ == "__main__":
    unittest.main()
