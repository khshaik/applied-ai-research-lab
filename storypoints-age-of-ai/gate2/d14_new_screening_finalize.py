"""Validate four-case adjudication and finalize newly resolved D14 screening."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import tempfile
from typing import Any

from gate2.citation_chasing import OUTPUT, sha256
from gate2.d14_new_screening_reconcile import FINAL as ADJUDICATION, verify as verify_reconciliation


FINAL = OUTPUT / "newly_resolved_candidate_screening_final_v2"
VERSION = "d14-new-screening-finalize/1.0.0"
CODES = {"E1", "E2", "E3", "E4", "E9", "E10"}


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def validate_adjudication(path: Path = ADJUDICATION / "adjudicated_decisions.jsonl") -> dict[str, Any]:
    reconciliation = verify_reconciliation(); packet = _read(ADJUDICATION / "adjudication_packet.jsonl")
    expected = {row["family"]["family_id"]: row["family"] for row in packet}; rows = _read(path); seen: set[str] = set(); contexts: set[str] = set(); counts: Counter[str] = Counter()
    for row in rows:
        family_id = row.get("family_id")
        if family_id not in expected or family_id in seen:
            raise ValueError("unknown or duplicate D14 new-screening adjudication")
        seen.add(family_id); context = row.get("adjudication_context_id")
        if not isinstance(context, str) or not context.startswith("d14-new-adjudicator-") or context in contexts:
            raise ValueError("D14 new-screening adjudicator context invalid")
        contexts.add(context); decision = row.get("final_title_abstract_decision"); code = row.get("exclusion_code")
        if decision not in {"include", "exclude"} or (decision == "exclude" and code not in CODES) or (decision == "include" and code is not None):
            raise ValueError("D14 new-screening adjudication decision/code invalid")
        if row.get("record_id") != expected[family_id]["record_id"] or row.get("stage") != "title_abstract":
            raise ValueError("D14 new-screening adjudication identity invalid")
        if row.get("decision_basis") != "separate_ai_adjudication" or row.get("adjudicator_type") != "ai_agent" or row.get("adjudicator_id") != "d14-new-adjudicator-v1":
            raise ValueError("D14 new-screening adjudicator provenance invalid")
        if row.get("input_checksum") != reconciliation["adjudication_packet_sha256"] or row.get("prior_fulltext_or_synthesis_visible") is not False:
            raise ValueError("D14 new-screening adjudicator binding/blinding invalid")
        if not row.get("reason") or not row.get("source_locator") or len(row.get("independence_attestation", "")) < 30:
            raise ValueError("D14 new-screening adjudication support incomplete")
        if not isinstance(row.get("confidence"), (int, float)) or not 0 <= row["confidence"] <= 1:
            raise ValueError("D14 new-screening adjudication confidence invalid")
        counts[decision] += 1
    if seen != set(expected):
        raise ValueError(f"D14 new-screening adjudication incomplete: {len(set(expected) - seen)} missing")
    sidecar = path.with_suffix(path.suffix + ".sha256")
    if not sidecar.exists() or sidecar.read_text().split()[0] != sha256(path):
        raise ValueError("D14 new-screening adjudication sidecar mismatch")
    return {"status": "valid_complete_adjudication", "family_count": len(rows), "decision_counts": dict(counts), "sha256": sha256(path)}


def finalize() -> dict[str, Any]:
    if FINAL.exists():
        raise ValueError(f"immutable D14 new-screening final exists: {FINAL}")
    reconciliation = verify_reconciliation(); adjudication = validate_adjudication()
    consensus = _read(ADJUDICATION / "consensus_decisions.jsonl"); adjudicated = _read(ADJUDICATION / "adjudicated_decisions.jsonl")
    rows = [{**row, "exclusion_code": None} for row in consensus]
    rows += [{"family_id": row["family_id"], "record_id": row["record_id"], "final_title_abstract_decision": row["final_title_abstract_decision"], "decision_basis": row["decision_basis"], "reason": row["reason"], "exclusion_code": row.get("exclusion_code")} for row in adjudicated]
    rows.sort(key=lambda row: row["family_id"])
    if len(rows) != 33 or len({row["family_id"] for row in rows}) != 33:
        raise ValueError("D14 new-screening final population mismatch")
    FINAL.parent.mkdir(parents=True, exist_ok=True); staging = Path(tempfile.mkdtemp(prefix="d14-new-screen-final-", dir=str(FINAL.parent)))
    try:
        ledger_path = staging / "final_screening_ledger.jsonl"; ledger_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
        counts = Counter(row["final_title_abstract_decision"] for row in rows)
        manifest = {"status": "d14_new_candidate_screening_complete", "protocol_version": "1.3", "pipeline_version": VERSION, "family_count": 33,
                    "decision_counts": dict(counts), "consensus_count": len(consensus), "adjudicated_count": len(adjudicated),
                    "reconciliation_manifest_sha256": sha256(ADJUDICATION / "reconciliation_manifest.json"), "adjudication": adjudication,
                    "final_ledger_sha256": sha256(ledger_path), "interpretation_boundary": "Title/abstract inclusion requires lawful full-text assessment before evidence inclusion."}
        manifest_path = staging / "final_screening_manifest.json"; manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (staging / "final_screening_manifest.json.sha256").write_text(f"{sha256(manifest_path)}  final_screening_manifest.json\n", encoding="ascii")
        staging.rename(FINAL); return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True); raise


def verify() -> dict[str, Any]:
    path = FINAL / "final_screening_manifest.json"; manifest = json.loads(path.read_text(encoding="utf-8")); rows = _read(FINAL / "final_screening_ledger.jsonl")
    if len(rows) != 33 or sha256(FINAL / "final_screening_ledger.jsonl") != manifest["final_ledger_sha256"] or manifest["adjudication"] != validate_adjudication():
        raise ValueError("D14 new-screening final binding mismatch")
    if (FINAL / "final_screening_manifest.json.sha256").read_text().split()[0] != sha256(path):
        raise ValueError("D14 new-screening final sidecar mismatch")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("validate-adjudication", "finalize", "verify")); args = parser.parse_args()
    result = validate_adjudication() if args.command == "validate-adjudication" else finalize() if args.command == "finalize" else verify()
    print(json.dumps(result, sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
