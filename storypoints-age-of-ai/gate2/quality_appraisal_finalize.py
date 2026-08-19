"""Validate D12 dispute adjudication and publish final quality appraisals."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import shutil
import tempfile
from typing import Any

from gate2.fulltext_screening import FullTextScreeningError, sha256
from gate2.quality_appraisal import (
    BANDS, CRITICAL_BASES, FORMS, NATURES, OUTPUT,
    QualityAppraisalError, _expected_band,
)
from gate2.quality_appraisal_reconcile import RECONCILIATION, verify as verify_reconciliation


FINAL = OUTPUT / "final"
VERSION = "d12-quality-appraisal-finalizer/1.0.0"
CREATED_AT = "2026-08-17T04:00:00Z"


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def validate_adjudication(path: Path = RECONCILIATION / "adjudicated_appraisals.jsonl") -> dict[str, Any]:
    reconciliation = verify_reconciliation(RECONCILIATION)
    packet = _read(RECONCILIATION / "appraisal_disputes.jsonl")
    expected = {row["family"]["family_id"]: row for row in packet}
    rows = _read(path)
    seen: set[str] = set(); forms: Counter[str] = Counter(); bands: Counter[str] = Counter()
    for row in rows:
        family_id = row.get("family_id")
        if family_id not in expected or family_id in seen:
            raise QualityAppraisalError(f"unknown/duplicate D12 adjudication family: {family_id}")
        seen.add(family_id); source = expected[family_id]["family"]
        if row.get("record_id") != source["record_id"] or row.get("source_text_sha256") != source["extracted_text_sha256"]:
            raise QualityAppraisalError(f"D12 adjudication identity/source mismatch: {family_id}")
        if row.get("adjudicator_agent_id") != "d12-quality-adjudicator-v1" or not row.get("review_context_id"):
            raise QualityAppraisalError(f"D12 adjudication provenance missing: {family_id}")
        form = row.get("appraisal_form")
        if form not in FORMS:
            raise QualityAppraisalError(f"D12 adjudication form invalid: {family_id}")
        criteria = row.get("criteria_scores")
        if not isinstance(criteria, list) or len(criteria) != FORMS[form]:
            raise QualityAppraisalError(f"D12 adjudication criterion count invalid: {family_id}")
        ids = set(); points = 0
        for criterion in criteria:
            cid = str(criterion.get("criterion_id", "")); score = criterion.get("score")
            if not cid or cid in ids or score not in {0, 1, 2}:
                raise QualityAppraisalError(f"D12 adjudication criterion invalid: {family_id}/{cid}")
            ids.add(cid); points += score
            locator = criterion.get("source_locator", "")
            match = re.search(r"\bpage(?:s)?\s+(\d+)", locator, flags=re.I)
            if not criterion.get("justification") or not match or int(match.group(1)) > int(source["page_count"]):
                raise QualityAppraisalError(f"D12 adjudication source evidence invalid: {family_id}/{cid}")
        applicable = 2 * FORMS[form]; percent = 100 * points / applicable
        if row.get("applicable_points") != applicable or row.get("points_awarded") != points:
            raise QualityAppraisalError(f"D12 adjudication arithmetic mismatch: {family_id}")
        if abs(float(row.get("percent_score", -1)) - percent) > 0.051:
            raise QualityAppraisalError(f"D12 adjudication percentage mismatch: {family_id}")
        critical = row.get("critical_flaw"); basis = row.get("critical_flaw_basis")
        if not isinstance(critical, bool) or basis not in CRITICAL_BASES or critical != (basis != "none"):
            raise QualityAppraisalError(f"D12 adjudication critical flaw invalid: {family_id}")
        band = row.get("evidence_band")
        if band not in BANDS or band != _expected_band(points, applicable, critical):
            raise QualityAppraisalError(f"D12 adjudication band invalid: {family_id}")
        if row.get("data_nature") not in NATURES or not row.get("design_type") or not row.get("resolution_rationale"):
            raise QualityAppraisalError(f"D12 adjudication interpretation missing: {family_id}")
        security = row.get("security_attestation")
        if not ((isinstance(security, str) and len(security) >= 30) or isinstance(security, dict)):
            raise QualityAppraisalError(f"D12 adjudication security attestation missing: {family_id}")
        forms[form] += 1; bands[band] += 1
    if seen != set(expected) or len(rows) != reconciliation["dispute_count"]:
        raise QualityAppraisalError(f"D12 adjudication incomplete: missing {len(set(expected)-seen)}")
    sidecar = path.with_name(path.name + ".sha256")
    if sidecar.exists() and sidecar.read_text(encoding="utf-8").split()[0] != sha256(path):
        raise QualityAppraisalError("D12 adjudication sidecar mismatch")
    return {
        "status": "valid_complete_d12_dispute_adjudication", "family_count": len(rows),
        "form_counts": dict(sorted(forms.items())), "band_counts": dict(sorted(bands.items())),
        "sha256": sha256(path),
    }


def finalize(output_dir: Path = FINAL) -> dict[str, Any]:
    if output_dir.exists():
        raise QualityAppraisalError(f"immutable D12 final exists: {output_dir}")
    reconciliation = verify_reconciliation(RECONCILIATION)
    adjudication = validate_adjudication()
    rows = _read(RECONCILIATION / "concordant_appraisals.jsonl") + _read(RECONCILIATION / "adjudicated_appraisals.jsonl")
    rows.sort(key=lambda row: row["family_id"])
    if len(rows) != 570 or len({row["family_id"] for row in rows}) != 570:
        raise QualityAppraisalError("D12 final population conservation failed")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="d12-final-", dir=str(output_dir.parent)))
    try:
        ledger = staging / "quality_appraisals.jsonl"
        ledger.write_text("".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
        manifest = {
            "status": "d12_quality_appraisal_complete", "protocol_version": "1.3",
            "pipeline_version": VERSION, "created_at_utc": CREATED_AT,
            "reconciliation_manifest_sha256": sha256(RECONCILIATION / "d12_reconciliation_manifest.json"),
            "adjudication_validation": adjudication, "family_count": len(rows),
            "form_counts": dict(sorted(Counter(row["appraisal_form"] for row in rows).items())),
            "band_counts": dict(sorted(Counter(row["evidence_band"] for row in rows).items())),
            "critical_flaw_count": sum(bool(row["critical_flaw"]) for row in rows),
            "ledger_sha256": sha256(ledger),
            "interpretation_boundary": "Evidence bands govern narrative weight and sensitivity analyses; they are not certainty weights, eligibility decisions, or evidence that technical outcomes measure human cognitive workload.",
            "security_boundary": "Local checksum-bound extracted text only; no network, credentials, Git history, package installation, or executable PDF content.",
        }
        path = staging / "d12_final_manifest.json"
        path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (staging / "d12_final_manifest.json.sha256").write_text(f"{sha256(path)}  d12_final_manifest.json\n", encoding="utf-8")
        staging.rename(output_dir); return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True); raise


def verify(output_dir: Path = FINAL) -> dict[str, Any]:
    path = output_dir / "d12_final_manifest.json"; result = json.loads(path.read_text(encoding="utf-8"))
    if result["adjudication_validation"] != validate_adjudication():
        raise QualityAppraisalError("D12 final no longer binds adjudication")
    ledger = output_dir / "quality_appraisals.jsonl"; rows = _read(ledger)
    if sha256(ledger) != result["ledger_sha256"] or len(rows) != 570 or len({row["family_id"] for row in rows}) != 570:
        raise QualityAppraisalError("D12 final ledger mismatch")
    if (output_dir / "d12_final_manifest.json.sha256").read_text().split()[0] != sha256(path):
        raise QualityAppraisalError("D12 final manifest sidecar mismatch")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("validate-adjudication", "finalize", "verify")); args = parser.parse_args()
    result = validate_adjudication() if args.command == "validate-adjudication" else finalize() if args.command == "finalize" else verify()
    print(json.dumps(result, sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
