"""Known-item recall and sampled-precision controls for development exports."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
import random
from typing import Any

from simulation.config import ConfigError, validate_config


class AppraisalError(ValueError):
    pass


SCHEMA_DIR = Path(__file__).with_name("schemas")
REGISTRY_SCHEMA_PATH = SCHEMA_DIR / "open_index_pilot_queries.schema.json"
RESULT_SCHEMA_PATH = SCHEMA_DIR / "query_appraisal_result.schema.json"


def normalize_doi(value: str) -> str:
    value = value.strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if value.startswith(prefix):
            value = value[len(prefix):]
    return value


def normalize_title(value: str) -> str:
    return " ".join(value.casefold().split())


def required_sample_size(population_size: int) -> int:
    """Return the prespecified Appendix 4.2 sample requirement."""
    if population_size < 0:
        raise AppraisalError("population size cannot be negative")
    if population_size <= 50:
        return population_size
    if population_size <= 1000:
        return 50
    return 100


def deterministic_sample_positions(population_size: int, source: str,
                                   family_id: str, query_version: str) -> tuple[list[int], str]:
    """Return the Appendix 4.2 boundary-plus-hash sample and seed digest."""
    required = required_sample_size(population_size)
    seed_text = f"{source}|{family_id}|{query_version}"
    seed_digest = hashlib.sha256(seed_text.encode("utf-8")).hexdigest()
    if required == population_size:
        return list(range(population_size)), seed_digest
    fixed = set(range(min(10, population_size)))
    fixed.update(range(max(0, population_size - 10), population_size))
    if population_size > 1000:
        middle_start = max(0, population_size // 2 - 5)
        fixed.update(range(middle_start, min(population_size, middle_start + 10)))
    available = [index for index in range(population_size) if index not in fixed]
    needed = required - len(fixed)
    if needed < 0 or needed > len(available):
        raise AppraisalError("deterministic sample cannot satisfy the required size")
    rng = random.Random(int(seed_digest, 16))
    fixed.update(rng.sample(available, needed))
    positions = sorted(fixed)
    if len(positions) != required:
        raise AppraisalError("deterministic sample size reconciliation failed")
    return positions, seed_digest


def _population_size(manifest: dict[str, Any], retrieved: int) -> tuple[int, str]:
    recorded_retrieved = manifest.get("records_retrieved")
    if recorded_retrieved is not None and recorded_retrieved != retrieved:
        raise AppraisalError("manifest records_retrieved does not match records.csv")
    reported = manifest.get("total_reported")
    if manifest.get("complete_pagination") is True:
        if isinstance(reported, int) and reported != retrieved:
            raise AppraisalError("complete export total_reported must equal retrieved records")
        return retrieved, "complete_export_retrieved_count"
    if isinstance(reported, int):
        if reported < retrieved:
            raise AppraisalError("incomplete export total_reported cannot be below retrieved records")
        return reported, "incomplete_export_reported_total_projection"
    return retrieved, "incomplete_export_retrieved_lower_bound"


def _wilson(successes: int, total: int) -> list[float] | None:
    if total == 0:
        return None
    z = 1.959963984540054
    proportion = successes / total
    denominator = 1 + z * z / total
    center = (proportion + z * z / (2 * total)) / denominator
    half = z * math.sqrt(proportion * (1 - proportion) / total + z * z / (4 * total * total)) / denominator
    return [center - half, center + half]


def appraise(export_dir: str | Path, registry: dict[str, Any], decisions: list[dict[str, str]]) -> dict[str, Any]:
    try:
        validate_config(registry, REGISTRY_SCHEMA_PATH)
    except ConfigError as exc:
        raise AppraisalError(f"query-appraisal registry is invalid: {exc}") from exc
    root = Path(export_dir)
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("status") != "development_pilot":
        raise AppraisalError("only development_pilot exports may be appraised")
    with (root / "records.csv").open(encoding="utf-8", newline="") as handle:
        records = list(csv.DictReader(handle))
    ids = {row.get("source_id", "") for row in records}
    dois = {normalize_doi(row.get("doi", "")) for row in records if row.get("doi")}
    titles = {normalize_title(row.get("title", "")) for row in records if row.get("title")}
    source = str(manifest.get("source", "")).casefold().replace(" ", "_")
    control_v3 = registry.get("sentinel_control_version") == "family_scoped_v0.3"
    family_id = None
    if control_v3:
        matches = [row for row in registry.get("queries", [])
                   if row.get("source") == source and row.get("query_id") == manifest.get("query_id")]
        if len(matches) != 1:
            raise AppraisalError("v0.3 appraisal requires exactly one source/query registry row")
        query_row = matches[0]
        family_id = query_row.get("family_id")
        if not family_id or query_row.get("query") != manifest.get("query"):
            raise AppraisalError("manifest query does not match its v0.3 family-scoped registry row")
        sentinels = [row for row in registry.get("sentinels", [])
                     if row.get("family_id") == family_id and source in row.get("testable_sources", [])]
    else:
        sentinels = registry.get("sentinels", [])
    checks = []
    for sentinel in sentinels:
        doi_present = bool(sentinel.get("doi")) and normalize_doi(sentinel["doi"]) in dois
        title_present = bool(sentinel.get("title")) and normalize_title(sentinel["title"]) in titles
        present = doi_present or title_present
        role = sentinel["role"]
        expected_present = role in {"positive", "scope_positive", "neutral_disconfirming"}
        check = {"sentinel_id": sentinel["sentinel_id"], "doi": sentinel["doi"],
                 "role": role, "present": present,
                 "pass": present if expected_present else not present}
        if control_v3:
            check["match_basis"] = "doi" if doi_present else "title" if title_present else "none"
        checks.append(check)
    rule = registry["sampled_precision_rule"]
    allowed = set(rule["allowed_decisions"])
    seen: set[str] = set()
    for row in decisions:
        if set(rule["required_fields"]) - set(row):
            raise AppraisalError("sample decision lacks required fields")
        if row["source_id"] not in ids or row["source_id"] in seen:
            raise AppraisalError("sample source_id is absent from export or duplicated")
        if row["decision"] not in allowed or not row["reason"].strip():
            raise AppraisalError("sample decision or reason is invalid")
        seen.add(row["source_id"])
    relevant = sum(row["decision"] == "likely_relevant" for row in decisions)
    uncertain = sum(row["decision"] == "uncertain" for row in decisions)
    decided = sum(row["decision"] != "uncertain" for row in decisions)
    diagnostic_minimum = int(rule["development_diagnostic_minimum_sample"])
    expected_bands = [
        {"population_min": 0, "population_max": 50, "required_sample": "all"},
        {"population_min": 51, "population_max": 1000, "required_sample": 50},
        {"population_min": 1001, "population_max": None, "required_sample": 100},
    ]
    if rule.get("freeze_sample_bands") != expected_bands:
        raise AppraisalError("freeze_sample_bands must exactly match Appendix 4.2")
    population, population_basis = _population_size(manifest, len(records))
    freeze_minimum = required_sample_size(population)
    burden_numerator = relevant + uncertain
    burden_proportion = burden_numerator / len(decisions) if decisions else None
    bands = rule.get("acceptance_bands")
    if not isinstance(bands, dict):
        raise AppraisalError("sampled_precision_rule.acceptance_bands is required")
    operational_minimum = bands.get("operational_minimum_relevant_plus_uncertain")
    conditional_minimum = bands.get("conditional_minimum_relevant_plus_uncertain")
    if not isinstance(operational_minimum, (int, float)) or not isinstance(conditional_minimum, (int, float)):
        raise AppraisalError("acceptance bands require numeric operational and conditional minima")
    if not 0 <= conditional_minimum <= operational_minimum <= 1:
        raise AppraisalError("acceptance bands must satisfy 0 <= conditional <= operational <= 1")
    if burden_proportion is None:
        burden_band = "not_estimable"
    elif burden_proportion >= operational_minimum:
        burden_band = "operational_pass"
    elif burden_proportion >= conditional_minimum:
        burden_band = "conditional_review_required"
    else:
        burden_band = "revise_or_split"
    positive_roles = {"positive", "scope_positive"}
    positive_checks = [row for row in checks if row["role"] in positive_roles]
    neutral_checks = [row for row in checks if row["role"] == "neutral_disconfirming"]
    class_complete = bool(positive_checks) and (bool(neutral_checks) if control_v3 else True)
    required_recall_checks = positive_checks + neutral_checks
    # Negative-boundary retrieval is a precision warning handled through the
    # sampled burden appraisal; it is not a known-item recall failure.
    sentinel_pass = class_complete and all(row["pass"] for row in required_recall_checks)
    # A complete population smaller than the diagnostic target is appraised in
    # full; it must not fail merely because more records do not exist.
    diagnostic_required = min(diagnostic_minimum, population)
    diagnostic_pass = sentinel_pass and len(decisions) >= diagnostic_required
    freeze_ready = (
        sentinel_pass
        and manifest.get("complete_pagination") is True
        and len(decisions) >= freeze_minimum
        and burden_band == "operational_pass"
    )
    result = {
        "status": "development_query_appraisal",
        "interpretation_boundary": "Known-item recall and sampled relevance appraisal only; not screening, eligibility, or PRISMA evidence.",
        "source": manifest.get("source"), "query_id": manifest.get("query_id"),
        "complete_pagination": manifest.get("complete_pagination"),
        "sentinel_checks": checks,
        "positive_sentinel_recall_pass": bool(positive_checks) and all(row["pass"] for row in positive_checks),
        "negative_boundary_pass": all(row["pass"] for row in checks if row["role"] == "negative_boundary"),
        "population_size_for_sample": population, "population_size_basis": population_basis,
        "required_sample_size_for_freeze": freeze_minimum,
        "development_diagnostic_minimum": diagnostic_minimum,
        "development_diagnostic_required_for_population": diagnostic_required,
        "sample_size": len(decisions), "sample_minimum_met": len(decisions) >= freeze_minimum,
        "sample_likely_relevant": relevant, "sample_decided": decided,
        "sample_precision_point_estimate": relevant / decided if decided else None,
        "sample_uncertain": uncertain,
        "relevant_plus_uncertain_count": burden_numerator,
        "relevant_plus_uncertain_proportion": burden_proportion,
        "relevant_plus_uncertain_wilson_95_interval": _wilson(burden_numerator, len(decisions)),
        "burden_acceptance_band": burden_band,
        "development_diagnostic_pass": diagnostic_pass,
        "freeze_ready": freeze_ready,
        "query_appraisal_pass": freeze_ready,
        "query_appraisal_pass_deprecated_alias_for": "freeze_ready",
    }
    if control_v3:
        result.update({
            "family_id": family_id,
            "sentinel_class_complete": class_complete,
            "neutral_disconfirming_recall_pass": bool(neutral_checks) and all(
                row["pass"] for row in neutral_checks
            ),
        })
    try:
        validate_config(result, RESULT_SCHEMA_PATH)
    except ConfigError as exc:
        raise AppraisalError(f"derived query-appraisal result is invalid: {exc}") from exc
    return result
