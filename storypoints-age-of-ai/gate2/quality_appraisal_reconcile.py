"""Reconcile blinded D12 primary and cross-audit appraisals."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import tempfile
from typing import Any

from gate2.fulltext_screening import OUTPUT as D11_SCREENING, FullTextScreeningError, sha256
from gate2.quality_appraisal import OUTPUT, QualityAppraisalError, validate_part, verify_primary


RECONCILIATION = OUTPUT / "reconciliation"
VERSION = "d12-appraisal-reconciliation/1.0.0"
CREATED_AT = "2026-08-17T03:30:00Z"


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _criteria(row: dict[str, Any]) -> dict[str, int]:
    values = row.get("criteria_scores", row.get("criteria", []))
    return {str(item["criterion_id"]): int(item["score"]) for item in values}


def prepare(output_dir: Path = RECONCILIATION) -> dict[str, Any]:
    if output_dir.exists():
        raise QualityAppraisalError(f"immutable D12 reconciliation exists: {output_dir}")
    primary = verify_primary()
    audit_a_path = OUTPUT / "audit_part_a_by_b.jsonl"
    audit_b_path = OUTPUT / "audit_part_b_by_a.jsonl"
    audit_a = validate_part(audit_a_path, "a")
    audit_b = validate_part(audit_b_path, "b")
    primary_rows = {row["family_id"]: row for row in _read(OUTPUT / "primary/primary_quality_appraisals.jsonl")}
    audit_rows = {row["family_id"]: row for row in _read(audit_a_path) + _read(audit_b_path)}
    packet_by_id = {}
    manifest = json.loads((D11_SCREENING / "d11_packet_manifest.json").read_text(encoding="utf-8"))
    for shard in manifest["shards"]:
        for row in _read(D11_SCREENING / shard["path"]):
            packet_by_id[row["family_id"]] = row
    disputes, concordant = [], []
    reasons: Counter[str] = Counter()
    for family_id in sorted(primary_rows):
        p, a = primary_rows[family_id], audit_rows[family_id]
        dispute_reasons = []
        if p["appraisal_form"] != a["appraisal_form"]:
            dispute_reasons.append("appraisal_form")
        if _criteria(p) != _criteria(a):
            dispute_reasons.append("criterion_scores")
        if p["critical_flaw"] != a["critical_flaw"] or p["critical_flaw_basis"] != (
            "none" if a.get("critical_flaw_basis") in {None, "None", "none"} else str(a.get("critical_flaw_basis")).lower().replace(" ", "_")
        ):
            dispute_reasons.append("critical_flaw")
        if p["evidence_band"] != a["evidence_band"]:
            dispute_reasons.append("evidence_band")
        if dispute_reasons:
            for reason in dispute_reasons:
                reasons[reason] += 1
            disputes.append({
                "family": packet_by_id[family_id], "primary_appraisal": p,
                "cross_audit_appraisal": a, "dispute_reasons": dispute_reasons,
            })
        else:
            concordant.append(p)
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="d12-reconcile-", dir=str(output_dir.parent)))
    try:
        disputes_path = staging / "appraisal_disputes.jsonl"
        disputes_path.write_text("".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in disputes), encoding="utf-8")
        concordant_path = staging / "concordant_appraisals.jsonl"
        concordant_path.write_text("".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in concordant), encoding="utf-8")
        result = {
            "status": "d12_appraisal_reconciled_pending_dispute_resolution",
            "protocol_version": "1.3", "pipeline_version": VERSION,
            "created_at_utc": CREATED_AT, "primary_validation": primary,
            "audit_part_a_validation": audit_a, "audit_part_b_validation": audit_b,
            "family_count": len(primary_rows), "concordant_count": len(concordant),
            "dispute_count": len(disputes), "dispute_reason_counts": dict(sorted(reasons.items())),
            "disputes_sha256": sha256(disputes_path), "concordant_sha256": sha256(concordant_path),
            "interpretation_boundary": "Cross-audit agreement is AI-agent reproducibility, not human appraisal reliability. Every criterion/form/band/critical-flaw dispute requires separate resolution.",
        }
        path = staging / "d12_reconciliation_manifest.json"
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (staging / "d12_reconciliation_manifest.json.sha256").write_text(f"{sha256(path)}  d12_reconciliation_manifest.json\n", encoding="utf-8")
        staging.rename(output_dir)
        return result
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def verify(output_dir: Path = RECONCILIATION) -> dict[str, Any]:
    path = output_dir / "d12_reconciliation_manifest.json"
    result = json.loads(path.read_text(encoding="utf-8"))
    if result["primary_validation"] != verify_primary():
        raise QualityAppraisalError("D12 reconciliation no longer binds primary")
    if result["audit_part_a_validation"] != validate_part(OUTPUT / "audit_part_a_by_b.jsonl", "a"):
        raise QualityAppraisalError("D12 reconciliation no longer binds audit A")
    if result["audit_part_b_validation"] != validate_part(OUTPUT / "audit_part_b_by_a.jsonl", "b"):
        raise QualityAppraisalError("D12 reconciliation no longer binds audit B")
    if sha256(output_dir / "appraisal_disputes.jsonl") != result["disputes_sha256"]:
        raise QualityAppraisalError("D12 dispute packet mismatch")
    if sha256(output_dir / "concordant_appraisals.jsonl") != result["concordant_sha256"]:
        raise QualityAppraisalError("D12 concordant packet mismatch")
    if result["concordant_count"] + result["dispute_count"] != result["family_count"]:
        raise QualityAppraisalError("D12 reconciliation conservation failed")
    if (output_dir / "d12_reconciliation_manifest.json.sha256").read_text().split()[0] != sha256(path):
        raise QualityAppraisalError("D12 reconciliation sidecar mismatch")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("prepare", "verify")); args = parser.parse_args()
    print(json.dumps(prepare() if args.command == "prepare" else verify(), sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
