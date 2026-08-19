from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from urllib.parse import parse_qs, urlparse

from gate2.arxiv_export import ExportError, export_query


def atom(total: int, start: int, ids: list[str]) -> bytes:
    entries = "".join(
        f"""<entry><id>https://arxiv.org/abs/{record_id}</id>
        <updated>2026-08-01T00:00:00Z</updated><published>2026-08-01T00:00:00Z</published>
        <title>Title {record_id}</title><summary>Abstract {record_id}</summary>
        <author><name>Researcher</name></author><category term="cs.SE"/></entry>"""
        for record_id in ids
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">
      <opensearch:totalResults>{total}</opensearch:totalResults>
      <opensearch:startIndex>{start}</opensearch:startIndex>
      <opensearch:itemsPerPage>{len(ids)}</opensearch:itemsPerPage>{entries}</feed>""".encode()


class ArxivExportTests(unittest.TestCase):
    def test_full_pagination_raw_pages_csv_and_checksums(self):
        pages = {0: atom(3, 0, ["2601.00001v1", "2601.00002v1"]),
                 2: atom(3, 2, ["2601.00003v2"])}

        def fetch(url: str) -> bytes:
            start = int(parse_qs(urlparse(url).query)["start"][0])
            return pages[start]

        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "nested" / "export"
            result = export_query(query_id="TEST", query="all:test", output_dir=target,
                                  page_size=2, fetcher=fetch, pause_seconds=0,
                                  expected_sentinels=("2601.00003", "9999.99999"))
            self.assertEqual(result["records_retrieved"], 3)
            self.assertTrue(result["complete_pagination"])
            self.assertTrue(result["sentinel_checks"]["2601.00003"])
            self.assertFalse(result["sentinel_checks"]["9999.99999"])
            self.assertFalse(result["sentinel_recall_pass"])
            self.assertEqual(len(list(target.glob("page_*.atom"))), 2)
            self.assertTrue((target / "records.csv").exists())
            manifest = json.loads((target / "manifest.json").read_text())
            self.assertEqual(manifest["status"], "development_pilot")
            self.assertEqual(len(manifest["records_csv"]["sha256"]), 64)
            self.assertEqual(len((target / "manifest.sha256").read_text().split()[0]), 64)

    def test_refuses_frozen_claim_and_existing_target(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "existing"
            target.mkdir()
            with self.assertRaisesRegex(ExportError, "status must"):
                export_query(query_id="T", query="all:test", output_dir=target,
                             status="frozen_systematic", fetcher=lambda _: b"")
            with self.assertRaisesRegex(ExportError, "already exists"):
                export_query(query_id="T", query="all:test", output_dir=target,
                             fetcher=lambda _: b"")

    def test_frozen_systematic_mode_is_hash_and_date_bound(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "gate2/output/systematic/v1.3/arxiv/Q"
            result = export_query(
                query_id="Q", query="all:test", output_dir=target,
                status="systematic_frozen", registry_sha256="a" * 64,
                freeze_package_sha256="b" * 64, matrix_row_sha256="c" * 64,
                fetcher=lambda _: atom(1, 0, ["2601.00001v1"]), pause_seconds=0,
            )
            self.assertEqual(result["retrieval_scope"], "complete_systematic")
            self.assertEqual(result["query_registry_sha256"], "a" * 64)

    def test_empty_page_before_reported_total_is_hard_error_and_atomic(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "export"
            with self.assertRaisesRegex(ExportError, "empty page"):
                export_query(query_id="T", query="all:test", output_dir=target,
                             fetcher=lambda _: atom(2, 0, []), pause_seconds=0)
            self.assertFalse(target.exists())

    def test_total_change_and_duplicate_ids_are_hard_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "volatile"
            pages = {0: atom(2, 0, ["2601.00001v1"]),
                     1: atom(3, 1, ["2601.00002v1"])}
            with self.assertRaisesRegex(ExportError, "volatile totalResults"):
                export_query(query_id="T", query="all:test", output_dir=target,
                             page_size=1,
                             fetcher=lambda url: pages[int(parse_qs(urlparse(url).query)["start"][0])],
                             pause_seconds=0)


if __name__ == "__main__":
    unittest.main()
