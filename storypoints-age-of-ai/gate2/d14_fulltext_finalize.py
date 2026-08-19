"""Validate adjudication and publish the conserved D14 full-text ledger."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import tempfile
from typing import Any

from gate2.citation_chasing import OUTPUT, sha256
from gate2.d14_fulltext_dispositions import FINAL as DISPOSITIONS, verify as verify_dispositions
from gate2.d14_fulltext_reconcile import FINAL as ADJUDICATION, verify as verify_reconciliation


FINAL = OUTPUT / "fulltext_final"
VERSION = "d14-fulltext-finalize/1.0.0"
EXCLUSIONS = {f"E{index}" for index in range(1, 11)}


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def validate_adjudication(path: Path = ADJUDICATION / "adjudicated_decisions.jsonl") -> dict[str, Any]:
    reconciliation = verify_reconciliation()
    packet = _read(ADJUDICATION / "adjudication_packet.jsonl")
    expected = {row["family"]["family_id"]: row for row in packet}
    rows = _read(path)
    seen: set[str] = set()
    contexts: set[str] = set()
    counts: Counter[str] = Counter()
    for row in rows:
        family_id = row.get("family_id")
        if family_id not in expected or family_id in seen:
            raise ValueError("unknown or duplicate D14 full-text adjudication")
        seen.add(family_id)
        context = row.get("adjudication_context_id")
        if not isinstance(context, str) or not context.startswith("d14-ft-adjudicator-") or context in contexts:
            raise ValueError("D14 full-text adjudicator context invalid")
        contexts.add(context)
        decision = row.get("final_fulltext_decision")
        code = row.get("exclusion_code")
        if decision not in {"include", "exclude"}:
            raise ValueError("D14 full-text adjudication decision invalid")
        if (decision == "exclude" and code not in EXCLUSIONS) or (decision == "include" and code is not None):
            raise ValueError("D14 full-text adjudication exclusion code invalid")
        if row.get("record_id") != expected[family_id]["family"]["record_id"] or row.get("stage") != "full_text":
            raise ValueError("D14 full-text adjudication identity mismatch")
        if row.get("decision_basis") != "separate_ai_adjudication" or row.get("adjudicator_type") != "ai_agent" or row.get("adjudicator_id") != "d14-fulltext-adjudicator-v1":
            raise ValueError("D14 full-text adjudicator provenance mismatch")
        if row.get("input_checksum") != reconciliation["adjudication_packet_sha256"] or row.get("prior_synthesis_visible") is not False:
            raise ValueError("D14 full-text adjudication input/blinding mismatch")
        if not row.get("reason") or not row.get("source_locator") or len(row.get("independence_attestation", "")) < 30:
            raise ValueError("D14 full-text adjudication support incomplete")
        confidence = row.get("confidence")
        if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            raise ValueError("D14 full-text adjudication confidence invalid")
        counts[decision] += 1
    if seen != set(expected):
        raise ValueError(f"D14 full-text adjudication incomplete: {len(set(expected) - seen)} missing")
    sidecar = path.with_suffix(path.suffix + ".sha256")
    if not sidecar.exists() or sidecar.read_text().split()[0] != sha256(path):
        raise ValueError("D14 full-text adjudication sidecar mismatch")
    return {"status": "valid_complete_fulltext_adjudication", "family_count": len(rows), "decision_counts": dict(counts), "sha256": sha256(path)}


def finalize() -> dict[str, Any]:
    if FINAL.exists():
        raise ValueError(f"immutable D14 full-text final ledger exists: {FINAL}")
    dispositions_manifest = verify_dispositions()
    reconciliation = verify_reconciliation()
    adjudication = validate_adjudication()
    dispositions = {row["citation_family_id"]: row for row in _read(DISPOSITIONS / "fulltext_dispositions.jsonl")}
    consensus = _read(ADJUDICATION / "consensus_decisions.jsonl")
    adjudicated = _read(ADJUDICATION / "adjudicated_decisions.jsonl")
    screened: dict[str, dict[str, Any]] = {}
    for row in consensus:
        screened[row["family_id"]] = {
            "final_fulltext_decision": row["final_fulltext_decision"],
            "exclusion_code": row.get("exclusion_code"),
            "decision_basis": row["decision_basis"],
            "decision_reason": None,
        }
    for row in adjudicated:
        if row["family_id"] in screened:
            raise ValueError("D14 full-text consensus/adjudication overlap")
        screened[row["family_id"]] = {
            "final_fulltext_decision": row["final_fulltext_decision"],
            "exclusion_code": row.get("exclusion_code"),
            "decision_basis": row["decision_basis"],
            "decision_reason": row["reason"],
        }
    if len(screened) != 337:
        raise ValueError("D14 full-text screened population mismatch")

    rows: list[dict[str, Any]] = []
    for family_id in sorted(dispositions):
        disposition = dispositions[family_id]
        decision = screened.get(family_id)
        if disposition["eligible_for_fulltext_screening"] != (decision is not None):
            raise ValueError("D14 full-text availability/screening reconciliation failure")
        rows.append({
            "citation_family_id": family_id,
            "title": disposition["title"],
            "doi": disposition["doi"],
            "arxiv_id": disposition["arxiv_id"],
            "availability_disposition": disposition["fulltext_disposition"],
            "fulltext_assessment_status": "assessed" if decision else "unavailable_not_assessed",
            "final_fulltext_decision": decision["final_fulltext_decision"] if decision else None,
            "exclusion_code": decision["exclusion_code"] if decision else None,
            "decision_basis": decision["decision_basis"] if decision else "lawful_fulltext_unavailable",
            "decision_reason": decision["decision_reason"] if decision else disposition["fulltext_disposition"],
        })
    if len(rows) != 1017 or len({row["citation_family_id"] for row in rows}) != 1017:
        raise ValueError("D14 full-text final population conservation failure")

    FINAL.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="d14-fulltext-final-", dir=str(FINAL.parent)))
    try:
        ledger_path = staging / "final_fulltext_ledger.jsonl"
        ledger_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
        decision_counts = Counter(row["final_fulltext_decision"] or "unavailable_not_assessed" for row in rows)
        result = {
            "status": "d14_fulltext_assessment_complete",
            "protocol_version": "1.3",
            "pipeline_version": VERSION,
            "family_count": len(rows),
            "screened_family_count": len(screened),
            "unavailable_family_count": len(rows) - len(screened),
            "decision_counts": dict(sorted(decision_counts.items())),
            "disposition_manifest_sha256": sha256(DISPOSITIONS / "disposition_manifest.json"),
            "reconciliation_manifest_sha256": sha256(ADJUDICATION / "reconciliation_manifest.json"),
            "adjudication": adjudication,
            "final_ledger_sha256": sha256(ledger_path),
            "interpretation_boundary": "Unavailable full text is an availability outcome, not an eligibility exclusion, quality judgment, or novelty finding.",
        }
        manifest_path = staging / "final_fulltext_manifest.json"
        manifest_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (staging / "final_fulltext_manifest.json.sha256").write_text(
            f"{sha256(manifest_path)}  final_fulltext_manifest.json\n", encoding="ascii"
        )
        staging.rename(FINAL)
        return result
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def verify() -> dict[str, Any]:
    manifest_path = FINAL / "final_fulltext_manifest.json"
    result = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = _read(FINAL / "final_fulltext_ledger.jsonl")
    if len(rows) != result["family_count"] or sha256(FINAL / "final_fulltext_ledger.jsonl") != result["final_ledger_sha256"]:
        raise ValueError("D14 full-text final ledger mismatch")
    if result["adjudication"] != validate_adjudication():
        raise ValueError("D14 full-text final adjudication binding mismatch")
    if Counter(row["final_fulltext_decision"] or "unavailable_not_assessed" for row in rows) != Counter(result["decision_counts"]):
        raise ValueError("D14 full-text final decision counts mismatch")
    if (FINAL / "final_fulltext_manifest.json.sha256").read_text().split()[0] != sha256(manifest_path):
        raise ValueError("D14 full-text final manifest sidecar mismatch")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("validate-adjudication", "finalize", "verify"))
    args = parser.parse_args()
    result = validate_adjudication() if args.command == "validate-adjudication" else finalize() if args.command == "finalize" else verify()
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
