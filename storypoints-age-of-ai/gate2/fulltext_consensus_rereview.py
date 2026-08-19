"""Validate the required D11 re-review of every consensus inclusion."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
from typing import Any

from gate2.fulltext_consensus_audit import validate_decisions as validate_audit
from gate2.fulltext_reconcile import verify as verify_reconciliation
from gate2.fulltext_screening import (
    EXCLUSION_CODES,
    OUTPUT,
    STRATA,
    FullTextScreeningError,
    sha256,
    verify_packet,
)


ADJUDICATION = OUTPUT / "adjudication"
PATH = ADJUDICATION / "consensus_rereview_decisions.jsonl"


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def validate(path: Path = PATH) -> dict[str, Any]:
    audit = validate_audit()
    if audit["status"] != "full_consensus_rereview_required":
        raise FullTextScreeningError("D11 full consensus re-review was not triggered")
    reconciliation = verify_reconciliation(ADJUDICATION)
    packet_manifest = verify_packet()
    packet: dict[str, tuple[dict[str, Any], str]] = {}
    for shard in packet_manifest["shards"]:
        for row in _read(OUTPUT / shard["path"]):
            packet[row["family_id"]] = (row, shard["sha256"])
    consensus = _read(ADJUDICATION / "consensus_decisions.jsonl")
    expected = {
        row["family_id"]: row
        for row in consensus
        if row["final_fulltext_decision"] == "include"
    }
    if len(expected) != reconciliation["decision_pair_counts"].get("include|include", 0):
        raise FullTextScreeningError("D11 consensus re-review population mismatch")
    rows = _read(path)
    seen: set[str] = set()
    counts: Counter[str] = Counter()
    for row in rows:
        family_id = row.get("family_id")
        if family_id not in expected or family_id in seen:
            raise FullTextScreeningError(f"unknown/duplicate D11 re-review family: {family_id}")
        seen.add(family_id)
        source, checksum = packet[family_id]
        if row.get("record_id") != source["record_id"] or row.get("stage") != "full_text":
            raise FullTextScreeningError(f"D11 re-review identity/stage mismatch: {family_id}")
        if row.get("input_checksum") != checksum:
            raise FullTextScreeningError(f"D11 re-review checksum mismatch: {family_id}")
        if row.get("reviewer_id") != "d11-consensus-rereviewer-v1" or not row.get("review_context_id"):
            raise FullTextScreeningError(f"D11 re-review provenance invalid: {family_id}")
        decision = row.get("decision")
        if decision not in {"include", "exclude"}:
            raise FullTextScreeningError(f"D11 re-review decision invalid: {family_id}")
        code = row.get("exclusion_code")
        if decision == "exclude" and code not in EXCLUSION_CODES:
            raise FullTextScreeningError(f"D11 re-review exclusion lacks E1-E10: {family_id}")
        if decision == "include" and code is not None:
            raise FullTextScreeningError(f"D11 re-review include carries exclusion code: {family_id}")
        if row.get("evidence_stratum") not in STRATA or not row.get("reason") or not row.get("control_check"):
            raise FullTextScreeningError(f"D11 re-review evidence/provenance missing: {family_id}")
        if not re.search(r"\bpage(?:s)?\s+\d+", row.get("source_locator", ""), flags=re.I):
            raise FullTextScreeningError(f"D11 re-review locator lacks page: {family_id}")
        confidence = row.get("confidence")
        if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            raise FullTextScreeningError(f"D11 re-review confidence invalid: {family_id}")
        counts[decision] += 1
    if seen != set(expected):
        raise FullTextScreeningError(f"D11 consensus re-review incomplete: missing {len(set(expected) - seen)}")
    return {
        "status": "valid_complete_consensus_include_rereview",
        "family_count": len(rows), "decision_counts": dict(sorted(counts.items())),
        "sha256": sha256(path), "trigger_audit": audit,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("validate",))
    parser.parse_args()
    print(json.dumps(validate(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
