import copy
import json
import unittest
from pathlib import Path

from evidence_review.workflow import (
    NOVELTY_STATEMENT, ReviewValidationError, derive_evidence_matrix,
    derive_prisma, validate_bundle,
)


ROOT = Path(__file__).resolve().parents[1]


def complete_bundle():
    b = {
        "schema_version": "1.0.0",
        "metadata": {"review_id": "test", "protocol_version": "1.1",
                     "review_design": "ai_assisted_systematic_evidence_map_open_indexes",
                     "evidence_coverage": "access_constrained", "search_cutoff_date": "2026-08-14",
                     "status": "frozen_complete",
                     "accountable_author_ids": ["author-1"],
                     "search_completion": {"systematic_searches_complete": True, "update_search_complete": True},
                     "coverage_contract": {"required_search_family_ids": ["S1"],
                                           "required_source_ids": ["synthetic"],
                                           "required_search_pairs": [{"source": "synthetic", "search_family": "S1"}],
                                           "approved_unavailable_sources": []},
                     "novelty_claim_contract": {"allowed_statement": NOVELTY_STATEMENT,
                                                "reported_statement": NOVELTY_STATEMENT,
                                                "prohibited_unbounded_claims": ["No prior research exists.",
                                                                                "All relevant literature was searched."]}},
        "search_runs": [{"search_run_id": "s1", "source": "synthetic", "search_family": "S1",
                         "exact_query": "synthetic fixture only", "executed_at_utc": "2026-08-14T08:00:00Z",
                         "status": "approved_systematic", "results_returned": 2, "export_checksum": "synthetic-checksum"}],
        "records": [
            {"record_id": "r1", "title": "included", "source_type": "scholarly_database", "retrieval_batch_id": "s1",
             "evidence_stratum": "peer_reviewed_scholarly", "publication_status": "journal_article",
             "full_text_access_status": "lawful_open_full_text", "full_text_locator": "https://example.invalid/r1",
             "full_text_access_checked_at_utc": "2026-08-14T08:30:00Z", "full_text_access_checked_by": "access-agent"},
            {"record_id": "r2", "title": "duplicate", "source_type": "scholarly_database", "retrieval_batch_id": "s1",
             "evidence_stratum": "preprint_scholarly", "publication_status": "preprint",
             "full_text_access_status": "not_sought"},
        ],
        "deduplication_decisions": [{"deduplication_id": "d1", "removed_record_id": "r2",
                                      "retained_record_id": "r1", "match_basis": "title_author_year",
                                      "evidence": "synthetic normalized-title/author/year match",
                                      "decider_id": "dedup-agent", "decided_at_utc": "2026-08-14T08:40:00Z"}],
        "agent_screenings": [], "adjudications": [],
        "study_families": [{"family_id": "f1", "member_record_ids": ["r1"], "representative_record_id": "r1",
                            "consolidation_basis": "single eligible report", "linkage_signals": ["singleton"],
                            "family_reviewer_agent_id": "family-agent",
                            "status": "included_final", "author_source_confirmation_status": "confirmed",
                            "accountable_author_id": "author-1", "confirmed_at_utc": "2026-08-14T10:00:00Z"}],
        "quality_appraisals": [{"appraisal_id": "q1", "family_id": "f1", "appraisal_form": "quantitative_mixed",
                                "appraiser_agent_id": "quality-agent", "applicable_points": 20, "points_awarded": 15,
                                "critical_flaw": False, "evidence_band": "high", "source_locators": ["Methods; Table 2"]}],
        "extractions": [{"extraction_id": "x1", "family_id": "f1", "source_record_id": "r1", "claim_id": "claim-1",
                         "field_name": "sample_size", "value": 22, "unit": "participants", "data_nature": "observed",
                         "source_locator": "Methods, Participants", "extractor_agent_id": "extract-agent",
                         "verifier_agent_id": "verify-agent", "verification_status": "verified"}],
        "citation_confirmations": [{"confirmation_id": "c1", "extraction_id": "x1", "citation_key": "Example2026",
                                    "status": "confirmed", "supports_claim": True, "accountable_author_id": "author-1",
                                    "source_locator_checked": "Methods, Participants", "confirmed_at_utc": "2026-08-14T10:05:00Z"}],
        "citation_chases": [
            {"chase_id": "ch-back", "seed_family_id": "f1", "seed_record_id": "r1", "direction": "backward",
             "provider": "synthetic", "search_run_id": "s1", "executed_at_utc": "2026-08-14T10:10:00Z",
             "raw_export_checksum": "back-checksum", "discovered_record_ids": []},
            {"chase_id": "ch-forward", "seed_family_id": "f1", "seed_record_id": "r1", "direction": "forward",
             "provider": "synthetic", "search_run_id": "s1", "executed_at_utc": "2026-08-14T10:11:00Z",
             "raw_export_checksum": "forward-checksum", "discovered_record_ids": []},
        ],
        "prisma_events": [],
    }
    for stage in ("title_abstract", "full_text"):
        for n, decision in ((1, "include"), (2, "unclear" if stage == "full_text" else "include")):
            b["agent_screenings"].append({"screening_id": f"s-{stage}-{n}", "record_id": "r1", "stage": stage,
                "review_pass_id": f"pass-{n}", "reviewer_type": "ai_agent", "reviewer_id": f"agent-{n}",
                "model_prompt_version": "prompt-1", "review_context_id": f"isolated-{stage}-{n}",
                "prior_screening_decisions_visible": False, "input_checksum": f"same-{stage}-input",
                "decision": decision, "reason": "synthetic fixture",
                "confidence": 0.8, "source_locator": "synthetic abstract" if stage == "title_abstract" else "synthetic full text",
                "independence_attestation": "separate prompt sessions; shared-model limitation disclosed"})
    b["adjudications"].append({"adjudication_id": "a1", "record_id": "r1", "stage": "full_text",
                               "adjudicator_id": "agent-3", "review_context_id": "adjudication-context",
                               "decision": "include", "exclusion_code": None,
                               "rationale": "synthetic resolution", "source_locator": "synthetic full text"})
    actions = [("r1", "identified_database"), ("r2", "identified_database"), ("r2", "duplicate_removed"),
               ("r1", "screened_title_abstract"), ("r1", "sought_full_text"), ("r1", "assessed_full_text"),
               ("r1", "included_report")]
    b["prisma_events"] = [{"event_id": f"p{i}", "event_index": i,
                            "previous_event_id": None if i == 0 else f"p{i - 1}", "record_id": rid, "action": action,
                            "occurred_at_utc": "2026-08-14T09:00:00Z", "actor_id": "ledger-agent",
                            "basis": "synthetic test fixture", "exclusion_code": None}
                           for i, (rid, action) in enumerate(actions)]
    return b


class EvidenceReviewWorkflowTests(unittest.TestCase):
    def test_empty_template_is_valid_and_has_no_counts(self):
        template = json.loads((ROOT / "evidence_review/templates/review_bundle.template.json").read_text())
        schema = json.loads((ROOT / "evidence_review/schemas/review_bundle.schema.json").read_text())
        self.assertEqual(schema["properties"]["schema_version"]["const"], template["schema_version"])
        self.assertTrue(set(schema["required"]).issubset(template))
        validate_bundle(template)
        self.assertEqual(derive_prisma(template), {"status": "no_observations", "counts": None, "exclusions_by_code": None})

    def test_complete_synthetic_bundle_reconciles(self):
        bundle = complete_bundle()
        validate_bundle(bundle, require_complete=True)
        self.assertEqual(derive_prisma(bundle, final=True)["status"], "final_reconciled")
        matrix = derive_evidence_matrix(bundle)
        self.assertEqual(matrix["rows"][0]["representative_evidence_stratum"], "peer_reviewed_scholarly")
        self.assertEqual(matrix["rows"][0]["verified_extraction_count"], 1)

    def test_disagreement_requires_distinct_adjudication(self):
        bundle = complete_bundle()
        bundle["adjudications"] = []
        with self.assertRaisesRegex(ReviewValidationError, "requires adjudication"):
            validate_bundle(bundle, require_complete=True)

    def test_verified_extraction_requires_author_confirmation(self):
        bundle = complete_bundle()
        bundle["citation_confirmations"][0]["status"] = "pending"
        with self.assertRaisesRegex(ReviewValidationError, "accountable-author citation confirmation"):
            validate_bundle(bundle, require_complete=True)

    def test_family_membership_and_verifier_independence_are_enforced(self):
        bundle = complete_bundle()
        bundle["study_families"].append({"family_id": "f2", "member_record_ids": ["r1"],
                                         "representative_record_id": "r1", "consolidation_basis": "bad duplicate family",
                                         "linkage_signals": ["singleton"],
                                         "family_reviewer_agent_id": "family-agent", "status": "candidate"})
        bundle["extractions"][0]["verifier_agent_id"] = "extract-agent"
        with self.assertRaisesRegex(ReviewValidationError, "multiple study families"):
            validate_bundle(bundle)

    def test_nonconserving_prisma_ledger_hard_stops_finalization(self):
        bundle = complete_bundle()
        bundle["prisma_events"] = [e for e in bundle["prisma_events"] if e["action"] != "duplicate_removed"]
        with self.assertRaisesRegex(ReviewValidationError, "does not reconcile"):
            validate_bundle(bundle, require_complete=True)

    def test_final_mode_rejects_empty_review_and_incomplete_coverage(self):
        bundle = json.loads((ROOT / "evidence_review/templates/review_bundle.template.json").read_text())
        bundle["metadata"].update(status="frozen_complete", accountable_author_ids=["author-1"],
                                  search_completion={"systematic_searches_complete": True, "update_search_complete": True})
        with self.assertRaisesRegex(ReviewValidationError, "non-empty search runs"):
            validate_bundle(bundle, require_complete=True)

    def test_per_record_prisma_paths_cannot_hide_behind_balanced_totals(self):
        bundle = complete_bundle()
        bundle["prisma_events"][2]["record_id"] = "r1"  # r1 removed and screened; r2 has no disposition.
        with self.assertRaisesRegex(ReviewValidationError, "PRISMA record path"):
            validate_bundle(bundle, require_complete=True)

    def test_schema_independence_family_and_exact_citation_controls(self):
        bundle = complete_bundle()
        bundle["agent_screenings"][0].pop("model_prompt_version")
        with self.assertRaisesRegex(ReviewValidationError, "missing required property"):
            validate_bundle(bundle, require_complete=True)
        bundle = complete_bundle(); bundle["agent_screenings"][0]["independence_attestation"] = "same context"
        with self.assertRaisesRegex(ReviewValidationError, "independence"):
            validate_bundle(bundle, require_complete=True)
        bundle = complete_bundle(); bundle["extractions"][0]["source_record_id"] = "r2"
        with self.assertRaisesRegex(ReviewValidationError, "outside its study family"):
            validate_bundle(bundle, require_complete=True)
        bundle = complete_bundle(); bundle["citation_confirmations"][0]["source_locator_checked"] = "unrelated"
        with self.assertRaisesRegex(ReviewValidationError, "locator does not match"):
            validate_bundle(bundle, require_complete=True)

    def test_isolation_requires_distinct_contexts_and_identical_inputs(self):
        bundle = complete_bundle()
        bundle["agent_screenings"][1]["review_context_id"] = bundle["agent_screenings"][0]["review_context_id"]
        bundle["agent_screenings"][1]["input_checksum"] = "different-input"
        with self.assertRaisesRegex(ReviewValidationError, "isolated review contexts"):
            validate_bundle(bundle, require_complete=True)

    def test_access_state_and_citation_chasing_are_final_hard_stops(self):
        bundle = complete_bundle()
        bundle["records"][0]["full_text_access_status"] = "unavailable_paywall"
        with self.assertRaisesRegex(ReviewValidationError, "requires lawfully accessible full text"):
            validate_bundle(bundle, require_complete=True)
        bundle = complete_bundle(); bundle["citation_chases"] = bundle["citation_chases"][:1]
        with self.assertRaisesRegex(ReviewValidationError, "forward citation chase"):
            validate_bundle(bundle, require_complete=True)

    def test_duplicate_provenance_and_bounded_novelty_wording_are_final_hard_stops(self):
        bundle = complete_bundle(); bundle["deduplication_decisions"] = []
        with self.assertRaisesRegex(ReviewValidationError, "deduplication decisions do not match"):
            validate_bundle(bundle, require_complete=True)
        bundle = complete_bundle(); bundle["metadata"]["novelty_claim_contract"]["reported_statement"] = "No prior research exists."
        with self.assertRaisesRegex(ReviewValidationError, "access-bounded wording"):
            validate_bundle(bundle, require_complete=True)


if __name__ == "__main__":
    unittest.main()
