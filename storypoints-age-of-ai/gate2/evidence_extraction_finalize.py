"""Validate distinct D13 verification and publish the final evidence matrix."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import tempfile
from typing import Any

from gate2.evidence_extraction import OUTPUT, EvidenceExtractionError, validate_part, verify_primary
from gate2.fulltext_screening import sha256


FINAL = OUTPUT / "final"
VERSION = "d13-evidence-extraction-finalizer/1.0.0"
CREATED_AT = "2026-08-18T01:00:00Z"


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _dimensions(row: dict[str, Any]) -> dict[str, Any]:
    novelty = row["novelty_assessment"]
    return novelty.get("dimensions", {key: novelty[key] for key in (
        "precommitment_predictors", "multirole_lifecycle", "touch_queue_separation",
        "capacity_readiness_dependencies", "verified_completion_forecast",
    )})


def validate_verified(path: Path, part: str) -> dict[str, Any]:
    base = validate_part(path, part); primary = verify_primary()
    rows = _read(path); corrections: Counter[str] = Counter()
    for row in rows:
        if not row.get("verifier_agent_id") or row.get("verifier_agent_id") == row.get("extractor_agent_id"):
            raise EvidenceExtractionError(f"D13 verifier is not distinct: {row.get('family_id')}")
        if not row.get("verification_context_id"):
            raise EvidenceExtractionError(f"D13 verification context missing: {row.get('family_id')}")
        if row.get("original_extraction_sha256") != primary["ledger_sha256"]:
            raise EvidenceExtractionError(f"D13 verification input hash mismatch: {row.get('family_id')}")
        summary = row.get("verification_summary")
        required = {"quantitative_verified", "quantitative_corrected", "quantitative_rejected", "novelty_corrected", "other_corrections"}
        if not isinstance(summary, dict) or set(summary) != required:
            raise EvidenceExtractionError(f"D13 verification summary invalid: {row.get('family_id')}")
        for key, value in summary.items():
            if not isinstance(value, int) or value < 0:
                raise EvidenceExtractionError(f"D13 verification counter invalid: {row.get('family_id')}/{key}")
            corrections[key] += value
        if part == "a" and path.name == "verified_part_a_v2.jsonl":
            completeness = row.get("completeness_review")
            required_completeness = {
                "baseline_finding_count", "retained_baseline_findings",
                "new_findings_added", "quantitative_new_findings_added",
            }
            if not isinstance(completeness, dict) or set(completeness) != required_completeness:
                raise EvidenceExtractionError(f"D13 completeness review missing: {row.get('family_id')}")
            if any(not isinstance(value, int) or value < 0 for value in completeness.values()):
                raise EvidenceExtractionError(f"D13 completeness counts invalid: {row.get('family_id')}")
            if completeness["baseline_finding_count"] != 1 or completeness["retained_baseline_findings"] > 1:
                raise EvidenceExtractionError(f"D13 completeness baseline invalid: {row.get('family_id')}")
    return {**base, "status": "valid_complete_d13_verified_part", "verification_totals": dict(sorted(corrections.items()))}


def finalize(output_dir: Path = FINAL) -> dict[str, Any]:
    if output_dir.exists():
        raise EvidenceExtractionError(f"immutable D13 final exists: {output_dir}")
    a_path, b_path = OUTPUT / "verified_part_a_v2.jsonl", OUTPUT / "verified_part_b.jsonl"
    va, vb = validate_verified(a_path, "a"), validate_verified(b_path, "b")
    rows = sorted(_read(a_path) + _read(b_path), key=lambda row: row["family_id"])
    if len(rows) != 570 or len({row["family_id"] for row in rows}) != 570:
        raise EvidenceExtractionError("D13 final population conservation failed")
    for row in rows:
        novelty = row["novelty_assessment"]
        if "dimensions" not in novelty:
            novelty["dimensions"] = {key: novelty.pop(key) for key in sorted(_dimensions(row))}
        for finding in row["measures_findings"]:
            if finding.get("direction") is None: finding["direction"] = "null"
    stop_candidates, near_candidates = [], []
    for row in rows:
        statuses = [value["status"] for value in row["novelty_assessment"]["dimensions"].values()]
        same_use = row["novelty_assessment"]["same_planning_use"]
        if all(status == "met" for status in statuses) and same_use == "yes":
            stop_candidates.append(row["family_id"])
        elif same_use in {"yes", "unclear"} and sum(status == "met" for status in statuses) >= 4 and all(status in {"met", "partial"} for status in statuses):
            near_candidates.append(row["family_id"])
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="d13-final-", dir=str(output_dir.parent)))
    try:
        ledger = staging / "evidence_matrix.jsonl"
        ledger.write_text("".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
        findings = sum(len(row["measures_findings"]) for row in rows)
        quantitative = sum(sum(bool(f["quantitative"]) for f in row["measures_findings"]) for row in rows)
        result = {
            "status": "d13_evidence_extraction_complete", "protocol_version": "1.3",
            "pipeline_version": VERSION, "created_at_utc": CREATED_AT,
            "verified_part_a": va, "verified_part_b": vb, "family_count": len(rows),
            "finding_count": findings, "quantitative_finding_count": quantitative,
            "evidence_band_counts": dict(sorted(Counter(row["evidence_band"] for row in rows).items())),
            "novelty_stop_candidate_family_ids": stop_candidates,
            "novelty_near_candidate_family_ids": near_candidates,
            "ledger_sha256": sha256(ledger),
            "interpretation_boundary": "Verified extraction candidates remain subject to D17 accountable-author citation confirmation. No causal, cognitive-load, organizational-validity, or final novelty conclusion is made at D13.",
            "security_boundary": "Local checksum-bound static text only; no network, credentials, Git history, package installation, links, or executable PDF content.",
        }
        path = staging / "d13_final_manifest.json"; path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (staging / "d13_final_manifest.json.sha256").write_text(f"{sha256(path)}  d13_final_manifest.json\n", encoding="utf-8")
        staging.rename(output_dir); return result
    except Exception:
        shutil.rmtree(staging, ignore_errors=True); raise


def verify(output_dir: Path = FINAL) -> dict[str, Any]:
    path = output_dir / "d13_final_manifest.json"; result = json.loads(path.read_text(encoding="utf-8"))
    if result["verified_part_a"] != validate_verified(OUTPUT / "verified_part_a_v2.jsonl", "a"):
        raise EvidenceExtractionError("D13 final no longer binds verified A")
    if result["verified_part_b"] != validate_verified(OUTPUT / "verified_part_b.jsonl", "b"):
        raise EvidenceExtractionError("D13 final no longer binds verified B")
    ledger = output_dir / "evidence_matrix.jsonl"; rows = _read(ledger)
    if sha256(ledger) != result["ledger_sha256"] or len(rows) != 570 or len({row["family_id"] for row in rows}) != 570:
        raise EvidenceExtractionError("D13 final ledger mismatch")
    if (output_dir / "d13_final_manifest.json.sha256").read_text().split()[0] != sha256(path):
        raise EvidenceExtractionError("D13 final sidecar mismatch")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("validate-part", "finalize", "verify")); parser.add_argument("--part", choices=("a", "b")); parser.add_argument("--path", type=Path); args = parser.parse_args()
    if args.command == "validate-part":
        if not args.part or not args.path: raise EvidenceExtractionError("validate-part needs --part and --path")
        result = validate_verified(args.path, args.part)
    elif args.command == "finalize": result = finalize()
    else: result = verify()
    print(json.dumps(result, sort_keys=True)); return 0


if __name__ == "__main__": raise SystemExit(main())
