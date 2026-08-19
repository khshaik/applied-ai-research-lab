"""Reconcile D11 isolated full-text passes and prepare adjudication."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import tempfile
from typing import Any

from gate2.fulltext_screening import OUTPUT, FullTextScreeningError, sha256, validate_pass, verify_packet


VERSION = "d11-fulltext-reconcile/1.0.0"
CREATED_AT = "2026-08-17T01:00:00Z"


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def prepare(output_dir: Path = OUTPUT / "adjudication") -> dict[str, Any]:
    if output_dir.exists():
        raise FullTextScreeningError(f"immutable D11 adjudication packet exists: {output_dir}")
    pass_a_path = OUTPUT / "pass_a_fulltext_decisions.jsonl"
    pass_b_path = OUTPUT / "pass_b_fulltext_decisions.jsonl"
    valid_a = validate_pass(pass_a_path, "pass-a")
    valid_b = validate_pass(pass_b_path, "pass-b")
    manifest = verify_packet()
    pass_a = {row["family_id"]: row for row in _read(pass_a_path)}
    pass_b = {row["family_id"]: row for row in _read(pass_b_path)}
    packet = {}
    for shard in manifest["shards"]:
        for row in _read(OUTPUT / shard["path"]):
            packet[row["family_id"]] = row
    candidates, consensus = [], []
    pairs = Counter()
    for family_id in sorted(packet):
        a, b = pass_a[family_id], pass_b[family_id]
        pairs[f"{a['decision']}|{b['decision']}"] += 1
        needs = a["decision"] != b["decision"] or "unclear" in {a["decision"], b["decision"]}
        if needs:
            candidates.append({"family": packet[family_id], "pass_a": a, "pass_b": b,
                               "adjudication_reason": "disagreement" if a["decision"] != b["decision"] else "consensus_unclear"})
        else:
            consensus.append({"family_id": family_id, "record_id": a["record_id"],
                              "final_fulltext_decision": a["decision"],
                              "exclusion_code": a.get("exclusion_code"),
                              "decision_basis": "agent_consensus_no_unclear"})
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="d11-adj-", dir=str(output_dir.parent)))
    try:
        candidates_path = staging / "adjudication_packet.jsonl"
        candidates_path.write_text("".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in candidates), encoding="utf-8")
        consensus_path = staging / "consensus_decisions.jsonl"
        consensus_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in consensus), encoding="utf-8")
        concordant = sum(a["decision"] == pass_b[fid]["decision"] for fid, a in pass_a.items())
        result = {"status": "prepared_for_separate_fulltext_adjudication", "protocol_version": "1.3",
                  "pipeline_version": VERSION, "created_at_utc": CREATED_AT,
                  "assessed_family_count": len(packet), "pass_a": valid_a, "pass_b": valid_b,
                  "agent_concordance_count": concordant, "agent_concordance_rate": concordant / len(packet),
                  "decision_pair_counts": dict(sorted(pairs.items())),
                  "consensus_without_unclear_count": len(consensus),
                  "adjudication_candidate_count": len(candidates),
                  "adjudication_packet_sha256": sha256(candidates_path),
                  "consensus_sha256": sha256(consensus_path),
                  "interpretation_boundary": "AI-agent concordance only, not human inter-rater reliability. Every disagreement or unclear decision requires separate adjudication."}
        result_path = staging / "d11_reconciliation_manifest.json"
        result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (staging / "d11_reconciliation_manifest.json.sha256").write_text(f"{sha256(result_path)}  d11_reconciliation_manifest.json\n", encoding="utf-8")
        staging.rename(output_dir)
        return result
    except Exception:
        shutil.rmtree(staging, ignore_errors=True); raise


def verify(output_dir: Path = OUTPUT / "adjudication") -> dict[str, Any]:
    path = output_dir / "d11_reconciliation_manifest.json"
    row = json.loads(path.read_text(encoding="utf-8"))
    if row["pass_a"] != validate_pass(OUTPUT / "pass_a_fulltext_decisions.jsonl", "pass-a"):
        raise FullTextScreeningError("D11 reconciliation no longer binds pass A")
    if row["pass_b"] != validate_pass(OUTPUT / "pass_b_fulltext_decisions.jsonl", "pass-b"):
        raise FullTextScreeningError("D11 reconciliation no longer binds pass B")
    if sha256(output_dir / "adjudication_packet.jsonl") != row["adjudication_packet_sha256"]:
        raise FullTextScreeningError("D11 adjudication packet mismatch")
    if sha256(output_dir / "consensus_decisions.jsonl") != row["consensus_sha256"]:
        raise FullTextScreeningError("D11 consensus mismatch")
    if row["consensus_without_unclear_count"] + row["adjudication_candidate_count"] != row["assessed_family_count"]:
        raise FullTextScreeningError("D11 reconciliation conservation failed")
    if (output_dir / "d11_reconciliation_manifest.json.sha256").read_text().split()[0] != sha256(path):
        raise FullTextScreeningError("D11 reconciliation sidecar mismatch")
    return row


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("prepare", "verify")); args = parser.parse_args()
    result = prepare() if args.command == "prepare" else verify()
    print(json.dumps(result, sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
