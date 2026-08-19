"""Validate and reconcile D12 source-grounded quality appraisals."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import shutil
import tempfile
from typing import Any

from gate2.fulltext_screening import ROOT, SYSTEMATIC, FullTextScreeningError, sha256


OUTPUT = SYSTEMATIC / "d12"
D11_LEDGER = SYSTEMATIC / "d11/screening/final/fulltext_eligibility_decisions.jsonl"
EXTRACTION = SYSTEMATIC / "d11/extraction/text"
VERSION = "d12-quality-appraisal-controller/1.0.0"
CREATED_AT = "2026-08-17T03:00:00Z"
FORMS = {
    "quantitative_mixed": 10,
    "qualitative": 10,
    "secondary_review": 10,
    "conceptual_framework": 10,
    "grey_aacods": 6,
}
BANDS = {"high", "moderate", "low_contextual"}
NATURES = {"observed", "self_reported", "modeled", "conceptual", "mixed"}
CRITICAL_BASES = {
    "none",
    "no_inspectable_data_provenance",
    "fatal_design_outcome_mismatch",
    "unverifiable_primary_claim",
}


class QualityAppraisalError(FullTextScreeningError):
    pass


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def expected_part(part: str) -> dict[str, tuple[dict[str, Any], str]]:
    if part not in {"a", "b"}:
        raise QualityAppraisalError("D12 part must be a or b")
    included = sorted(
        (row for row in _read(D11_LEDGER) if row["final_status"] == "included_full_text"),
        key=lambda row: row["family_id"],
    )
    if len(included) != 570:
        raise QualityAppraisalError("D12 expected 570 D11 inclusions")
    selected = included[:285] if part == "a" else included[285:]
    return {
        row["family_id"]: (row, sha256(EXTRACTION / f"{row['family_id']}.json"))
        for row in selected
    }


def _expected_band(points: int, applicable: int, critical: bool) -> str:
    percent = 100 * points / applicable
    if critical or percent < 50:
        return "low_contextual"
    if percent < 75:
        return "moderate"
    return "high"


def validate_part(path: Path, part: str) -> dict[str, Any]:
    expected = expected_part(part)
    rows = _read(path)
    seen: set[str] = set()
    forms: Counter[str] = Counter()
    bands: Counter[str] = Counter()
    for row in rows:
        family_id = row.get("family_id")
        if family_id not in expected or family_id in seen:
            raise QualityAppraisalError(f"unknown/duplicate D12 family: {family_id}")
        seen.add(family_id)
        source, source_sha = expected[family_id]
        if row.get("record_id") != source["record_id"] or row.get("source_text_sha256") != source_sha:
            raise QualityAppraisalError(f"D12 identity/source checksum mismatch: {family_id}")
        if not row.get("appraiser_agent_id") or not row.get("review_context_id"):
            raise QualityAppraisalError(f"D12 appraiser provenance missing: {family_id}")
        form = row.get("appraisal_form")
        if form not in FORMS:
            raise QualityAppraisalError(f"D12 appraisal form invalid: {family_id}")
        criteria = row.get("criteria_scores", row.get("criteria"))
        if not isinstance(criteria, list) or len(criteria) != FORMS[form]:
            raise QualityAppraisalError(f"D12 criterion count invalid: {family_id}")
        criterion_ids = set()
        points = 0
        for criterion in criteria:
            cid = str(criterion.get("criterion_id", ""))
            if not cid or cid in criterion_ids:
                raise QualityAppraisalError(f"D12 criterion IDs invalid: {family_id}")
            criterion_ids.add(cid)
            score = criterion.get("score")
            if score not in {0, 1, 2}:
                raise QualityAppraisalError(f"D12 criterion score invalid: {family_id}/{cid}")
            locator = criterion.get("source_locator", criterion.get("page_locator", ""))
            if not criterion.get("justification") or not re.search(r"(?:\bpage(?:s)?|\bp\.)\s+\d+", locator, flags=re.I):
                raise QualityAppraisalError(f"D12 criterion evidence missing: {family_id}/{cid}")
            points += score
        applicable = 2 * FORMS[form]
        if row.get("applicable_points") != applicable or row.get("points_awarded") != points:
            raise QualityAppraisalError(f"D12 score arithmetic mismatch: {family_id}")
        percent = 100 * points / applicable
        if abs(float(row.get("percent_score", row.get("percent", -1))) - percent) > 0.051:
            raise QualityAppraisalError(f"D12 percentage mismatch: {family_id}")
        critical = row.get("critical_flaw")
        raw_basis = row.get("critical_flaw_basis")
        basis = "none" if raw_basis in {None, "None", "none"} else str(raw_basis).lower().replace(" ", "_")
        if not isinstance(critical, bool) or basis not in CRITICAL_BASES:
            raise QualityAppraisalError(f"D12 critical-flaw declaration invalid: {family_id}")
        if critical != (basis != "none"):
            raise QualityAppraisalError(f"D12 critical-flaw basis inconsistent: {family_id}")
        band = row.get("evidence_band")
        if band not in BANDS or band != _expected_band(points, applicable, critical):
            raise QualityAppraisalError(f"D12 evidence band mismatch: {family_id}")
        nature = str(row.get("data_nature", row.get("evidence_nature", ""))).replace("-", "_")
        if nature not in NATURES or not row.get("design_type"):
            raise QualityAppraisalError(f"D12 design/data nature missing: {family_id}")
        security = row.get("security_attestation")
        security_ok = (
            isinstance(security, str) and len(security) >= 30
        ) or (
            isinstance(security, dict)
            and security.get("local_only") is True
            and security.get("network_used") is False
            and security.get("git_or_history_inspected") is False
            and security.get("environment_or_secrets_inspected") is False
            and security.get("credentials_accessed") is False
            and security.get("packages_installed") is False
            and security.get("pdf_executed") is False
        )
        if not row.get("overall_notes") or not security_ok:
            raise QualityAppraisalError(f"D12 notes/security provenance missing: {family_id}")
        forms[form] += 1
        bands[band] += 1
    if seen != set(expected):
        raise QualityAppraisalError(f"D12 part {part} incomplete: missing {len(set(expected) - seen)}")
    sidecar = path.with_name(path.name + ".sha256")
    if sidecar.exists() and sidecar.read_text(encoding="utf-8").split()[0] != sha256(path):
        raise QualityAppraisalError(f"D12 part {part} sidecar mismatch")
    return {
        "status": "valid_complete_d12_appraisal_part",
        "part": part, "family_count": len(rows),
        "form_counts": dict(sorted(forms.items())), "band_counts": dict(sorted(bands.items())),
        "sha256": sha256(path),
    }


def combine(output_dir: Path = OUTPUT / "primary") -> dict[str, Any]:
    if output_dir.exists():
        raise QualityAppraisalError(f"immutable D12 primary output exists: {output_dir}")
    a_path, b_path = OUTPUT / "appraisal_part_a.jsonl", OUTPUT / "appraisal_part_b.jsonl"
    va, vb = validate_part(a_path, "a"), validate_part(b_path, "b")
    source_rows = sorted(_read(a_path) + _read(b_path), key=lambda row: row["family_id"])
    rows = []
    for source in source_rows:
        row = dict(source)
        row["criteria_scores"] = row.pop("criteria", row.get("criteria_scores"))
        row["percent_score"] = row.pop("percent", row.get("percent_score"))
        row["data_nature"] = str(row.pop("evidence_nature", row.get("data_nature"))).replace("-", "_")
        raw_basis = row.get("critical_flaw_basis")
        row["critical_flaw_basis"] = "none" if raw_basis in {None, "None", "none"} else str(raw_basis).lower().replace(" ", "_")
        rows.append(row)
    if len(rows) != 570 or len({row["family_id"] for row in rows}) != 570:
        raise QualityAppraisalError("D12 combined population invalid")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="d12-primary-", dir=str(output_dir.parent)))
    try:
        ledger = staging / "primary_quality_appraisals.jsonl"
        ledger.write_text("".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
        manifest = {
            "status": "d12_primary_appraisals_complete_pending_audit",
            "protocol_version": "1.3", "pipeline_version": VERSION,
            "created_at_utc": CREATED_AT, "part_a_validation": va, "part_b_validation": vb,
            "family_count": len(rows),
            "form_counts": dict(sorted(Counter(row["appraisal_form"] for row in rows).items())),
            "band_counts": dict(sorted(Counter(row["evidence_band"] for row in rows).items())),
            "critical_flaw_count": sum(bool(row["critical_flaw"]) for row in rows),
            "ledger_sha256": sha256(ledger),
            "interpretation_boundary": "Quality bands govern evidentiary weight, not eligibility or mathematical certainty. Technical quality evidence cannot validate human cognitive workload.",
            "security_boundary": "Local checksum-bound extracted text only; no network, credentials, Git history, package installation, or executable PDF content.",
        }
        path = staging / "d12_primary_manifest.json"
        path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (staging / "d12_primary_manifest.json.sha256").write_text(f"{sha256(path)}  d12_primary_manifest.json\n", encoding="utf-8")
        staging.rename(output_dir)
        return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def verify_primary(output_dir: Path = OUTPUT / "primary") -> dict[str, Any]:
    path = output_dir / "d12_primary_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest["part_a_validation"] != validate_part(OUTPUT / "appraisal_part_a.jsonl", "a"):
        raise QualityAppraisalError("D12 primary no longer binds part A")
    if manifest["part_b_validation"] != validate_part(OUTPUT / "appraisal_part_b.jsonl", "b"):
        raise QualityAppraisalError("D12 primary no longer binds part B")
    ledger = output_dir / "primary_quality_appraisals.jsonl"
    if sha256(ledger) != manifest["ledger_sha256"] or len(_read(ledger)) != 570:
        raise QualityAppraisalError("D12 primary ledger mismatch")
    if (output_dir / "d12_primary_manifest.json.sha256").read_text().split()[0] != sha256(path):
        raise QualityAppraisalError("D12 primary manifest sidecar mismatch")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("validate-part", "combine", "verify-primary"))
    parser.add_argument("--part", choices=("a", "b")); parser.add_argument("--path", type=Path)
    args = parser.parse_args()
    if args.command == "validate-part":
        if not args.part or not args.path:
            raise QualityAppraisalError("validate-part requires --part and --path")
        result = validate_part(args.path, args.part)
    elif args.command == "combine":
        result = combine()
    else:
        result = verify_primary()
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
