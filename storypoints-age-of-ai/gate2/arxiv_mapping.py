"""Fail-closed cross-family mapping for an immutable arXiv development export."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from gate2.query_appraisal import _wilson, required_sample_size


class ArxivMappingError(ValueError):
    pass


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_mapping(export_dir: str | Path, registry_path: str | Path) -> dict[str, Any]:
    root = Path(export_dir)
    registry = json.loads(Path(registry_path).read_text(encoding="utf-8"))
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    family_id = registry.get("family_id")
    if registry.get("status") != "development_pilot" or not isinstance(family_id, str) or not family_id:
        raise ArxivMappingError("mapping registry must declare a developmental family")
    if manifest.get("status") != "development_pilot" or manifest.get("complete_pagination") is not True:
        raise ArxivMappingError("mapped export must be complete and developmental")
    if manifest.get("query_id") != registry.get("source_query_id"):
        raise ArxivMappingError("source query ID does not match mapping registry")
    if manifest.get("query") != registry.get("query"):
        raise ArxivMappingError("source query text does not match mapping registry")
    csv_path = root / manifest["records_csv"]["file"]
    if _sha(csv_path) != manifest["records_csv"]["sha256"]:
        raise ArxivMappingError("records CSV checksum mismatch")
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8", newline="")))
    if len(rows) != manifest.get("records_retrieved"):
        raise ArxivMappingError("record count does not reconcile")
    ids = {re.sub(r"v\d+$", "", row["arxiv_id_version"]) for row in rows}
    checks = []
    for sentinel in registry.get("sentinels", []):
        present = sentinel.get("arxiv_id") in ids
        checks.append({
            "sentinel_id": sentinel.get("sentinel_id"),
            "role": sentinel.get("role"),
            "arxiv_id": sentinel.get("arxiv_id"),
            "present": present,
            "pass": present,
        })
    roles = {row["role"] for row in checks}
    class_complete = {"scope_positive", "neutral_disconfirming"}.issubset(roles)
    sentinel_pass = class_complete and bool(checks) and all(row["pass"] for row in checks)
    return {
        "status": "development_arxiv_family_mapping",
        "source_query_id": manifest["query_id"],
        "mapped_family_id": family_id,
        "records_reconciled": len(rows),
        "complete_pagination": True,
        "sentinel_class_complete": class_complete,
        "sentinel_recall_pass": sentinel_pass,
        "sentinel_checks": checks,
        "precision_appraisal_pending": True,
        "freeze_ready": False,
        "interpretation_boundary": "Cross-family mapping and known-item recall only; not screening, eligibility, PRISMA, or query freeze.",
    }


def appraise_mapping(export_dir: str | Path, registry_path: str | Path,
                      decisions: list[dict[str, str]]) -> dict[str, Any]:
    mapping = verify_mapping(export_dir, registry_path)
    root = Path(export_dir)
    registry = json.loads(Path(registry_path).read_text(encoding="utf-8"))
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    rows = list(csv.DictReader((root / manifest["records_csv"]["file"]).open(
        encoding="utf-8", newline=""
    )))
    ids = {row["arxiv_id_version"] for row in rows}
    rule = registry["sampled_precision_rule"]
    allowed = set(rule["allowed_decisions"])
    seen: set[str] = set()
    for decision in decisions:
        if set(decision) < {"source_id", "decision", "reason"}:
            raise ArxivMappingError("precision decision lacks required fields")
        if decision["source_id"] not in ids or decision["source_id"] in seen:
            raise ArxivMappingError("precision source ID is absent or duplicated")
        if decision["decision"] not in allowed or not decision["reason"].strip():
            raise ArxivMappingError("precision decision or reason is invalid")
        seen.add(decision["source_id"])
    relevant = sum(row["decision"] == "likely_relevant" for row in decisions)
    uncertain = sum(row["decision"] == "uncertain" for row in decisions)
    burden_count = relevant + uncertain
    burden = burden_count / len(decisions) if decisions else None
    freeze_minimum = required_sample_size(len(rows))
    operational = rule["acceptance_bands"]["operational_minimum_relevant_plus_uncertain"]
    conditional = rule["acceptance_bands"]["conditional_minimum_relevant_plus_uncertain"]
    if burden is None:
        band = "not_estimable"
    elif burden >= operational:
        band = "operational_pass"
    elif burden >= conditional:
        band = "conditional_review_required"
    else:
        band = "revise_or_split"
    freeze_ready = (
        mapping["sentinel_recall_pass"]
        and len(decisions) >= freeze_minimum
        and band == "operational_pass"
    )
    return {
        **mapping,
        "status": "development_query_appraisal",
        "precision_appraisal_pending": False,
        "population_size_for_sample": len(rows),
        "population_size_basis": "complete_export_retrieved_count",
        "required_sample_size_for_freeze": freeze_minimum,
        "sample_size": len(decisions),
        "sample_minimum_met": len(decisions) >= freeze_minimum,
        "sample_likely_relevant": relevant,
        "sample_uncertain": uncertain,
        "sample_likely_irrelevant": len(decisions) - relevant - uncertain,
        "relevant_plus_uncertain_count": burden_count,
        "relevant_plus_uncertain_proportion": burden,
        "relevant_plus_uncertain_wilson_95_interval": _wilson(burden_count, len(decisions)),
        "burden_acceptance_band": band,
        "freeze_ready": freeze_ready,
        "query_appraisal_pass": freeze_ready,
        "interpretation_boundary": "Mapped arXiv query precision and known-item recall only; not screening, eligibility, inclusion, or PRISMA evidence.",
    }
