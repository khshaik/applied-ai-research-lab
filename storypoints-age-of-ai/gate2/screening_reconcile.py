"""Reconcile two complete D08 passes and prepare the isolated D09 packet."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from typing import Any

from gate2.title_abstract_screening import OUTPUT as D08, ScreeningControlError, sha256, validate_pass, verify_packet


ROOT = Path(__file__).resolve().parents[1]
VERSION = "d08-d09-reconcile/1.0.0"
CREATED_AT = "2026-08-16T10:02:00Z"


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def prepare_d09(output_dir: Path = D08 / "d09") -> dict[str, Any]:
    if output_dir.exists():
        raise ScreeningControlError(f"immutable D09 packet already exists: {output_dir}")
    pass_a_path, pass_b_path = D08 / "pass_a_decisions.jsonl", D08 / "pass_b_decisions.jsonl"
    valid_a = validate_pass(pass_a_path, "pass-a")
    valid_b = validate_pass(pass_b_path, "pass-b")
    packet_manifest = verify_packet()
    pass_a = {row["family_id"]: row for row in _read_jsonl(pass_a_path)}
    pass_b = {row["family_id"]: row for row in _read_jsonl(pass_b_path)}
    family_packet = {}
    for shard in packet_manifest["shards"]:
        for row in _read_jsonl(D08 / shard["path"]):
            family_packet[row["family_id"]] = row

    candidate_rows, consensus_rows = [], []
    pair_counts = Counter()
    for family_id in sorted(family_packet):
        a, b = pass_a[family_id], pass_b[family_id]
        pair_counts[f"{a['decision']}|{b['decision']}"] += 1
        needs_adjudication = a["decision"] != b["decision"] or "unclear" in {a["decision"], b["decision"]}
        if needs_adjudication:
            candidate_rows.append({
                "family": family_packet[family_id],
                "pass_a": a,
                "pass_b": b,
                "adjudication_reason": "disagreement" if a["decision"] != b["decision"] else "consensus_unclear",
            })
        else:
            consensus_rows.append({
                "family_id": family_id,
                "record_id": a["record_id"],
                "final_title_abstract_decision": a["decision"],
                "decision_basis": "agent_consensus_no_unclear",
                "pass_a_screening_sha256": valid_a["sha256"],
                "pass_b_screening_sha256": valid_b["sha256"],
            })

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="d09-", dir=str(output_dir.parent)))
    try:
        packet_path = staging / "adjudication_packet.jsonl"
        packet_path.write_text("".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in candidate_rows), encoding="utf-8")
        consensus_path = staging / "consensus_decisions.jsonl"
        consensus_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in consensus_rows), encoding="utf-8")
        manifest = {
            "status": "prepared_for_separate_adjudication",
            "protocol_version": "1.3",
            "pipeline_version": VERSION,
            "created_at_utc": CREATED_AT,
            "family_count": len(family_packet),
            "pass_a": valid_a,
            "pass_b": valid_b,
            "agent_concordance_count": sum(a["decision"] == pass_b[fid]["decision"] for fid, a in pass_a.items()),
            "agent_concordance_rate": sum(a["decision"] == pass_b[fid]["decision"] for fid, a in pass_a.items()) / len(family_packet),
            "decision_pair_counts": dict(sorted(pair_counts.items())),
            "consensus_without_unclear_count": len(consensus_rows),
            "adjudication_candidate_count": len(candidate_rows),
            "adjudication_packet_sha256": sha256(packet_path),
            "consensus_decisions_sha256": sha256(consensus_path),
            "interpretation_boundary": "Agreement is AI-agent concordance under separated contexts, not human inter-rater reliability. All disagreements and unclear decisions require a distinct adjudication context.",
        }
        manifest_path = staging / "d08_d09_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (staging / "d08_d09_manifest.json.sha256").write_text(f"{sha256(manifest_path)}  d08_d09_manifest.json\n", encoding="utf-8")
        staging.rename(output_dir)
        return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def verify(output_dir: Path = D08 / "d09") -> dict[str, Any]:
    manifest_path = output_dir / "d08_d09_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["pass_a"] != validate_pass(D08 / "pass_a_decisions.jsonl", "pass-a"):
        raise ScreeningControlError("D09 no longer binds the valid pass A artifact")
    if manifest["pass_b"] != validate_pass(D08 / "pass_b_decisions.jsonl", "pass-b"):
        raise ScreeningControlError("D09 no longer binds the valid pass B artifact")
    if sha256(output_dir / "adjudication_packet.jsonl") != manifest["adjudication_packet_sha256"]:
        raise ScreeningControlError("D09 adjudication packet mismatch")
    if sha256(output_dir / "consensus_decisions.jsonl") != manifest["consensus_decisions_sha256"]:
        raise ScreeningControlError("D09 consensus file mismatch")
    if manifest["consensus_without_unclear_count"] + manifest["adjudication_candidate_count"] != manifest["family_count"]:
        raise ScreeningControlError("D09 candidate/consensus conservation failed")
    if (output_dir / "d08_d09_manifest.json.sha256").read_text().split()[0] != sha256(manifest_path):
        raise ScreeningControlError("D09 manifest sidecar mismatch")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("prepare", "verify"))
    args = parser.parse_args()
    result = prepare_d09() if args.command == "prepare" else verify()
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
