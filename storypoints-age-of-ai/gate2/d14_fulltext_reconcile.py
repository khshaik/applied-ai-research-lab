"""Reconcile isolated D14 full-text passes and prepare adjudication."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import tempfile
from typing import Any

from gate2.citation_chasing import OUTPUT, sha256
from gate2.d14_fulltext_screening import PACKET, validate_pass, verify_packet


SCREEN = OUTPUT / "fulltext_screening"
FINAL = SCREEN / "adjudication_v2"
PASS_A = SCREEN / "pass_a_decisions.jsonl"
PASS_B = SCREEN / "pass_b_decisions_v2.jsonl"
VERSION = "d14-fulltext-reconcile/1.0.0"


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def prepare() -> dict[str, Any]:
    if FINAL.exists():
        raise ValueError(f"immutable D14 full-text adjudication package exists: {FINAL}")
    manifest = verify_packet()
    valid_a = validate_pass(PASS_A, "pass-a")
    valid_b = validate_pass(PASS_B, "pass-b")
    packet: dict[str, dict[str, Any]] = {}
    for shard in manifest["shards"]:
        for row in _read(Path(shard["path"])):
            packet[row["family_id"]] = row
    pass_a = {row["family_id"]: row for row in _read(PASS_A)}
    pass_b = {row["family_id"]: row for row in _read(PASS_B)}
    if set(packet) != set(pass_a) or set(packet) != set(pass_b):
        raise ValueError("D14 full-text reconciliation population mismatch")

    pairs: Counter[str] = Counter()
    consensus: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    for family_id in sorted(packet):
        a, b = pass_a[family_id], pass_b[family_id]
        pairs[f"{a['decision']}|{b['decision']}"] += 1
        needs_adjudication = a["decision"] != b["decision"] or "unclear" in {a["decision"], b["decision"]}
        if needs_adjudication:
            candidates.append({
                "family": packet[family_id],
                "pass_a": a,
                "pass_b": b,
                "adjudication_reason": "disagreement" if a["decision"] != b["decision"] else "consensus_unclear",
            })
        else:
            consensus.append({
                "family_id": family_id,
                "record_id": packet[family_id]["record_id"],
                "final_fulltext_decision": a["decision"],
                "exclusion_code": a.get("exclusion_code"),
                "decision_basis": "agent_consensus_no_unclear",
            })

    FINAL.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="d14-ft-adjudication-", dir=str(FINAL.parent)))
    try:
        adjudication_path = staging / "adjudication_packet.jsonl"
        consensus_path = staging / "consensus_decisions.jsonl"
        adjudication_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in candidates), encoding="utf-8")
        consensus_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in consensus), encoding="utf-8")
        concordant = sum(pass_a[fid]["decision"] == pass_b[fid]["decision"] for fid in packet)
        result = {
            "status": "prepared_for_separate_fulltext_adjudication",
            "protocol_version": "1.3",
            "pipeline_version": VERSION,
            "family_count": len(packet),
            "pass_a": valid_a,
            "pass_b": valid_b,
            "agent_concordance_count": concordant,
            "agent_concordance_rate": concordant / len(packet),
            "decision_pair_counts": dict(sorted(pairs.items())),
            "consensus_without_unclear_count": len(consensus),
            "adjudication_candidate_count": len(candidates),
            "adjudication_packet_sha256": sha256(adjudication_path),
            "consensus_decisions_sha256": sha256(consensus_path),
            "interpretation_boundary": "AI-agent concordance only, not human inter-rater reliability; every disagreement or unclear decision requires separate adjudication.",
        }
        manifest_path = staging / "reconciliation_manifest.json"
        manifest_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (staging / "reconciliation_manifest.json.sha256").write_text(
            f"{sha256(manifest_path)}  reconciliation_manifest.json\n", encoding="ascii"
        )
        staging.rename(FINAL)
        return result
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def verify() -> dict[str, Any]:
    manifest_path = FINAL / "reconciliation_manifest.json"
    result = json.loads(manifest_path.read_text(encoding="utf-8"))
    if result["pass_a"] != validate_pass(PASS_A, "pass-a") or result["pass_b"] != validate_pass(PASS_B, "pass-b"):
        raise ValueError("D14 full-text reconciliation pass binding mismatch")
    if sha256(FINAL / "adjudication_packet.jsonl") != result["adjudication_packet_sha256"]:
        raise ValueError("D14 full-text adjudication packet checksum mismatch")
    if sha256(FINAL / "consensus_decisions.jsonl") != result["consensus_decisions_sha256"]:
        raise ValueError("D14 full-text consensus checksum mismatch")
    if result["consensus_without_unclear_count"] + result["adjudication_candidate_count"] != result["family_count"]:
        raise ValueError("D14 full-text reconciliation conservation failure")
    if (FINAL / "reconciliation_manifest.json.sha256").read_text().split()[0] != sha256(manifest_path):
        raise ValueError("D14 full-text reconciliation sidecar mismatch")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("prepare", "verify"))
    args = parser.parse_args()
    result = prepare() if args.command == "prepare" else verify()
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
