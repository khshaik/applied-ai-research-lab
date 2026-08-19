import unittest

from gate2.deduplicate_systematic import (
    arxiv_base,
    deduplicate,
    load_occurrences,
    normalize_doi,
    normalize_text,
    verify,
)


def record(rid, *, source="OpenAlex", source_id=None, doi="", arxiv_id="", title="Title", author="Author", year="2026", abstract="A"):
    return {
        "record_id": rid,
        "source": source,
        "source_id": source_id or rid,
        "doi": doi,
        "arxiv_id": arxiv_id,
        "title": title,
        "normalized_title": normalize_text(title),
        "authors": author,
        "normalized_first_author": normalize_text(author),
        "published": f"{year}-01-01",
        "publication_year": year,
        "updated": "",
        "abstract": abstract,
        "venue": "Venue",
        "record_type": "article",
        "url": "https://example.invalid",
        "evidence_stratum_candidate": "scholarly_status_unverified",
        "search_family": "S1",
        "retrieval_batch_id": "Q1",
    }


class SystematicDeduplicationTests(unittest.TestCase):
    def test_identifier_normalization(self):
        self.assertEqual(normalize_doi("https://doi.org/10.1000/ABC.1 "), "10.1000/abc.1")
        self.assertEqual(arxiv_base("10.48550/arXiv.2603.20028"), "2603.20028")
        self.assertEqual(arxiv_base("2603.20028v3"), "2603.20028")
        self.assertEqual(normalize_text("Café—Code: Review!"), "cafe code review")

    def test_exact_hierarchy_clusters_without_fuzzy_merges(self):
        rows = [
            record("r1", doi="10.1/a", title="A sufficiently long exact title"),
            record("r2", source="Semantic Scholar", doi="10.1/a", title="Different metadata title", abstract="Longer abstract"),
            record("r3", source="arXiv", arxiv_id="2603.20028", title="Another sufficiently long title"),
            record("r4", doi="10.48550/arxiv.2603.20028", arxiv_id="2603.20028", title="Published title variant"),
            record("r5", title="An exact normalized title for matching", author="First Author", year="2025"),
            record("r6", source="Semantic Scholar", title="An exact normalized title for matching!", author="First Author", year="2025"),
            record("r7", title="An exact normalized title for matching", author="Different Author", year="2025"),
        ]
        canonical, decisions, clusters = deduplicate(rows)
        self.assertEqual(len(canonical), 4)
        self.assertEqual(len(decisions), 3)
        self.assertEqual(sum(c["member_count"] for c in clusters), 7)
        self.assertEqual({d["match_basis"] for d in decisions}, {"doi", "arxiv_related_doi", "title_author_year"})

    def test_repeated_provider_record_is_exact_duplicate(self):
        rows = [
            record("r1", source_id="W1", title="Short"),
            record("r2", source_id="W1", title="Short", abstract="More complete abstract"),
        ]
        canonical, decisions, _ = deduplicate(rows)
        self.assertEqual(len(canonical), 1)
        self.assertEqual(decisions[0]["match_basis"], "manual_exact_duplicate")
        self.assertIn("exact repeated provider record", decisions[0]["evidence"])

    def test_frozen_input_count_and_record_ids_reconcile(self):
        rows = load_occurrences()
        self.assertEqual(len(rows), 5879)
        self.assertEqual(len({r["record_id"] for r in rows}), 5879)
        self.assertEqual({r["source"] for r in rows}, {"OpenAlex", "Semantic Scholar", "arXiv"})

    def test_published_d06_contract_reconciles(self):
        manifest = verify()
        self.assertEqual(manifest["raw_occurrence_count"], 5879)
        self.assertEqual(manifest["canonical_record_count"], 3962)
        self.assertEqual(manifest["duplicates_removed_count"], 1917)
        self.assertEqual(manifest["raw_occurrence_count"], manifest["canonical_record_count"] + manifest["duplicates_removed_count"])
        self.assertNotIn("fuzzy title", manifest["auto_merge_rules"])


if __name__ == "__main__":
    unittest.main()
