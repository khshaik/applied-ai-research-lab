from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from gate2.open_index_export import OpenIndexExportError, export_query, load_registry, main, resolve_registry_entry, resolve_registry_query


def payload(source: str, total: int, ids: list[str], token: str | None = None) -> bytes:
    if source == "openalex":
        value = {"meta": {"count": total, "next_cursor": token}, "results": [
            {"id": record_id, "doi": f"https://doi.org/10.1/{record_id}", "display_name": f"Title {record_id}",
             "abstract_inverted_index": {"Human": [0], "review": [1]}, "publication_date": "2026-01-01",
             "authorships": [{"author": {"display_name": "A Researcher"}}], "primary_location": {},
             "type": "article", "cited_by_count": 1} for record_id in ids]}
    elif source == "semantic_scholar":
        value = {"total": total, "data": [
            {"paperId": record_id, "externalIds": {"DOI": f"10.2/{record_id}"}, "title": f"Title {record_id}",
             "abstract": "Human review", "year": 2026, "authors": [{"name": "A Researcher"}],
             "citationCount": 1, "url": f"https://example.invalid/{record_id}"} for record_id in ids]}
        if token:
            value["token"] = token
    else:
        value = {"message": {"total-results": total, "items": [
            {"DOI": f"10.3/{record_id}", "title": [f"Title {record_id}"],
             "published": {"date-parts": [[2026, 1, 2]]},
             "author": [{"given": "A", "family": "Researcher"}], "type": "journal-article"}
            for record_id in ids]}}
        if token:
            value["message"]["next-cursor"] = token
    return json.dumps(value).encode()


class OpenIndexExportTests(unittest.TestCase):
    def test_each_source_full_pagination_raw_csv_and_manifest(self):
        for source in ("openalex", "semantic_scholar", "crossref"):
            with self.subTest(source=source), tempfile.TemporaryDirectory() as directory:
                pages = [payload(source, 3, ["a", "b"], "next"), payload(source, 3, ["c"], None)]
                requested: list[str] = []

                def fetch(url: str) -> bytes:
                    requested.append(url)
                    return pages[len(requested) - 1]

                target = Path(directory) / source / "run"
                result = export_query(source=source, query_id="S3", query="story points LLM",
                                      output_dir=target, page_size=2, fetcher=fetch,
                                      pause_seconds=0, registry_sha256="a" * 64)
                self.assertEqual(result["records_retrieved"], 3)
                self.assertTrue(result["complete_pagination"])
                self.assertEqual(len(list(target.glob("page_*.json"))), 2)
                self.assertTrue((target / "records.csv").exists())
                manifest = json.loads((target / "manifest.json").read_text())
                self.assertIn("not frozen", manifest["interpretation_boundary"])
                self.assertEqual(manifest["query_registry_sha256"], "a" * 64)
                self.assertEqual(len(manifest["records_csv"]["sha256"]), 64)
                query = parse_qs(urlparse(requested[1]).query)
                self.assertIn("cursor" if source != "semantic_scholar" else "token", query)

    def test_incomplete_empty_page_missing_or_repeated_cursor_fail_atomically(self):
        cases = [
            ("empty page", [payload("openalex", 2, [], "next")]),
            ("missing continuation", [payload("openalex", 2, ["a"], None)]),
            ("repeated", [payload("openalex", 3, ["a"], "same"), payload("openalex", 3, ["b"], "same")]),
        ]
        for message, pages in cases:
            with self.subTest(message=message), tempfile.TemporaryDirectory() as directory:
                calls = 0

                def fetch(_: str) -> bytes:
                    nonlocal calls
                    result = pages[calls]
                    calls += 1
                    return result

                target = Path(directory) / "run"
                with self.assertRaisesRegex(OpenIndexExportError, message):
                    export_query(source="openalex", query_id="T", query="test", output_dir=target,
                                 page_size=1, fetcher=fetch, pause_seconds=0)
                self.assertFalse(target.exists())

    def test_total_change_duplicate_ids_status_and_existing_target_are_hard_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "run"
            pages = iter([payload("crossref", 2, ["a"], "next"), payload("crossref", 3, ["b"], None)])
            with self.assertRaisesRegex(OpenIndexExportError, "volatile"):
                export_query(source="crossref", query_id="T", query="test", output_dir=target,
                             page_size=1, fetcher=lambda _: next(pages), pause_seconds=0)
            self.assertFalse(target.exists())
            with self.assertRaisesRegex(OpenIndexExportError, "status must"):
                export_query(source="openalex", query_id="T", query="test", output_dir=target,
                             status="frozen_systematic", fetcher=lambda _: b"{}")

    def test_frozen_systematic_mode_is_hash_bound_and_complete_only(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "gate2/output/systematic/v1.3/run"
            result = export_query(
                source="openalex", query_id="Q", query="test", output_dir=target,
                status="systematic_frozen", registry_sha256="a" * 64,
                freeze_package_sha256="b" * 64, matrix_row_sha256="c" * 64,
                api_key="test-key", fetcher=lambda _: payload("openalex", 1, ["a"]), pause_seconds=0,
            )
            self.assertEqual(result["retrieval_scope"], "complete_systematic")
            self.assertIn("Frozen systematic", result["interpretation_boundary"])
            self.assertEqual(result["freeze_package_sha256"], "b" * 64)
        with self.assertRaisesRegex(OpenIndexExportError, "cannot use max_pages"):
            export_query(
                source="openalex", query_id="Q", query="test",
                output_dir="gate2/output/systematic/v1.3/rejected",
                status="systematic_frozen", max_pages=1, registry_sha256="a" * 64,
                freeze_package_sha256="b" * 64, matrix_row_sha256="c" * 64,
            )
        with self.assertRaisesRegex(OpenIndexExportError, "OPENALEX_API_KEY"):
            export_query(
                source="openalex", query_id="Q", query="test",
                output_dir="gate2/output/systematic/v1.3/no-key",
                status="systematic_frozen", registry_sha256="a" * 64,
                freeze_package_sha256="b" * 64, matrix_row_sha256="c" * 64,
            )
            target.mkdir()
            with self.assertRaisesRegex(OpenIndexExportError, "already exists"):
                export_query(source="openalex", query_id="T", query="test", output_dir=target,
                             fetcher=lambda _: b"{}")

    def test_page_cap_is_explicitly_incomplete_and_not_a_review_count(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "run"
            result = export_query(source="crossref", query_id="T", query="broad discovery",
                                  output_dir=target, page_size=2, max_pages=1,
                                  fetcher=lambda _: payload("crossref", 1000, ["a", "b"], "next"),
                                  pause_seconds=0)
            self.assertFalse(result["complete_pagination"])
            self.assertEqual(result["retrieval_scope"], "truncated_development_pilot")
            self.assertIn("intentionally capped", result["interpretation_boundary"])
            self.assertEqual(result["records_retrieved"], 2)

    def test_registry_is_hashed_and_rejects_duplicate_source_query_id(self):
        registry_path = Path("gate2/open_index_pilot_queries.json")
        registry, digest = load_registry(registry_path)
        self.assertEqual(registry["status"], "development_pilot")
        self.assertEqual(len(digest), 64)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            row = {"source": "openalex", "query_id": "Q", "query": "test"}
            path.write_text(json.dumps({"status": "development_pilot", "queries": [row, row]}))
            with self.assertRaisesRegex(OpenIndexExportError, "duplicate"):
                load_registry(path)

    def test_registry_resolution_returns_exact_query_and_rejects_conflict_or_missing(self):
        path = Path("gate2/open_index_pilot_queries.json")
        query, digest = resolve_registry_query(path, "openalex", "OA-S3R")
        self.assertIn("software effort estimation", query)
        self.assertEqual(len(digest), 64)
        with self.assertRaisesRegex(OpenIndexExportError, "conflicts"):
            resolve_registry_query(path, "openalex", "OA-S3R", "different query")
        with self.assertRaisesRegex(OpenIndexExportError, "exactly one"):
            resolve_registry_query(path, "openalex", "MISSING")

    def test_cli_resolves_registry_query_and_passes_nonempty_registry_hash(self):
        manifest = {"status": "development_pilot", "source": "openalex", "query_id": "OA-S3R",
                    "total_reported": 1, "records_retrieved": 1, "complete_pagination": True}
        with patch("gate2.open_index_export.export_query", return_value=manifest) as exporter:
            main(["openalex", "OA-S3R", "/tmp/unused-test-target",
                  "--registry", "gate2/open_index_pilot_queries.json", "--max-pages", "1"])
        kwargs = exporter.call_args.kwargs
        self.assertIn("software effort estimation", kwargs["query"])
        self.assertEqual(len(kwargs["registry_sha256"]), 64)

    def test_cli_rejects_conflicting_literal_before_export(self):
        with patch("gate2.open_index_export.export_query") as exporter:
            with self.assertRaisesRegex(OpenIndexExportError, "conflicts"):
                main(["openalex", "OA-S3R", "/tmp/unused-test-target",
                      "--registry", "gate2/open_index_pilot_queries.json",
                      "--literal-query", "unregistered query"])
            exporter.assert_not_called()

    def test_openalex_title_abstract_mode_is_explicit_and_source_restricted(self):
        with tempfile.TemporaryDirectory() as directory:
            requested: list[str] = []

            def fetch(url: str) -> bytes:
                requested.append(url)
                return payload("openalex", 1, ["a"], None)

            result = export_query(
                source="openalex", query_id="OA-FIELD", query='"code review" AND LLM',
                query_mode="title_abstract_filter", output_dir=Path(directory) / "run",
                fetcher=fetch, pause_seconds=0,
            )
            parsed = parse_qs(urlparse(requested[0]).query)
            self.assertNotIn("search", parsed)
            self.assertIn("title_and_abstract.search:", parsed["filter"][0])
            self.assertEqual(result["query_mode"], "title_abstract_filter")
        with self.assertRaisesRegex(OpenIndexExportError, "restricted to OpenAlex"):
            export_query(source="semantic_scholar", query_id="bad", query="x",
                         query_mode="title_abstract_filter", output_dir="/tmp/unused-field-mode")

    def test_openalex_deterministic_publication_sort_is_explicit_and_restricted(self):
        with tempfile.TemporaryDirectory() as directory:
            requested: list[str] = []

            def fetch(url: str) -> bytes:
                requested.append(url)
                return payload("openalex", 1, ["a"], None)

            result = export_query(
                source="openalex", query_id="OA-SORT", query="code review",
                result_sort="publication_date:desc", output_dir=Path(directory) / "run",
                fetcher=fetch, pause_seconds=0,
            )
            parsed = parse_qs(urlparse(requested[0]).query)
            self.assertEqual(parsed["sort"], ["publication_date:desc"])
            self.assertEqual(result["result_sort"], "publication_date:desc")
        with self.assertRaisesRegex(OpenIndexExportError, "result_sort"):
            export_query(source="semantic_scholar", query_id="bad", query="x",
                         result_sort="publication_date:desc", output_dir="/tmp/unused-sort")

    def test_registry_entry_defaults_mode_and_preserves_explicit_mode(self):
        row, digest = resolve_registry_entry("gate2/open_index_pilot_queries.json", "openalex", "OA-S3R")
        self.assertEqual(row["query_mode"], "fulltext_search")
        self.assertEqual(len(digest), 64)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "registry.json"
            path.write_text(json.dumps({"status":"development_pilot","queries":[{
                "source":"openalex","query_id":"Q","query":"code review",
                "query_mode":"title_abstract_filter","result_sort":"publication_date:desc"
            }]}))
            row, _ = resolve_registry_entry(path, "openalex", "Q")
            self.assertEqual(row["query_mode"], "title_abstract_filter")
            self.assertEqual(row["result_sort"], "publication_date:desc")


if __name__ == "__main__":
    unittest.main()
