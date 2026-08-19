"""Reconcile two isolated passes for the 33 newly resolved D14 candidates."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import tempfile
from typing import Any

from gate2.citation_chasing import OUTPUT, sha256
from gate2.d14_new_candidate_screening import FINAL as SCREEN, validate_pass, verify_packet


FINAL = SCREEN / "adjudication"
VERSION = "d14-new-screening-reconcile/1.0.0"
PASS_A = SCREEN / "pass_a_decisions.jsonl"
PASS_B = SCREEN / "pass_b_decisions.jsonl"


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def prepare() -> dict[str, Any]:
    if FINAL.exists():
        raise ValueError(f"immutable D14 new-screening adjudication package exists: {FINAL}")
    manifest = verify_packet(); valid_a = validate_pass(PASS_A, "pass-a"); valid_b = validate_pass(PASS_B, "pass-b")
    packet = {row["family_id"]: row for row in _read(Path(manifest["packet_path"]))}
    pass_a = {row["family_id"]: row for row in _read(PASS_A)}; pass_b = {row["family_id"]: row for row in _read(PASS_B)}
    if set(packet) != set(pass_a) or set(packet) != set(pass_b):
        raise ValueError("D14 new-screening reconciliation population mismatch")
    consensus: list[dict[str, Any]] = []; candidates: list[dict[str, Any]] = []; pairs: Counter[str] = Counter()
    for family_id in sorted(packet):
        a, b = pass_a[family_id], pass_b[family_id]; pairs[f"{a['decision']}|{b['decision']}"] += 1
        if a["decision"] == b["decision"] and a["decision"] != "unclear":
            consensus.append({"family_id": family_id, "record_id": family_id, "final_title_abstract_decision": a["decision"], "decision_basis": "agent_consensus_no_unclear", "reason": a["reason"]})
        else:
            candidates.append({"family": packet[family_id], "pass_a": a, "pass_b": b, "adjudication_reason": "disagreement" if a["decision"] != b["decision"] else "consensus_unclear"})
    FINAL.parent.mkdir(parents=True, exist_ok=True); staging = Path(tempfile.mkdtemp(prefix="d14-new-adj-", dir=str(FINAL.parent)))
    try:
        packet_path = staging / "adjudication_packet.jsonl"; consensus_path = staging / "consensus_decisions.jsonl"
        packet_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in candidates), encoding="utf-8")
        consensus_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in consensus), encoding="utf-8")
        result = {"status": "prepared_for_separate_adjudication", "protocol_version": "1.3", "pipeline_version": VERSION, "family_count": 33,
                  "pass_a": valid_a, "pass_b": valid_b, "decision_pair_counts": dict(sorted(pairs.items())),
                  "agent_concordance_count": sum(pass_a[fid]["decision"] == pass_b[fid]["decision"] for fid in packet),
                  "consensus_without_unclear_count": len(consensus), "adjudication_candidate_count": len(candidates),
                  "adjudication_packet_sha256": sha256(packet_path), "consensus_decisions_sha256": sha256(consensus_path),
                  "interpretation_boundary": "AI-agent concordance only, not human inter-rater reliability; every disagreement or unclear decision requires separate adjudication."}
        manifest_path = staging / "reconciliation_manifest.json"; manifest_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (staging / "reconciliation_manifest.json.sha256").write_text(f"{sha256(manifest_path)}  reconciliation_manifest.json\n", encoding="ascii")
        staging.rename(FINAL); return result
    except Exception:
        shutil.rmtree(staging, ignore_errors=True); raise


def verify() -> dict[str, Any]:
    path = FINAL / "reconciliation_manifest.json"; result = json.loads(path.read_text(encoding="utf-8"))
    if result["pass_a"] != validate_pass(PASS_A, "pass-a") or result["pass_b"] != validate_pass(PASS_B, "pass-b"):
        raise ValueError("D14 new-screening pass binding mismatch")
    if sha256(FINAL / "adjudication_packet.jsonl") != result["adjudication_packet_sha256"] or sha256(FINAL / "consensus_decisions.jsonl") != result["consensus_decisions_sha256"]:
        raise ValueError("D14 new-screening reconciliation checksum mismatch")
    if result["consensus_without_unclear_count"] + result["adjudication_candidate_count"] != 33:
        raise ValueError("D14 new-screening reconciliation conservation failure")
    if (FINAL / "reconciliation_manifest.json.sha256").read_text().split()[0] != sha256(path):
        raise ValueError("D14 new-screening reconciliation sidecar mismatch")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("prepare", "verify")); args = parser.parse_args()
    print(json.dumps(prepare() if args.command == "prepare" else verify(), sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
