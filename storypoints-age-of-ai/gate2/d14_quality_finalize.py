"""Validate D14 quality adjudication and publish the final 212-family ledger."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import tempfile
from typing import Any

from gate2.citation_chasing import OUTPUT, sha256
from gate2.d12_appraisal_partition_b_local import FORMS
from gate2.d14_quality_reconcile import FINAL as ADJUDICATION, verify as verify_reconciliation


FINAL = OUTPUT / "quality_appraisal_final"
VERSION = "d14-quality-finalize/1.0.0"


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def validate_adjudication(path: Path = ADJUDICATION / "adjudicated_appraisals.jsonl") -> dict[str, Any]:
    reconciliation = verify_reconciliation()
    packet = _read(ADJUDICATION / "adjudication_packet.jsonl")
    expected = {row["family"]["family_id"]: row["family"] for row in packet}
    rows = _read(path)
    seen: set[str] = set(); contexts: set[str] = set()
    for row in rows:
        family_id = row.get("family_id")
        if family_id not in expected or family_id in seen:
            raise ValueError("unknown or duplicate D14 quality adjudication")
        seen.add(family_id)
        source = expected[family_id]
        if row.get("record_id") != source["record_id"] or row.get("source_text_sha256") != source["source_text_sha256"]:
            raise ValueError("D14 quality adjudication source binding mismatch")
        if row.get("appraiser_agent_id") != "d14-quality-adjudicator-v1" or row.get("decision_basis") != "separate_source_grounded_quality_adjudication":
            raise ValueError("D14 quality adjudicator provenance mismatch")
        context = row.get("review_context_id")
        if not isinstance(context, str) or not context.startswith("d14-quality-adjudicator-") or context in contexts:
            raise ValueError("D14 quality adjudicator context invalid")
        contexts.add(context)
        form = row.get("appraisal_form")
        if form not in FORMS:
            raise ValueError("D14 quality adjudication form invalid")
        criteria = row.get("criteria")
        if not isinstance(criteria, list) or [item.get("criterion_id") for item in criteria] != [item[0] for item in FORMS[form]]:
            raise ValueError("D14 quality adjudication criteria mismatch")
        for item in criteria:
            if item.get("score") not in {0, 1, 2} or not item.get("justification") or not item.get("source_locator"):
                raise ValueError("D14 quality adjudication criterion invalid")
            locator = str(item["source_locator"])
            if not locator.startswith("page ") or not locator[5:].isdigit() or not 1 <= int(locator[5:]) <= source["page_count"]:
                raise ValueError("D14 quality adjudication locator invalid")
        points = sum(item["score"] for item in criteria)
        if row.get("applicable_points") != 20 or row.get("points_awarded") != points or abs(row.get("percent", -1) - points * 5.0) > 1e-9:
            raise ValueError("D14 quality adjudication arithmetic mismatch")
        critical = row.get("critical_flaw") is True
        band = "low_contextual" if critical or row["percent"] < 50 else "moderate" if row["percent"] < 75 else "high"
        if row.get("evidence_band") != band or (critical and not row.get("critical_flaw_basis")):
            raise ValueError("D14 quality adjudication band mismatch")
        if not row.get("design_type") or row.get("evidence_nature") not in {"observed", "self-reported", "modeled", "conceptual"}:
            raise ValueError("D14 quality adjudication design/nature invalid")
        if len(row.get("security_attestation", "")) < 30:
            raise ValueError("D14 quality adjudication security attestation incomplete")
    if seen != set(expected):
        raise ValueError(f"D14 quality adjudication incomplete: {len(set(expected) - seen)} missing")
    sidecar = path.with_suffix(path.suffix + ".sha256")
    if not sidecar.exists() or sidecar.read_text().split()[0] != sha256(path):
        raise ValueError("D14 quality adjudication sidecar mismatch")
    return {"status": "valid_complete_quality_adjudication", "family_count": len(rows), "forms": dict(Counter(row["appraisal_form"] for row in rows)), "bands": dict(Counter(row["evidence_band"] for row in rows)), "sha256": sha256(path)}


def finalize() -> dict[str, Any]:
    if FINAL.exists():
        raise ValueError(f"immutable D14 final quality ledger exists: {FINAL}")
    reconciliation = verify_reconciliation(); adjudication = validate_adjudication()
    consensus = _read(ADJUDICATION / "consensus_appraisals.jsonl")
    adjudicated = _read(ADJUDICATION / "adjudicated_appraisals.jsonl")
    rows = sorted(consensus + adjudicated, key=lambda row: row["family_id"])
    if len(rows) != 212 or len({row["family_id"] for row in rows}) != 212:
        raise ValueError("D14 final quality population mismatch")
    FINAL.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="d14-quality-final-", dir=str(FINAL.parent)))
    try:
        ledger_path = staging / "final_quality_appraisals.jsonl"
        ledger_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
        manifest = {
            "status": "d14_quality_appraisal_complete", "protocol_version": "1.3", "pipeline_version": VERSION,
            "family_count": len(rows), "forms": dict(Counter(row["appraisal_form"] for row in rows)),
            "bands": dict(Counter(row["evidence_band"] for row in rows)),
            "critical_flaw_count": sum(row["critical_flaw"] is True for row in rows),
            "consensus_count": len(consensus), "adjudicated_count": len(adjudicated),
            "reconciliation_manifest_sha256": sha256(ADJUDICATION / "reconciliation_manifest.json"),
            "adjudication": adjudication, "final_ledger_sha256": sha256(ledger_path),
            "interpretation_boundary": "Quality bands weight evidence; they do not change eligibility or establish human cognitive-load validity.",
        }
        manifest_path = staging / "final_quality_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (staging / "final_quality_manifest.json.sha256").write_text(f"{sha256(manifest_path)}  final_quality_manifest.json\n", encoding="ascii")
        staging.rename(FINAL)
        return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True); raise


def verify() -> dict[str, Any]:
    manifest_path = FINAL / "final_quality_manifest.json"; manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = _read(FINAL / "final_quality_appraisals.jsonl")
    if len(rows) != manifest["family_count"] or sha256(FINAL / "final_quality_appraisals.jsonl") != manifest["final_ledger_sha256"]:
        raise ValueError("D14 final quality ledger mismatch")
    if manifest["adjudication"] != validate_adjudication():
        raise ValueError("D14 final quality adjudication binding mismatch")
    if (FINAL / "final_quality_manifest.json.sha256").read_text().split()[0] != sha256(manifest_path):
        raise ValueError("D14 final quality manifest sidecar mismatch")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("validate-adjudication", "finalize", "verify")); args = parser.parse_args()
    result = validate_adjudication() if args.command == "validate-adjudication" else finalize() if args.command == "finalize" else verify()
    print(json.dumps(result, sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
