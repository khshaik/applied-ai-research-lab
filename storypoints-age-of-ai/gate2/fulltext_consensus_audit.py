"""Prepare and verify the D11 deterministic consensus-include quality audit."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from typing import Any
import re

from gate2.fulltext_reconcile import verify as verify_reconciliation
from gate2.fulltext_screening import OUTPUT, FullTextScreeningError, sha256


VERSION = "d11-consensus-include-audit/1.0.0"
CREATED_AT = "2026-08-17T02:10:00Z"
SAMPLE_SIZE = 100
SEED_LABEL = "protocol-v1.3|d11|consensus-include-quality-audit|v1"
ADJUDICATION = OUTPUT / "adjudication"
AUDIT = ADJUDICATION / "consensus_quality_audit"


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def prepare(output_dir: Path = AUDIT) -> dict[str, Any]:
    if output_dir.exists():
        raise FullTextScreeningError(f"immutable D11 consensus audit exists: {output_dir}")
    reconciliation = verify_reconciliation(ADJUDICATION)
    consensus = _read(ADJUDICATION / "consensus_decisions.jsonl")
    includes = [row for row in consensus if row["final_fulltext_decision"] == "include"]
    if len(includes) != reconciliation["decision_pair_counts"].get("include|include", 0):
        raise FullTextScreeningError("D11 consensus include population mismatch")
    packet_by_id: dict[str, dict[str, Any]] = {}
    manifest = json.loads((OUTPUT / "d11_packet_manifest.json").read_text(encoding="utf-8"))
    for shard in manifest["shards"]:
        for row in _read(OUTPUT / shard["path"]):
            packet_by_id[row["family_id"]] = row
    ranked = sorted(
        includes,
        key=lambda row: hashlib.sha256(f"{SEED_LABEL}|{row['family_id']}".encode()).hexdigest(),
    )
    selected = ranked[:SAMPLE_SIZE]
    rows = []
    for rank, decision in enumerate(selected, 1):
        family = packet_by_id[decision["family_id"]]
        rows.append({
            "audit_rank": rank,
            "selection_hash": hashlib.sha256(f"{SEED_LABEL}|{decision['family_id']}".encode()).hexdigest(),
            "family": family,
            "consensus_decision": decision,
            "audit_question": "Does the full text satisfy every applicable frozen inclusion criterion and avoid E1-E10, especially E2 and E10?",
        })
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="d11-consensus-audit-", dir=str(output_dir.parent)))
    try:
        packet = staging / "consensus_include_audit_packet.jsonl"
        packet.write_text("".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
        result = {
            "status": "prepared_deterministic_consensus_include_audit",
            "protocol_version": "1.3", "pipeline_version": VERSION,
            "created_at_utc": CREATED_AT, "seed_label": SEED_LABEL,
            "population_count": len(includes), "sample_size": len(rows),
            "selection_method": "ascending SHA-256(seed_label|family_id), first 100",
            "packet_sha256": sha256(packet),
            "trigger": "Both isolated passes produced a high inclusion rate and independently identified the breadth of I3 quality consequences as a methodological concern before D11 closure.",
            "decision_rule": "Any audited false inclusion is corrected through separate audit adjudication. If more than 5 of 100 are false inclusions, the complete consensus-include population requires separate re-review before D11 can close.",
            "security_boundary": "Local checksum-bound text only; no network, credentials, Git history, package installation, or executable PDF content.",
        }
        path = staging / "consensus_include_audit_manifest.json"
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (staging / "consensus_include_audit_manifest.json.sha256").write_text(
            f"{sha256(path)}  consensus_include_audit_manifest.json\n", encoding="utf-8"
        )
        staging.rename(output_dir)
        return result
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def verify(output_dir: Path = AUDIT) -> dict[str, Any]:
    path = output_dir / "consensus_include_audit_manifest.json"
    result = json.loads(path.read_text(encoding="utf-8"))
    packet = output_dir / "consensus_include_audit_packet.jsonl"
    if sha256(packet) != result["packet_sha256"]:
        raise FullTextScreeningError("D11 consensus audit packet hash mismatch")
    rows = _read(packet)
    if len(rows) != SAMPLE_SIZE or len({row["family"]["family_id"] for row in rows}) != SAMPLE_SIZE:
        raise FullTextScreeningError("D11 consensus audit sample identity/count mismatch")
    reranked = sorted(
        [row for row in _read(ADJUDICATION / "consensus_decisions.jsonl") if row["final_fulltext_decision"] == "include"],
        key=lambda row: hashlib.sha256(f"{SEED_LABEL}|{row['family_id']}".encode()).hexdigest(),
    )[:SAMPLE_SIZE]
    if [row["family"]["family_id"] for row in rows] != [row["family_id"] for row in reranked]:
        raise FullTextScreeningError("D11 consensus audit sample is not deterministic")
    if (output_dir / "consensus_include_audit_manifest.json.sha256").read_text().split()[0] != sha256(path):
        raise FullTextScreeningError("D11 consensus audit sidecar mismatch")
    return result


def validate_decisions(
    output_dir: Path = AUDIT,
    decisions_path: Path | None = None,
) -> dict[str, Any]:
    manifest = verify(output_dir)
    packet = _read(output_dir / "consensus_include_audit_packet.jsonl")
    expected = {row["family"]["family_id"]: row for row in packet}
    path = decisions_path or output_dir / "consensus_include_audit_decisions.jsonl"
    decisions = _read(path)
    seen: set[str] = set()
    counts = {"confirm_include": 0, "false_include": 0}
    exclusion_codes = {f"E{number}" for number in range(1, 11)}
    strata = {"peer_reviewed_scholarly", "preprint_scholarly", "grey_practitioner", "method_reference"}
    for row in decisions:
        family_id = row.get("family_id")
        if family_id not in expected or family_id in seen:
            raise FullTextScreeningError(f"unknown/duplicate D11 consensus-audit family: {family_id}")
        seen.add(family_id)
        source = expected[family_id]
        if row.get("record_id") != source["family"]["record_id"]:
            raise FullTextScreeningError(f"D11 consensus-audit record mismatch: {family_id}")
        if row.get("audit_rank") != source["audit_rank"] or row.get("selection_hash") != source["selection_hash"]:
            raise FullTextScreeningError(f"D11 consensus-audit sample binding mismatch: {family_id}")
        if row.get("input_checksum") != manifest["packet_sha256"]:
            raise FullTextScreeningError(f"D11 consensus-audit packet checksum mismatch: {family_id}")
        decision = row.get("decision")
        if decision not in counts:
            raise FullTextScreeningError(f"D11 consensus-audit decision invalid: {family_id}")
        code = row.get("exclusion_code")
        if decision == "false_include" and code not in exclusion_codes:
            raise FullTextScreeningError(f"D11 consensus false inclusion lacks E1-E10: {family_id}")
        if decision == "confirm_include" and code is not None:
            raise FullTextScreeningError(f"D11 confirmed include carries exclusion code: {family_id}")
        if not row.get("auditor_id") or not row.get("audit_context_id"):
            raise FullTextScreeningError(f"D11 consensus-audit provenance missing: {family_id}")
        if not row.get("rationale") or not row.get("control_check"):
            raise FullTextScreeningError(f"D11 consensus-audit rationale/control missing: {family_id}")
        if row.get("evidence_stratum") not in strata:
            raise FullTextScreeningError(f"D11 consensus-audit stratum invalid: {family_id}")
        if not re.search(r"\bpage(?:s)?\s+\d+", row.get("source_locator", ""), flags=re.I):
            raise FullTextScreeningError(f"D11 consensus-audit locator lacks page: {family_id}")
        counts[decision] += 1
    if seen != set(expected) or len(decisions) != manifest["sample_size"]:
        raise FullTextScreeningError("D11 consensus-audit decisions are incomplete")
    return {
        "status": "audit_pass" if counts["false_include"] <= 5 else "full_consensus_rereview_required",
        "sample_size": len(decisions), "decision_counts": counts,
        "false_inclusion_rate": counts["false_include"] / len(decisions),
        "threshold": "full re-review when false_include > 5 of 100",
        "sha256": sha256(path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("prepare", "verify", "validate-decisions"))
    args = parser.parse_args()
    result = prepare() if args.command == "prepare" else verify() if args.command == "verify" else validate_decisions()
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
