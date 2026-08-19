import copy
from pathlib import Path

import pytest

from gate2.search_control import SearchControlError, load_control, render_families, validate_search_control


TEMPLATE = Path("gate2/search_control_template.json")


def test_draft_template_has_literal_coverage_without_execution_claims():
    control = load_control(TEMPLATE)
    validate_search_control(control)
    rendered = render_families(control)
    assert set(rendered) == set(control["required_family_ids"])
    assert all("_TERMS" not in query and "{" not in query for query in rendered.values())
    assert control["query_runs"] == []


def test_blocked_access_requires_auditable_non_substitution_record():
    control = load_control(TEMPLATE)
    control["source_access"][0]["status"] = "blocked_authentication"
    with pytest.raises(SearchControlError, match="requires attempt time"):
        validate_search_control(control)


def test_dated_user_confirmed_access_assessment_does_not_require_fake_attempt_time():
    control = load_control(TEMPLATE)
    scopus = next(row for row in control["source_access"] if row["source"] == "Scopus")
    assert "attempted_at_utc" not in scopus
    validate_search_control(control)


def test_open_route_declares_three_discovery_sources_and_crossref_verification():
    control = load_control(TEMPLATE)
    assert set(control["executable_sources"]) == {
        "OpenAlex", "Semantic Scholar Academic Graph", "arXiv"
    }
    assert control["verification_sources"] == ["Crossref REST API"]
    assert all(
        row["source"] != "Crossref REST API"
        for row in control["required_source_family_pairs"]
    )
    assert control["coverage_claim"] == "access_constrained"


def test_approved_non_cartesian_pair_matrix_is_exact():
    control = load_control(TEMPLATE)
    pairs = {
        (row["family_id"], row["source"])
        for row in control["required_source_family_pairs"]
    }
    assert len(pairs) == 21
    assert ("S1", "Semantic Scholar Academic Graph") in pairs
    assert ("S1", "OpenAlex") not in pairs
    assert ("S2", "OpenAlex") in pairs
    assert ("S2", "arXiv") not in pairs
    validate_search_control(control)


def test_failed_attempt_cannot_enter_prisma_counts():
    control = load_control(TEMPLATE)
    control["query_runs"].append({
        "run_id": "attempt-1", "source": "arXiv", "family_id": "S1",
        "status": "failed_attempt", "exact_accepted_query": "all:test",
        "prisma_eligible": True,
    })
    with pytest.raises(SearchControlError, match="excluded from PRISMA"):
        validate_search_control(control)


def test_final_fails_when_access_and_family_coverage_are_incomplete():
    control = load_control(TEMPLATE)
    control["protocol_status"] = "frozen_approved"
    control["refresh_search"]["completed_within_seven_days_of_submission"] = True
    with pytest.raises(SearchControlError, match="cannot leave source"):
        validate_search_control(control, require_final=True)


def test_verified_export_requires_checksum():
    control = load_control(TEMPLATE)
    control["query_runs"].append({
        "run_id": "run-1", "source": "arXiv", "family_id": "S3",
        "status": "export_verified", "exact_accepted_query": "all:test",
        "executed_at_utc": "2026-08-14T00:00:00Z", "results_returned": 1,
        "prisma_eligible": True,
    })
    with pytest.raises(SearchControlError, match="requires an export SHA-256"):
        validate_search_control(control)
