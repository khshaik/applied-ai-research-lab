"""Fail-closed controls for Gate 2 search planning and execution logs.

This module does not search any source.  It renders canonical Boolean families
from a term registry and validates that access failures, pilots, systematic
runs, exports, and final claims cannot be conflated.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


class SearchControlError(ValueError):
    """Raised when a search-control record is incomplete or inconsistent."""


RUN_STATUSES = {
    "translation_draft",
    "syntax_validated",
    "pilot_excluded",
    "systematic_executed",
    "export_verified",
    "refresh_executed",
    "failed_attempt",
}
ACCESS_STATUSES = {
    "not_assessed",
    "accessible",
    "blocked_authentication",
    "blocked_rate_limit",
    "blocked_technical",
}
BLOCKED_ACCESS = ACCESS_STATUSES - {"not_assessed", "accessible"}
OUTCOME_STATUSES = {"systematic_executed", "export_verified", "refresh_executed"}
CHECKSUM_STATUSES = {"export_verified", "refresh_executed"}


def load_control(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def render_families(control: dict[str, Any]) -> dict[str, str]:
    """Expand every ``{BLOCK}`` reference; reject unresolved placeholders."""
    blocks = control.get("term_blocks", {})
    rendered: dict[str, str] = {}
    for family in control.get("families", []):
        query = family.get("canonical_expression", "")
        for block_id, terms in blocks.items():
            literal = " OR ".join(terms)
            query = query.replace("{" + block_id + "}", literal)
        unresolved = re.findall(r"\{[A-Z0-9_]+\}|\b[A-Z]_TERMS\b", query)
        if unresolved:
            raise SearchControlError(
                f"family {family.get('family_id')} has unresolved blocks: {unresolved}"
            )
        rendered[family["family_id"]] = query
    return rendered


def validate_search_control(control: dict[str, Any], *, require_final: bool = False) -> None:
    errors: list[str] = []
    required_families = set(control.get("required_family_ids", []))
    families = control.get("families", [])
    family_ids = [row.get("family_id") for row in families]
    if len(family_ids) != len(set(family_ids)):
        errors.append("family_id values must be unique")
    if set(family_ids) != required_families:
        errors.append("families must exactly cover required_family_ids")
    try:
        rendered = render_families(control)
    except (KeyError, TypeError, SearchControlError) as exc:
        errors.append(str(exc))
        rendered = {}
    if any(not query.strip() for query in rendered.values()):
        errors.append("every family must render to a non-empty canonical query")

    mandatory_sources = set(control.get("mandatory_sources", []))
    access_rows = control.get("source_access", [])
    access_by_source: dict[str, dict[str, Any]] = {}
    for row in access_rows:
        source = row.get("source")
        if source in access_by_source:
            errors.append(f"duplicate source_access row for {source}")
        access_by_source[source] = row
        status = row.get("status")
        if status not in ACCESS_STATUSES:
            errors.append(f"source {source} has invalid access status")
        if status in BLOCKED_ACCESS:
            has_attempt = bool(row.get("attempted_at_utc"))
            has_assessment = bool(row.get("assessed_on") and row.get("assessment_basis"))
            if (not has_attempt and not has_assessment) or not row.get("reason") or not row.get("next_action"):
                errors.append(
                    f"blocked source {source} requires attempt time or dated assessment basis, reason, and next action"
                )
            if row.get("fallback_role") not in {"none", "discovery_only", "non_equivalent_supplement"}:
                errors.append(f"blocked source {source} requires an explicit non-substitution fallback role")
    if set(access_by_source) != mandatory_sources:
        errors.append("source_access must exactly cover mandatory_sources")

    executable_sources = set(control.get("executable_sources", []))
    if not executable_sources or not executable_sources.issubset(mandatory_sources):
        errors.append("executable_sources must be a non-empty subset of mandatory_sources")
    verification_sources = set(control.get("verification_sources", []))
    if not verification_sources.issubset(mandatory_sources):
        errors.append("verification_sources must be a subset of mandatory_sources")
    if executable_sources & verification_sources:
        errors.append("discovery and verification source roles must be disjoint")

    pair_rows = control.get("required_source_family_pairs", [])
    required_pairs: set[tuple[str, str]] = set()
    for row in pair_rows:
        pair = (row.get("source"), row.get("family_id"))
        if pair in required_pairs:
            errors.append(f"duplicate required source-family pair: {pair}")
        required_pairs.add(pair)
        if pair[0] not in executable_sources:
            errors.append(f"required pair source is not an executable discovery source: {pair}")
        if pair[1] not in required_families:
            errors.append(f"required pair references an unknown family: {pair}")
    if not required_pairs:
        errors.append("required_source_family_pairs must be non-empty")
    paired_families = {family for _, family in required_pairs}
    if paired_families != required_families:
        errors.append("required source-family pairs must cover every required family")
    paired_sources = {source for source, _ in required_pairs}
    if paired_sources != executable_sources:
        errors.append("required source-family pairs must use every executable discovery source")

    seen_runs: set[str] = set()
    coverage: set[tuple[str, str]] = set()
    for run in control.get("query_runs", []):
        run_id = run.get("run_id")
        if not run_id or run_id in seen_runs:
            errors.append("query run IDs must be non-empty and unique")
        seen_runs.add(run_id)
        source, family, status = run.get("source"), run.get("family_id"), run.get("status")
        if source not in mandatory_sources or family not in required_families:
            errors.append(f"run {run_id} references an unknown source or family")
        if status not in RUN_STATUSES:
            errors.append(f"run {run_id} has invalid status")
            continue
        if status != "translation_draft" and not run.get("exact_accepted_query"):
            errors.append(f"run {run_id} requires the exact platform-accepted query")
        if status in {"pilot_excluded", "failed_attempt"} and run.get("prisma_eligible") is not False:
            errors.append(f"run {run_id} must be explicitly excluded from PRISMA counts")
        if status in OUTCOME_STATUSES:
            if not run.get("executed_at_utc") or not isinstance(run.get("results_returned"), int):
                errors.append(f"outcome-bearing run {run_id} requires time and integer result count")
        if status in CHECKSUM_STATUSES and run.get("prisma_eligible") is True:
            coverage.add((source, family))
        if status in CHECKSUM_STATUSES and not run.get("export_sha256"):
            errors.append(f"verified run {run_id} requires an export SHA-256")

    if require_final:
        if control.get("protocol_status") != "frozen_approved":
            errors.append("final validation requires protocol_status=frozen_approved")
        for source, row in access_by_source.items():
            if row.get("status") == "not_assessed":
                errors.append(f"final validation cannot leave source {source} unassessed")
            if source in executable_sources and row.get("status") != "accessible":
                errors.append(f"final validation requires executable source {source} to be accessible")
        for source, family in required_pairs:
            if (source, family) not in coverage:
                errors.append(
                    f"declared source-family pair lacks a verified PRISMA-eligible export: {source}/{family}"
                )
        if not control.get("refresh_search", {}).get("completed_within_seven_days_of_submission"):
            errors.append("final validation requires the documented seven-day refresh")
        if any(row.get("status") in BLOCKED_ACCESS for row in access_rows):
            if control.get("coverage_claim") != "access_constrained":
                errors.append("blocked mandatory sources prohibit a comprehensive/full-access claim")

    if errors:
        raise SearchControlError("search control invalid:\n" + "\n".join(errors))
