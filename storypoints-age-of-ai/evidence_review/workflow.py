"""Validate and reconcile the Gate 2 evidence-review bundle.

The module deliberately uses only the Python standard library.  It validates
workflow invariants that are awkward to express in JSON Schema and derives
PRISMA counts from an append-only event ledger.  It never performs searches or
makes study decisions.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from simulation.config import ConfigError, validate_config


class ReviewValidationError(ValueError):
    """Raised when a review bundle violates a governance hard stop."""


DECISIONS = {"include", "exclude", "unclear"}
STAGES = {"title_abstract", "full_text"}
EXCLUSION_CODES = {f"E{i}" for i in range(1, 11)}
PRISMA_ACTIONS = {
    "identified_database", "identified_other", "duplicate_removed",
    "screened_title_abstract", "excluded_title_abstract", "sought_full_text",
    "full_text_unavailable", "assessed_full_text", "excluded_full_text",
    "included_report",
}
EVIDENCE_STRATA = {
    "peer_reviewed_scholarly", "preprint_scholarly",
    "grey_practitioner", "method_reference",
}
ACCESSIBLE_FULL_TEXT_STATES = {
    "lawful_open_full_text", "lawful_author_manuscript",
    "lawful_preprint_version", "authorized_subscription_access",
}
UNAVAILABLE_FULL_TEXT_STATES = {"unavailable_paywall", "unavailable_other"}
FULL_TEXT_STATES = {"not_sought"} | ACCESSIBLE_FULL_TEXT_STATES | UNAVAILABLE_FULL_TEXT_STATES
NOVELTY_STATEMENT = (
    "No substantively duplicative framework was identified within the predeclared "
    "open scholarly indexes, repositories, and citation networks searched through "
    "the stated cutoff date."
)
SCHEMA_PATH = Path(__file__).with_name("schemas") / "review_bundle.schema.json"


def _unique(rows: list[dict[str, Any]], field: str, label: str, errors: list[str]) -> set[str]:
    values: list[str] = []
    for i, row in enumerate(rows):
        value = row.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{label}[{i}].{field} must be a non-empty string")
        else:
            values.append(value)
    duplicates = {value for value, count in Counter(values).items() if count > 1}
    if duplicates:
        errors.append(f"duplicate {label} {field}: {sorted(duplicates)}")
    return set(values)


def validate_bundle(bundle: dict[str, Any], *, require_complete: bool = False) -> None:
    """Validate traceability, independence, consolidation, and author controls.

    ``require_complete`` activates final-review hard stops.  The empty template
    remains valid while searches and decisions are pending.
    """
    errors: list[str] = []
    try:
        validate_config(bundle, SCHEMA_PATH)
    except ConfigError as error:
        errors.append(str(error))
    required_arrays = (
        "search_runs", "records", "deduplication_decisions", "agent_screenings",
        "adjudications", "study_families", "citation_chases", "quality_appraisals",
        "extractions", "citation_confirmations", "prisma_events",
    )
    for name in required_arrays:
        if not isinstance(bundle.get(name), list):
            errors.append(f"{name} must be an array")
    if errors:
        raise ReviewValidationError("review bundle invalid:\n" + "\n".join(errors))

    meta = bundle.get("metadata")
    if not isinstance(meta, dict):
        errors.append("metadata must be an object")
        meta = {}
    authors = set(meta.get("accountable_author_ids", []))
    if not authors or any(not isinstance(x, str) or not x for x in authors):
        errors.append("metadata.accountable_author_ids requires at least one non-empty ID")
    if meta.get("review_design") != "ai_assisted_systematic_evidence_map_open_indexes":
        errors.append("metadata.review_design must declare the approved open-index evidence-map route")
    if meta.get("evidence_coverage") != "access_constrained":
        errors.append("metadata.evidence_coverage must be access_constrained")
    novelty_contract = meta.get("novelty_claim_contract", {})
    prohibited = set(novelty_contract.get("prohibited_unbounded_claims", []))
    required_prohibitions = {"No prior research exists.", "All relevant literature was searched."}
    if not required_prohibitions <= prohibited:
        errors.append("novelty claim contract must prohibit both unbounded claims")

    search_runs = bundle["search_runs"]
    records = bundle["records"]
    deduplications = bundle["deduplication_decisions"]
    screenings = bundle["agent_screenings"]
    adjudications = bundle["adjudications"]
    families = bundle["study_families"]
    chases = bundle["citation_chases"]
    appraisals = bundle["quality_appraisals"]
    extractions = bundle["extractions"]
    confirmations = bundle["citation_confirmations"]
    events = bundle["prisma_events"]

    search_run_ids = _unique(search_runs, "search_run_id", "search_runs", errors)
    record_ids = _unique(records, "record_id", "records", errors)
    _unique(deduplications, "deduplication_id", "deduplication_decisions", errors)
    _unique(screenings, "screening_id", "agent_screenings", errors)
    _unique(adjudications, "adjudication_id", "adjudications", errors)
    family_ids = _unique(families, "family_id", "study_families", errors)
    _unique(chases, "chase_id", "citation_chases", errors)
    _unique(appraisals, "appraisal_id", "quality_appraisals", errors)
    extraction_ids = _unique(extractions, "extraction_id", "extractions", errors)
    _unique(confirmations, "confirmation_id", "citation_confirmations", errors)
    _unique(events, "event_id", "prisma_events", errors)

    for run in search_runs:
        if run.get("status") not in {"approved_systematic", "pilot_excluded", "update_systematic"}:
            errors.append(f"search run {run.get('search_run_id')} has invalid status")
        if not run.get("exact_query") or not run.get("executed_at_utc"):
            errors.append(f"search run {run.get('search_run_id')} lacks query/execution time")
        if run.get("status") != "pilot_excluded" and not run.get("export_checksum"):
            errors.append(f"systematic search run {run.get('search_run_id')} lacks export checksum")
    for record in records:
        if record.get("retrieval_batch_id") not in search_run_ids:
            errors.append(f"record {record.get('record_id')} references unknown search run")
        matching = [x for x in search_runs if x.get("search_run_id") == record.get("retrieval_batch_id")]
        if matching and matching[0].get("status") == "pilot_excluded":
            errors.append(f"record {record.get('record_id')} improperly imports a pilot-only search result")
        if record.get("evidence_stratum") not in EVIDENCE_STRATA:
            errors.append(f"record {record.get('record_id')} has invalid evidence_stratum")
        access = record.get("full_text_access_status")
        if access not in FULL_TEXT_STATES:
            errors.append(f"record {record.get('record_id')} has invalid full_text_access_status")
        if access in ACCESSIBLE_FULL_TEXT_STATES and not record.get("full_text_locator"):
            errors.append(f"record {record.get('record_id')} has accessible full text without a locator")
        if access != "not_sought" and not record.get("full_text_access_checked_at_utc"):
            errors.append(f"record {record.get('record_id')} lacks full-text access check time")
        if access != "not_sought" and not record.get("full_text_access_checked_by"):
            errors.append(f"record {record.get('record_id')} lacks full-text access checker")

    duplicate_index: dict[str, dict[str, Any]] = {}
    for row in deduplications:
        removed, retained = row.get("removed_record_id"), row.get("retained_record_id")
        if removed in duplicate_index:
            errors.append(f"multiple deduplication decisions remove record {removed}")
        duplicate_index[str(removed)] = row
        if removed not in record_ids or retained not in record_ids or removed == retained:
            errors.append(f"deduplication {row.get('deduplication_id')} has invalid removed/retained records")
        if row.get("match_basis") not in {"doi", "arxiv_related_doi", "title_author_year", "manual_exact_duplicate"}:
            errors.append(f"deduplication {row.get('deduplication_id')} has invalid match_basis")
        if not row.get("evidence") or not row.get("decided_at_utc") or not row.get("decider_id"):
            errors.append(f"deduplication {row.get('deduplication_id')} lacks evidence/time/decider")

    screen_index: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    seen_passes: set[tuple[str, str, str]] = set()
    for row in screenings:
        rid, stage = row.get("record_id"), row.get("stage")
        if rid not in record_ids:
            errors.append(f"screening {row.get('screening_id')} references unknown record {rid!r}")
        if stage not in STAGES:
            errors.append(f"screening {row.get('screening_id')} has invalid stage {stage!r}")
        if row.get("reviewer_type") != "ai_agent":
            errors.append(f"screening {row.get('screening_id')} reviewer_type must be ai_agent")
        if row.get("decision") not in DECISIONS:
            errors.append(f"screening {row.get('screening_id')} has invalid decision")
        if not row.get("source_locator"):
            errors.append(f"screening {row.get('screening_id')} lacks a source locator")
        attestation = row.get("independence_attestation")
        if not isinstance(attestation, str) or len(attestation.strip()) < 20:
            errors.append(f"screening {row.get('screening_id')} lacks a substantive independence/limitations attestation")
        if row.get("prior_screening_decisions_visible") is not False:
            errors.append(f"screening {row.get('screening_id')} must be blinded to prior screening decisions")
        if not row.get("review_context_id") or not row.get("input_checksum"):
            errors.append(f"screening {row.get('screening_id')} lacks review context/input checksum")
        key = (str(rid), str(stage), str(row.get("review_pass_id")))
        if key in seen_passes:
            errors.append(f"duplicate review pass for {rid}/{stage}/{row.get('review_pass_id')}")
        seen_passes.add(key)
        screen_index[(str(rid), str(stage))].append(row)

    adjudication_index: dict[tuple[str, str], dict[str, Any]] = {}
    for row in adjudications:
        key = (str(row.get("record_id")), str(row.get("stage")))
        if key in adjudication_index:
            errors.append(f"multiple adjudications for {key[0]}/{key[1]}")
        adjudication_index[key] = row
        if key[0] not in record_ids or key[1] not in STAGES:
            errors.append(f"adjudication {row.get('adjudication_id')} has unknown record/stage")
        if row.get("decision") not in {"include", "exclude"}:
            errors.append(f"adjudication {row.get('adjudication_id')} must resolve to include/exclude")
        if not row.get("rationale") or not row.get("source_locator"):
            errors.append(f"adjudication {row.get('adjudication_id')} lacks rationale/source locator")
        if not row.get("review_context_id"):
            errors.append(f"adjudication {row.get('adjudication_id')} lacks separate review context")
        screen_agents = {x.get("reviewer_id") for x in screen_index.get(key, [])}
        screen_contexts = {x.get("review_context_id") for x in screen_index.get(key, [])}
        if row.get("adjudicator_id") in screen_agents:
            errors.append(f"adjudicator for {key[0]}/{key[1]} must differ from screening agents")
        if row.get("review_context_id") in screen_contexts:
            errors.append(f"adjudicator for {key[0]}/{key[1]} must use a separate review context")
        if row.get("decision") == "exclude" and key[1] == "full_text" and row.get("exclusion_code") not in EXCLUSION_CODES:
            errors.append(f"full-text exclusion for {key[0]} requires one E1-E10 code")

    record_membership: dict[str, str] = {}
    for family in families:
        members = family.get("member_record_ids", [])
        if not isinstance(members, list) or not members:
            errors.append(f"family {family.get('family_id')} requires member_record_ids")
            continue
        unknown = set(members) - record_ids
        if unknown:
            errors.append(f"family {family.get('family_id')} has unknown members {sorted(unknown)}")
        if family.get("representative_record_id") not in members:
            errors.append(f"family {family.get('family_id')} representative must be a member")
        if not family.get("consolidation_basis"):
            errors.append(f"family {family.get('family_id')} lacks consolidation_basis")
        signals = family.get("linkage_signals")
        allowed_signals = {"singleton", "doi_relation", "arxiv_related_doi", "title_author_year",
                           "explicit_version_statement", "shared_sample_project", "correction_companion", "manual_other"}
        if not isinstance(signals, list) or not signals or not set(signals) <= allowed_signals:
            errors.append(f"family {family.get('family_id')} requires valid linkage_signals")
        elif len(members) > 1 and "singleton" in signals:
            errors.append(f"multi-report family {family.get('family_id')} cannot use singleton linkage")
        elif len(members) == 1 and signals != ["singleton"]:
            errors.append(f"single-report family {family.get('family_id')} must use singleton linkage")
        for rid in members:
            if rid in record_membership:
                errors.append(f"record {rid} belongs to multiple study families")
            record_membership[rid] = str(family.get("family_id"))
        if family.get("status") == "included_final":
            if family.get("author_source_confirmation_status") != "confirmed":
                errors.append(f"included family {family.get('family_id')} lacks accountable-author source confirmation")
            if family.get("accountable_author_id") not in authors:
                errors.append(f"included family {family.get('family_id')} confirmation is not by an accountable author")

    chase_index: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in chases:
        fid, direction = row.get("seed_family_id"), row.get("direction")
        if fid not in family_ids or row.get("seed_record_id") not in record_ids:
            errors.append(f"citation chase {row.get('chase_id')} references unknown seed family/record")
        elif row.get("seed_record_id") not in next(x["member_record_ids"] for x in families if x.get("family_id") == fid):
            errors.append(f"citation chase {row.get('chase_id')} seed record is outside its family")
        if direction not in {"backward", "forward"}:
            errors.append(f"citation chase {row.get('chase_id')} has invalid direction")
        if row.get("search_run_id") not in search_run_ids:
            errors.append(f"citation chase {row.get('chase_id')} references unknown search run")
        if not row.get("provider") or not row.get("executed_at_utc") or not row.get("raw_export_checksum"):
            errors.append(f"citation chase {row.get('chase_id')} lacks provider/time/checksum")
        discovered = row.get("discovered_record_ids")
        if not isinstance(discovered, list) or len(discovered) != len(set(discovered)) or not set(discovered) <= record_ids:
            errors.append(f"citation chase {row.get('chase_id')} has invalid discovered_record_ids")
        else:
            for rid in discovered:
                rec = next(x for x in records if x.get("record_id") == rid)
                if rec.get("retrieval_batch_id") != row.get("search_run_id"):
                    errors.append(f"citation chase {row.get('chase_id')} discovered record {rid} from another batch")
        chase_index[(str(fid), str(direction))].append(row)

    for row in appraisals:
        if row.get("family_id") not in family_ids:
            errors.append(f"appraisal {row.get('appraisal_id')} references unknown family")
        applicable, awarded = row.get("applicable_points"), row.get("points_awarded")
        if not isinstance(applicable, int) or applicable <= 0 or not isinstance(awarded, int) or not 0 <= awarded <= applicable:
            errors.append(f"appraisal {row.get('appraisal_id')} has invalid points")
        if row.get("evidence_band") not in {"high", "moderate", "low_contextual"}:
            errors.append(f"appraisal {row.get('appraisal_id')} has invalid evidence band")
        if not row.get("source_locators"):
            errors.append(f"appraisal {row.get('appraisal_id')} lacks source locators")

    for row in extractions:
        if row.get("family_id") not in family_ids:
            errors.append(f"extraction {row.get('extraction_id')} references unknown family")
        if not row.get("source_locator") or not row.get("source_record_id"):
            errors.append(f"extraction {row.get('extraction_id')} lacks record/source locator")
        if row.get("source_record_id") not in record_ids:
            errors.append(f"extraction {row.get('extraction_id')} references unknown source record")
        elif record_membership.get(str(row.get("source_record_id"))) != row.get("family_id"):
            errors.append(f"extraction {row.get('extraction_id')} source record is outside its study family")
        if row.get("data_nature") not in {"observed", "self_reported", "modeled", "conceptual", "mixed"}:
            errors.append(f"extraction {row.get('extraction_id')} has invalid data_nature")
        if row.get("verification_status") == "verified":
            if row.get("extractor_agent_id") == row.get("verifier_agent_id"):
                errors.append(f"verified extraction {row.get('extraction_id')} needs a distinct verifier")
            if not row.get("verifier_agent_id"):
                errors.append(f"verified extraction {row.get('extraction_id')} lacks verifier")

    confirmation_by_extraction: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in confirmations:
        eid = row.get("extraction_id")
        if eid not in extraction_ids:
            errors.append(f"confirmation {row.get('confirmation_id')} references unknown extraction")
        confirmation_by_extraction[str(eid)].append(row)
        if row.get("status") not in {"pending", "confirmed", "rejected"}:
            errors.append(f"confirmation {row.get('confirmation_id')} has invalid status")
        if row.get("status") == "confirmed":
            if row.get("accountable_author_id") not in authors:
                errors.append(f"confirmation {row.get('confirmation_id')} is not by an accountable author")
            if not row.get("confirmed_at_utc") or not row.get("source_locator_checked"):
                errors.append(f"confirmation {row.get('confirmation_id')} lacks time/source check")
            extraction = next((x for x in extractions if x.get("extraction_id") == eid), None)
            if row.get("supports_claim") is not True:
                errors.append(f"confirmation {row.get('confirmation_id')} does not affirm support for the claim")
            if extraction is not None and row.get("source_locator_checked") != extraction.get("source_locator"):
                errors.append(f"confirmation {row.get('confirmation_id')} locator does not match the extraction")

    for i, event in enumerate(events):
        if event.get("action") not in PRISMA_ACTIONS:
            errors.append(f"PRISMA event {event.get('event_id')} has invalid action")
        if event.get("record_id") not in record_ids:
            errors.append(f"PRISMA event {event.get('event_id')} references unknown record")
        if event.get("action") == "excluded_full_text" and event.get("exclusion_code") not in EXCLUSION_CODES:
            errors.append(f"PRISMA full-text exclusion {event.get('event_id')} requires E1-E10")
        if event.get("event_index") != i:
            errors.append(f"PRISMA event {event.get('event_id')} has non-contiguous event_index")
        expected_previous = None if i == 0 else events[i - 1].get("event_id")
        if event.get("previous_event_id") != expected_previous:
            errors.append(f"PRISMA event {event.get('event_id')} breaks append-only predecessor chain")
        record = next((x for x in records if x.get("record_id") == event.get("record_id")), None)
        if record is not None and event.get("action") in {"assessed_full_text", "excluded_full_text", "included_report"}:
            if record.get("full_text_access_status") not in ACCESSIBLE_FULL_TEXT_STATES:
                errors.append(f"PRISMA event {event.get('event_id')} requires lawfully accessible full text")
        if record is not None and event.get("action") == "full_text_unavailable":
            if record.get("full_text_access_status") not in UNAVAILABLE_FULL_TEXT_STATES:
                errors.append(f"PRISMA event {event.get('event_id')} conflicts with full-text access state")

    if require_complete:
        completion = meta.get("search_completion", {})
        if completion.get("systematic_searches_complete") is not True or completion.get("update_search_complete") is not True:
            errors.append("final reconciliation requires completed systematic and update searches")
        if meta.get("status") != "frozen_complete":
            errors.append("final reconciliation requires metadata.status=frozen_complete")
        if not meta.get("search_cutoff_date"):
            errors.append("final reconciliation requires metadata.search_cutoff_date")
        if any("PENDING" in author.upper() for author in authors):
            errors.append("final reconciliation prohibits placeholder accountable-author IDs")
        if not search_runs or not record_ids or not events:
            errors.append("final reconciliation requires non-empty search runs, records, and PRISMA events")
        coverage = meta.get("coverage_contract", {})
        required_families = set(coverage.get("required_search_family_ids", []))
        required_sources = set(coverage.get("required_source_ids", []))
        required_pairs = {(x.get("source"), x.get("search_family")) for x in coverage.get("required_search_pairs", [])}
        unavailable = coverage.get("approved_unavailable_sources", [])
        if not required_families or not required_sources or not required_pairs:
            errors.append("final reconciliation requires non-empty search-family, source, and source/family-pair coverage contracts")
        executed = [x for x in search_runs if x.get("status") in {"approved_systematic", "update_systematic"}]
        missing_families = required_families - {x.get("search_family") for x in executed}
        unavailable_sources = {
            x.get("source") for x in unavailable
            if x.get("deviation_id") and x.get("rationale")
            and x.get("access_state") in {"blocked_authentication", "blocked_rate_limit", "blocked_technical"}
            and x.get("attempted_at_utc") and x.get("approved_by_author_id") in authors
        }
        missing_sources = required_sources - {x.get("source") for x in executed} - unavailable_sources
        executed_pairs = {(x.get("source"), x.get("search_family")) for x in executed}
        missing_pairs = {pair for pair in required_pairs if pair[0] not in unavailable_sources} - executed_pairs
        if missing_families:
            errors.append(f"unexecuted required search families: {sorted(missing_families)}")
        if missing_sources:
            errors.append(f"uncovered required sources: {sorted(missing_sources)}")
        if missing_pairs:
            errors.append(f"unexecuted required source/family pairs: {sorted(missing_pairs)}")
        stage_records = {
            "title_abstract": {e.get("record_id") for e in events if e.get("action") == "screened_title_abstract"},
            "full_text": {e.get("record_id") for e in events if e.get("action") == "assessed_full_text"},
        }
        for stage, expected_records in stage_records.items():
            for rid in expected_records:
                passes = screen_index.get((rid, stage), [])
                if len(passes) != 2 or len({x.get('reviewer_id') for x in passes}) != 2:
                    errors.append(f"{rid}/{stage} requires exactly two distinct agent review passes")
                if len({x.get('review_context_id') for x in passes}) != 2:
                    errors.append(f"{rid}/{stage} requires two isolated review contexts")
                if len({x.get('input_checksum') for x in passes}) != 1:
                    errors.append(f"{rid}/{stage} agent passes must screen identical input")
                decisions = {x.get("decision") for x in passes}
                if "unclear" in decisions or len(decisions) > 1:
                    if (rid, stage) not in adjudication_index:
                        errors.append(f"{rid}/{stage} disagreement/unclear requires adjudication")
        for extraction in extractions:
            if extraction.get("verification_status") == "verified":
                confirmed = any(x.get("status") == "confirmed" for x in confirmation_by_extraction[extraction["extraction_id"]])
                if not confirmed:
                    errors.append(f"verified extraction {extraction['extraction_id']} lacks accountable-author citation confirmation")
        included_reports = {e.get("record_id") for e in events if e.get("action") == "included_report"}
        for rid in included_reports:
            if rid not in record_membership:
                errors.append(f"included report {rid} is not assigned to a study family")
            elif next(x for x in families if x.get("family_id") == record_membership[rid]).get("status") != "included_final":
                errors.append(f"included report {rid} belongs to a non-included study family")
        for family in families:
            if family.get("status") == "included_final" and family.get("representative_record_id") not in included_reports:
                errors.append(f"included family {family.get('family_id')} representative is not an included report")
            if family.get("status") == "included_final":
                if not any(x.get("family_id") == family.get("family_id") for x in appraisals):
                    errors.append(f"included family {family.get('family_id')} lacks a quality appraisal")
                for direction in ("backward", "forward"):
                    if len(chase_index.get((family.get("family_id"), direction), [])) != 1:
                        errors.append(f"included family {family.get('family_id')} requires one completed {direction} citation chase")
        duplicate_events = {e.get("record_id") for e in events if e.get("action") == "duplicate_removed"}
        if duplicate_events != set(duplicate_index):
            errors.append("duplicate-removal ledger events and deduplication decisions do not match")
        novelty = meta.get("novelty_claim_contract", {})
        if novelty.get("reported_statement") != NOVELTY_STATEMENT:
            errors.append("final novelty statement must use the approved access-bounded wording exactly")
        _validate_prisma_record_paths(records, events)
        derive_prisma(bundle, final=True)

    if errors:
        raise ReviewValidationError("review bundle invalid:\n" + "\n".join(errors))


def _validate_prisma_record_paths(records: list[dict[str, Any]], events: list[dict[str, Any]]) -> None:
    paths: dict[str, list[str]] = defaultdict(list)
    for event in events:
        paths[str(event.get("record_id"))].append(str(event.get("action")))
    suffixes = {
        ("duplicate_removed",),
        ("screened_title_abstract", "excluded_title_abstract"),
        ("screened_title_abstract", "sought_full_text", "full_text_unavailable"),
        ("screened_title_abstract", "sought_full_text", "assessed_full_text", "excluded_full_text"),
        ("screened_title_abstract", "sought_full_text", "assessed_full_text", "included_report"),
    }
    failures = []
    for record in records:
        actions = paths.get(record["record_id"], [])
        first = "identified_database" if record.get("source_type") == "scholarly_database" else "identified_other"
        if not actions or actions[0] != first or tuple(actions[1:]) not in suffixes:
            failures.append(f"{record['record_id']}: invalid PRISMA transition path {actions!r}")
    if failures:
        raise ReviewValidationError("PRISMA record path does not reconcile:\n" + "\n".join(failures))


def derive_prisma(bundle: dict[str, Any], *, final: bool = False) -> dict[str, Any]:
    """Derive (never manually enter) PRISMA counts from unique ledger events."""
    events = bundle.get("prisma_events", [])
    if not events:
        return {"status": "no_observations", "counts": None, "exclusions_by_code": None}
    by_action: dict[str, set[str]] = defaultdict(set)
    exclusion_codes: Counter[str] = Counter()
    for event in events:
        action, rid = event.get("action"), event.get("record_id")
        if action in PRISMA_ACTIONS and isinstance(rid, str):
            by_action[action].add(rid)
        if action == "excluded_full_text" and event.get("exclusion_code") in EXCLUSION_CODES:
            exclusion_codes[event["exclusion_code"]] += 1
    counts = {name: len(by_action[name]) for name in sorted(PRISMA_ACTIONS)}
    if final:
        identified = counts["identified_database"] + counts["identified_other"]
        screened = counts["screened_title_abstract"]
        sought = counts["sought_full_text"]
        if identified != counts["duplicate_removed"] + screened:
            raise ReviewValidationError("PRISMA identification does not reconcile: identified != duplicates removed + screened")
        if screened != counts["excluded_title_abstract"] + sought:
            raise ReviewValidationError("PRISMA screening does not reconcile: screened != title/abstract exclusions + full texts sought")
        if sought != counts["full_text_unavailable"] + counts["assessed_full_text"]:
            raise ReviewValidationError("PRISMA retrieval does not reconcile: sought != unavailable + assessed")
        if counts["assessed_full_text"] != counts["excluded_full_text"] + counts["included_report"]:
            raise ReviewValidationError("PRISMA eligibility does not reconcile: assessed != full-text exclusions + included reports")
    return {
        "status": "final_reconciled" if final else "provisional_derived",
        "counts": counts,
        "exclusions_by_code": dict(sorted(exclusion_codes.items())),
    }


def derive_evidence_matrix(bundle: dict[str, Any]) -> dict[str, Any]:
    """Derive a transparent family-level evidence matrix without adding judgments."""
    records = {row["record_id"]: row for row in bundle.get("records", [])}
    appraisals: dict[str, list[dict[str, Any]]] = defaultdict(list)
    extractions: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in bundle.get("quality_appraisals", []):
        appraisals[str(row.get("family_id"))].append(row)
    for row in bundle.get("extractions", []):
        extractions[str(row.get("family_id"))].append(row)
    rows = []
    for family in bundle.get("study_families", []):
        representative = records.get(family.get("representative_record_id"), {})
        fid = str(family.get("family_id"))
        rows.append({
            "family_id": fid,
            "status": family.get("status"),
            "representative_record_id": family.get("representative_record_id"),
            "report_count": len(family.get("member_record_ids", [])),
            "representative_evidence_stratum": representative.get("evidence_stratum"),
            "member_evidence_strata": sorted({
                str(records.get(rid, {}).get("evidence_stratum"))
                for rid in family.get("member_record_ids", [])
            }),
            "publication_status": representative.get("publication_status"),
            "full_text_access_status": representative.get("full_text_access_status"),
            "appraisal_ids": sorted(str(x.get("appraisal_id")) for x in appraisals[fid]),
            "evidence_bands": sorted({str(x.get("evidence_band")) for x in appraisals[fid]}),
            "verified_extraction_count": sum(
                x.get("verification_status") == "verified" for x in extractions[fid]
            ),
            "candidate_extraction_count": sum(
                x.get("verification_status") == "candidate" for x in extractions[fid]
            ),
        })
    return {"status": "derived_from_bundle", "rows": sorted(rows, key=lambda x: x["family_id"])}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a Gate 2 evidence-review bundle")
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--final", action="store_true", help="activate completion and PRISMA hard stops")
    parser.add_argument("--prisma", action="store_true", help="print derived PRISMA JSON")
    parser.add_argument("--evidence-matrix", action="store_true", help="print derived family-level evidence matrix JSON")
    args = parser.parse_args(argv)
    bundle = json.loads(args.bundle.read_text(encoding="utf-8"))
    validate_bundle(bundle, require_complete=args.final)
    if args.prisma or args.evidence_matrix:
        output: dict[str, Any] = {}
        if args.prisma:
            output["flow"] = derive_prisma(bundle, final=args.final)
        if args.evidence_matrix:
            output["evidence_matrix"] = derive_evidence_matrix(bundle)
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        print("valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
