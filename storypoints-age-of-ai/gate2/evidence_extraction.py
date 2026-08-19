"""Validate and combine D13 structured evidence extractions."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import shutil
import tempfile
from typing import Any

from gate2.fulltext_screening import OUTPUT as D11_OUTPUT, SYSTEMATIC, FullTextScreeningError, sha256


OUTPUT = SYSTEMATIC / "d13"
D11_LEDGER = SYSTEMATIC / "d11/screening/final/fulltext_eligibility_decisions.jsonl"
D12_LEDGER = SYSTEMATIC / "d12/final/quality_appraisals.jsonl"
VERSION = "d13-evidence-extraction-controller/1.0.0"
CREATED_AT = "2026-08-18T00:30:00Z"
LIFECYCLE = {
    "requirements", "context_prompt", "architecture_design", "implementation_refinement",
    "integration", "code_review", "security_compliance", "testing", "release_operations",
    "manual_qa_uat", "coordination_switching",
}
CONSTRUCTS = {"PDD", "RHTD", "SAE", "ERS", "ARC", "RCP", "CQD", "VDC"}
NOVELTY_DIMENSIONS = {
    "precommitment_predictors", "multirole_lifecycle", "touch_queue_separation",
    "capacity_readiness_dependencies", "verified_completion_forecast",
}
DATA_NATURE = {"observed", "self_reported", "modeled", "conceptual", "mixed"}
DIRECTIONS = {"positive", "negative", "mixed", "null", "not_applicable", None}


class EvidenceExtractionError(FullTextScreeningError):
    pass


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _page(locator: Any) -> int | None:
    if not isinstance(locator, str):
        return None
    match = re.search(r"(?:\bpage(?:s)?|\bp\.)\s+(\d+)", locator, flags=re.I)
    return int(match.group(1)) if match else None


def _population(part: str) -> dict[str, dict[str, Any]]:
    if part not in {"a", "b"}:
        raise EvidenceExtractionError("D13 part must be a or b")
    included = sorted(
        (row for row in _read(D11_LEDGER) if row["final_status"] == "included_full_text"),
        key=lambda row: row["family_id"],
    )
    selected = included[:285] if part == "a" else included[285:]
    return {row["family_id"]: row for row in selected}


def _source_packet() -> dict[str, dict[str, Any]]:
    manifest = json.loads((D11_OUTPUT / "d11_packet_manifest.json").read_text(encoding="utf-8"))
    result = {}
    for shard in manifest["shards"]:
        for row in _read(D11_OUTPUT / shard["path"]):
            result[row["family_id"]] = row
    return result


def validate_part(path: Path, part: str) -> dict[str, Any]:
    expected = _population(part); sources = _source_packet()
    appraisals = {row["family_id"]: row for row in _read(D12_LEDGER)}
    rows = _read(path); seen = set(); findings = 0; quantitative = 0
    construct_counts: Counter[str] = Counter(); novelty_counts: Counter[str] = Counter()
    for row in rows:
        family_id = row.get("family_id")
        if family_id not in expected or family_id in seen:
            raise EvidenceExtractionError(f"unknown/duplicate D13 family: {family_id}")
        seen.add(family_id); source = sources[family_id]; appraisal = appraisals[family_id]
        if row.get("record_id") != expected[family_id]["record_id"]:
            raise EvidenceExtractionError(f"D13 record mismatch: {family_id}")
        if row.get("source_text_sha256") != source["extracted_text_sha256"]:
            raise EvidenceExtractionError(f"D13 source checksum mismatch: {family_id}")
        if row.get("evidence_band") != appraisal["evidence_band"] or row.get("appraisal_form") != appraisal["appraisal_form"]:
            raise EvidenceExtractionError(f"D13 appraisal binding mismatch: {family_id}")
        if not row.get("extractor_agent_id") or not row.get("review_context_id"):
            raise EvidenceExtractionError(f"D13 extractor provenance missing: {family_id}")
        if not isinstance(row.get("bibliographic_status"), dict) or not isinstance(row.get("context_method"), dict):
            raise EvidenceExtractionError(f"D13 bibliography/context missing: {family_id}")
        lifecycle = row.get("lifecycle_stages")
        if not isinstance(lifecycle, dict) or set(lifecycle) != LIFECYCLE:
            raise EvidenceExtractionError(f"D13 lifecycle keys invalid: {family_id}")
        for stage, value in lifecycle.items():
            if not isinstance(value, dict) or not isinstance(value.get("present"), bool):
                raise EvidenceExtractionError(f"D13 lifecycle value invalid: {family_id}/{stage}")
            locator = value.get("source_locator")
            if value["present"] and (_page(locator) is None or _page(locator) > source["page_count"]):
                raise EvidenceExtractionError(f"D13 lifecycle locator invalid: {family_id}/{stage}")
        constructs = row.get("vdcm_constructs")
        if not isinstance(constructs, dict) or set(constructs) != CONSTRUCTS:
            raise EvidenceExtractionError(f"D13 construct keys invalid: {family_id}")
        for name, value in constructs.items():
            if value.get("status") not in {"present", "absent", "unclear"} or not value.get("rationale"):
                raise EvidenceExtractionError(f"D13 construct value invalid: {family_id}/{name}")
            if value["status"] == "present" and (_page(value.get("source_locator")) is None or _page(value.get("source_locator")) > source["page_count"]):
                raise EvidenceExtractionError(f"D13 construct locator invalid: {family_id}/{name}")
            if value["status"] == "present": construct_counts[name] += 1
        if not isinstance(row.get("emergent_constructs"), list):
            raise EvidenceExtractionError(f"D13 emergent constructs invalid: {family_id}")
        study_findings = row.get("measures_findings")
        if not isinstance(study_findings, list) or not study_findings:
            raise EvidenceExtractionError(f"D13 lacks findings: {family_id}")
        finding_ids = set()
        for finding in study_findings:
            fid = finding.get("finding_id")
            if not fid or fid in finding_ids or not finding.get("field_name") or not finding.get("value"):
                raise EvidenceExtractionError(f"D13 finding identity/value invalid: {family_id}")
            finding_ids.add(fid)
            if finding.get("data_nature") not in DATA_NATURE or finding.get("direction") not in DIRECTIONS:
                raise EvidenceExtractionError(f"D13 finding enums invalid: {family_id}/{fid}")
            page = _page(finding.get("source_locator"))
            if page is None or page > source["page_count"]:
                raise EvidenceExtractionError(f"D13 finding locator invalid: {family_id}/{fid}")
            if not isinstance(finding.get("quantitative"), bool):
                raise EvidenceExtractionError(f"D13 quantitative flag invalid: {family_id}/{fid}")
            if finding["quantitative"] and finding.get("reported_estimate") in {None, ""}:
                raise EvidenceExtractionError(f"D13 quantitative estimate absent: {family_id}/{fid}")
            quantitative += int(finding["quantitative"]); findings += 1
        novelty = row.get("novelty_assessment")
        dimensions = novelty.get("dimensions") if isinstance(novelty, dict) else None
        if dimensions is None and isinstance(novelty, dict):
            dimensions = {key: novelty.get(key) for key in NOVELTY_DIMENSIONS}
        if not isinstance(novelty, dict) or not isinstance(dimensions, dict) or set(dimensions) != NOVELTY_DIMENSIONS:
            raise EvidenceExtractionError(f"D13 novelty dimensions invalid: {family_id}")
        for name, value in dimensions.items():
            if value.get("status") not in {"met", "partial", "not_met", "unclear"} or not value.get("rationale"):
                raise EvidenceExtractionError(f"D13 novelty value invalid: {family_id}/{name}")
            if value["status"] in {"met", "partial"} and (_page(value.get("source_locator")) is None or _page(value.get("source_locator")) > source["page_count"]):
                raise EvidenceExtractionError(f"D13 novelty locator invalid: {family_id}/{name}")
            novelty_counts[f"{name}:{value['status']}"] += 1
        if novelty.get("same_planning_use") not in {"yes", "no", "unclear"}:
            raise EvidenceExtractionError(f"D13 same-planning-use invalid: {family_id}")
        if not isinstance(novelty.get("comparator_story_points"), bool) or not isinstance(novelty.get("comparator_hie"), bool):
            raise EvidenceExtractionError(f"D13 comparator flags invalid: {family_id}")
        if novelty.get("novelty_risk") not in {"low", "moderate", "high", "critical"} or not novelty.get("validation_type"):
            raise EvidenceExtractionError(f"D13 novelty summary invalid: {family_id}")
        if not row.get("reviewer_notes") or not row.get("security_attestation"):
            raise EvidenceExtractionError(f"D13 notes/security provenance missing: {family_id}")
    if seen != set(expected):
        raise EvidenceExtractionError(f"D13 part {part} incomplete: missing {len(set(expected)-seen)}")
    sidecar = path.with_name(path.name + ".sha256")
    if sidecar.exists() and sidecar.read_text(encoding="utf-8").split()[0] != sha256(path):
        raise EvidenceExtractionError(f"D13 part {part} sidecar mismatch")
    return {
        "status": "valid_complete_d13_extraction_part", "part": part,
        "family_count": len(rows), "finding_count": findings, "quantitative_finding_count": quantitative,
        "present_construct_counts": dict(sorted(construct_counts.items())),
        "novelty_dimension_counts": dict(sorted(novelty_counts.items())), "sha256": sha256(path),
    }


def combine(output_dir: Path = OUTPUT / "primary") -> dict[str, Any]:
    if output_dir.exists():
        raise EvidenceExtractionError(f"immutable D13 primary exists: {output_dir}")
    a_path, b_path = OUTPUT / "extraction_part_a.jsonl", OUTPUT / "extraction_part_b.jsonl"
    va, vb = validate_part(a_path, "a"), validate_part(b_path, "b")
    rows = sorted(_read(a_path) + _read(b_path), key=lambda row: row["family_id"])
    for row in rows:
        novelty = row["novelty_assessment"]
        if "dimensions" not in novelty:
            novelty["dimensions"] = {key: novelty.pop(key) for key in sorted(NOVELTY_DIMENSIONS)}
        for finding in row["measures_findings"]:
            if finding.get("direction") is None:
                finding["direction"] = "null"
    if len(rows) != 570 or len({row["family_id"] for row in rows}) != 570:
        raise EvidenceExtractionError("D13 combined population invalid")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="d13-primary-", dir=str(output_dir.parent)))
    try:
        ledger = staging / "evidence_extractions.jsonl"
        ledger.write_text("".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
        result = {
            "status": "d13_primary_extraction_complete_pending_verification",
            "protocol_version": "1.3", "pipeline_version": VERSION, "created_at_utc": CREATED_AT,
            "part_a_validation": va, "part_b_validation": vb, "family_count": 570,
            "finding_count": sum(len(row["measures_findings"]) for row in rows),
            "quantitative_finding_count": sum(sum(bool(x["quantitative"]) for x in row["measures_findings"]) for row in rows),
            "ledger_sha256": sha256(ledger),
            "verification_requirement": "Every quantitative finding and every novelty dimension assessed as met/partial/unclear requires distinct source-grounded verification before D13 closes.",
            "interpretation_boundary": "Extraction does not establish causality, cognitive-workload validity, organizational generalizability, or novelty.",
        }
        path = staging / "d13_primary_manifest.json"; path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (staging / "d13_primary_manifest.json.sha256").write_text(f"{sha256(path)}  d13_primary_manifest.json\n", encoding="utf-8")
        staging.rename(output_dir); return result
    except Exception:
        shutil.rmtree(staging, ignore_errors=True); raise


def verify_primary(output_dir: Path = OUTPUT / "primary") -> dict[str, Any]:
    path = output_dir / "d13_primary_manifest.json"; result = json.loads(path.read_text(encoding="utf-8"))
    if result["part_a_validation"] != validate_part(OUTPUT / "extraction_part_a.jsonl", "a"):
        raise EvidenceExtractionError("D13 primary no longer binds part A")
    if result["part_b_validation"] != validate_part(OUTPUT / "extraction_part_b.jsonl", "b"):
        raise EvidenceExtractionError("D13 primary no longer binds part B")
    ledger = output_dir / "evidence_extractions.jsonl"
    if sha256(ledger) != result["ledger_sha256"] or len(_read(ledger)) != 570:
        raise EvidenceExtractionError("D13 primary ledger mismatch")
    if (output_dir / "d13_primary_manifest.json.sha256").read_text().split()[0] != sha256(path):
        raise EvidenceExtractionError("D13 primary sidecar mismatch")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("validate-part", "combine", "verify-primary")); parser.add_argument("--part", choices=("a", "b")); parser.add_argument("--path", type=Path); args = parser.parse_args()
    if args.command == "validate-part":
        if not args.part or not args.path: raise EvidenceExtractionError("validate-part requires --part and --path")
        result = validate_part(args.path, args.part)
    elif args.command == "combine": result = combine()
    else: result = verify_primary()
    print(json.dumps(result, sort_keys=True)); return 0


if __name__ == "__main__": raise SystemExit(main())
