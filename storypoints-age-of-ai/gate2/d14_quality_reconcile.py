"""Reconcile D14 primary and blinded cross-audit quality appraisals."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import tempfile
from typing import Any

from gate2.citation_chasing import OUTPUT, sha256
from gate2.d14_quality_appraisal import PACKET, validate_appraisal, verify_packet


BASE = OUTPUT / "quality_appraisal"
FINAL = BASE / "adjudication"
VERSION = "d14-quality-reconcile/1.0.0"
FILES = {
    "a": (BASE / "appraisal_part_a.jsonl", "d14-appraiser-a-v1", BASE / "audit_part_a_by_b.jsonl", "d14-audit-a-by-b-v1"),
    "b": (BASE / "appraisal_part_b.jsonl", "d14-appraiser-b-v1", BASE / "audit_part_b_by_a.jsonl", "d14-audit-b-by-a-v1"),
}


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _signature(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        row["appraisal_form"], row["design_type"], row["evidence_nature"], row["critical_flaw"],
        row.get("critical_flaw_basis"), row["points_awarded"], row["evidence_band"],
        tuple((item["criterion_id"], item["score"]) for item in row["criteria"]),
    )


def prepare() -> dict[str, Any]:
    if FINAL.exists():
        raise ValueError(f"immutable D14 quality adjudication package exists: {FINAL}")
    manifest = verify_packet()
    packet: dict[str, dict[str, Any]] = {}
    for partition in manifest["partitions"]:
        for row in _read(Path(partition["path"])):
            packet[row["family_id"]] = row
    candidates: list[dict[str, Any]] = []
    consensus: list[dict[str, Any]] = []
    validations: dict[str, Any] = {}
    pairs: Counter[str] = Counter()
    for partition, (primary_path, primary_id, audit_path, audit_id) in FILES.items():
        validations[f"primary_{partition}"] = validate_appraisal(primary_path, partition, primary_id)
        validations[f"audit_{partition}"] = validate_appraisal(audit_path, partition, audit_id)
        primary = {row["family_id"]: row for row in _read(primary_path)}
        audit = {row["family_id"]: row for row in _read(audit_path)}
        if set(primary) != set(audit):
            raise ValueError("D14 quality primary/audit population mismatch")
        for family_id in sorted(primary):
            p_row, a_row = primary[family_id], audit[family_id]
            same = _signature(p_row) == _signature(a_row)
            pairs["exact_consensus" if same else "requires_adjudication"] += 1
            if same:
                consensus.append({**p_row, "decision_basis": "exact_primary_cross_audit_consensus"})
            else:
                candidates.append({"family": packet[family_id], "primary": p_row, "cross_audit": a_row, "adjudication_reason": "quality_appraisal_disagreement"})
    if len(candidates) + len(consensus) != 212:
        raise ValueError("D14 quality reconciliation conservation failure")
    FINAL.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="d14-quality-adjudication-", dir=str(FINAL.parent)))
    try:
        packet_path = staging / "adjudication_packet.jsonl"
        consensus_path = staging / "consensus_appraisals.jsonl"
        packet_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in candidates), encoding="utf-8")
        consensus_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in consensus), encoding="utf-8")
        result = {
            "status": "prepared_for_separate_quality_adjudication",
            "protocol_version": "1.3", "pipeline_version": VERSION, "family_count": 212,
            "validations": validations, "pair_counts": dict(pairs),
            "consensus_count": len(consensus), "adjudication_candidate_count": len(candidates),
            "adjudication_packet_sha256": sha256(packet_path), "consensus_appraisals_sha256": sha256(consensus_path),
            "decision_rule": "Any form, design, nature, critical-flaw, total, band, or criterion-score difference is separately adjudicated; no averaging or confidence voting.",
        }
        manifest_path = staging / "reconciliation_manifest.json"
        manifest_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (staging / "reconciliation_manifest.json.sha256").write_text(f"{sha256(manifest_path)}  reconciliation_manifest.json\n", encoding="ascii")
        staging.rename(FINAL)
        return result
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def verify() -> dict[str, Any]:
    manifest_path = FINAL / "reconciliation_manifest.json"
    result = json.loads(manifest_path.read_text(encoding="utf-8"))
    if sha256(FINAL / "adjudication_packet.jsonl") != result["adjudication_packet_sha256"] or sha256(FINAL / "consensus_appraisals.jsonl") != result["consensus_appraisals_sha256"]:
        raise ValueError("D14 quality reconciliation artifact checksum mismatch")
    if result["consensus_count"] + result["adjudication_candidate_count"] != 212:
        raise ValueError("D14 quality reconciliation count mismatch")
    if (FINAL / "reconciliation_manifest.json.sha256").read_text().split()[0] != sha256(manifest_path):
        raise ValueError("D14 quality reconciliation manifest sidecar mismatch")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("prepare", "verify")); args = parser.parse_args()
    print(json.dumps(prepare() if args.command == "prepare" else verify(), sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
