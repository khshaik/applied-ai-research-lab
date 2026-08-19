"""Validate D11 adjudication and publish the conserved eligibility ledger."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import shutil
import tempfile
from typing import Any

from gate2.fulltext_reconcile import verify as verify_reconciliation
from gate2.fulltext_consensus_rereview import validate as validate_consensus_rereview
from gate2.fulltext_screening import (
    EXCLUSION_CODES,
    OUTPUT,
    STRATA,
    FullTextScreeningError,
    sha256,
    verify_packet,
)


VERSION = "d11-fulltext-finalizer/1.0.0"
CREATED_AT = "2026-08-17T02:00:00Z"
ADJUDICATION = OUTPUT / "adjudication"
FINAL = OUTPUT / "final"


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def validate_adjudication(path: Path = ADJUDICATION / "adjudicated_decisions.jsonl") -> dict[str, Any]:
    reconciliation = verify_reconciliation(ADJUDICATION)
    packet_rows = _read(ADJUDICATION / "adjudication_packet.jsonl")
    expected = {row["family"]["family_id"]: row for row in packet_rows}
    rows = _read(path)
    seen: set[str] = set()
    counts: Counter[str] = Counter()
    for row in rows:
        family_id = row.get("family_id")
        if family_id not in expected or family_id in seen:
            raise FullTextScreeningError(f"unknown/duplicate D11 adjudication family: {family_id}")
        seen.add(family_id)
        source = expected[family_id]
        family = source["family"]
        pass_a, pass_b = source["pass_a"], source["pass_b"]
        if row.get("record_id") != family["record_id"] or row.get("stage") != "full_text":
            raise FullTextScreeningError(f"D11 adjudication identity/stage mismatch: {family_id}")
        if pass_a["input_checksum"] != pass_b["input_checksum"]:
            raise FullTextScreeningError(f"D11 source passes do not share input: {family_id}")
        if row.get("input_checksum") != pass_a["input_checksum"]:
            raise FullTextScreeningError(f"D11 adjudication checksum mismatch: {family_id}")
        if row.get("adjudicator_id") in {pass_a["reviewer_id"], pass_b["reviewer_id"], None, ""}:
            raise FullTextScreeningError(f"D11 adjudicator is not separate: {family_id}")
        if row.get("review_context_id") in {pass_a["review_context_id"], pass_b["review_context_id"], None, ""}:
            raise FullTextScreeningError(f"D11 adjudication context is not separate: {family_id}")
        decision = row.get("decision")
        if decision not in {"include", "exclude"}:
            raise FullTextScreeningError(f"D11 adjudication remains unresolved: {family_id}")
        code = row.get("exclusion_code")
        if decision == "exclude" and code not in EXCLUSION_CODES:
            raise FullTextScreeningError(f"D11 adjudicated exclusion lacks E1-E10: {family_id}")
        if decision == "include" and code is not None:
            raise FullTextScreeningError(f"D11 adjudicated include carries exclusion code: {family_id}")
        if row.get("evidence_stratum") not in STRATA:
            raise FullTextScreeningError(f"D11 adjudication stratum invalid: {family_id}")
        if not row.get("rationale") or not row.get("control_check"):
            raise FullTextScreeningError(f"D11 adjudication rationale/control missing: {family_id}")
        if not re.search(r"\bpage(?:s)?\s+\d+", row.get("source_locator", ""), flags=re.I):
            raise FullTextScreeningError(f"D11 adjudication locator lacks page: {family_id}")
        counts[decision] += 1
    if seen != set(expected):
        raise FullTextScreeningError(f"D11 adjudication incomplete: missing {len(set(expected) - seen)}")
    if len(rows) != reconciliation["adjudication_candidate_count"]:
        raise FullTextScreeningError("D11 adjudication count does not reconcile")
    return {
        "status": "valid_complete_separate_fulltext_adjudication",
        "family_count": len(rows),
        "decision_counts": dict(sorted(counts.items())),
        "sha256": sha256(path),
    }


def finalize(output_dir: Path = FINAL) -> dict[str, Any]:
    if output_dir.exists():
        raise FullTextScreeningError(f"immutable D11 final output exists: {output_dir}")
    packet_manifest = verify_packet()
    reconciliation = verify_reconciliation(ADJUDICATION)
    adjudication_path = ADJUDICATION / "adjudicated_decisions.jsonl"
    adjudication_validation = validate_adjudication(adjudication_path)
    rows: list[dict[str, Any]] = []
    for row in _read(ADJUDICATION / "consensus_decisions.jsonl"):
        if row["final_fulltext_decision"] != "exclude":
            continue
        rows.append({
            "family_id": row["family_id"], "record_id": row["record_id"],
            "final_status": "excluded_full_text", "decision": "exclude",
            "exclusion_code": row.get("exclusion_code"),
            "decision_basis": "two_agent_consensus_exclusion", "retrieval_status": "retrieved_open",
        })
    consensus_rereview_validation = validate_consensus_rereview()
    for row in _read(ADJUDICATION / "consensus_rereview_decisions.jsonl"):
        decision = row["decision"]
        rows.append({
            "family_id": row["family_id"], "record_id": row["record_id"],
            "final_status": "included_full_text" if decision == "include" else "excluded_full_text",
            "decision": decision, "exclusion_code": row.get("exclusion_code"),
            "decision_basis": "triggered_strict_consensus_rereview", "retrieval_status": "retrieved_open",
            "source_locator": row["source_locator"], "rationale": row["reason"],
        })
    for row in _read(adjudication_path):
        decision = row["decision"]
        rows.append({
            "family_id": row["family_id"], "record_id": row["record_id"],
            "final_status": "included_full_text" if decision == "include" else "excluded_full_text",
            "decision": decision, "exclusion_code": row.get("exclusion_code"),
            "decision_basis": "separate_agent_adjudication", "retrieval_status": "retrieved_open",
            "source_locator": row["source_locator"], "rationale": row["rationale"],
        })
    for row in _read(OUTPUT / "unavailable_fulltexts.jsonl"):
        rows.append({
            "family_id": row["family_id"], "record_id": row["record_id"],
            "final_status": "full_text_unavailable", "decision": "unavailable",
            "exclusion_code": row.get("exclusion_code"), "decision_basis": row["reason"],
            "retrieval_status": row["retrieval_status"],
        })
    rows.sort(key=lambda row: row["family_id"])
    family_ids = [row["family_id"] for row in rows]
    if len(rows) != packet_manifest["total_family_count"] or len(set(family_ids)) != len(rows):
        raise FullTextScreeningError("D11 final family conservation/uniqueness failed")
    status_counts = Counter(row["final_status"] for row in rows)
    if status_counts["full_text_unavailable"] != packet_manifest["unavailable_family_count"]:
        raise FullTextScreeningError("D11 unavailable population changed")
    exclusion_counts = Counter(row["exclusion_code"] for row in rows if row["final_status"] == "excluded_full_text")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="d11-final-", dir=str(output_dir.parent)))
    try:
        ledger = staging / "fulltext_eligibility_decisions.jsonl"
        _write_jsonl(ledger, rows)
        manifest = {
            "status": "d11_fulltext_eligibility_complete",
            "protocol_version": "1.3", "pipeline_version": VERSION,
            "created_at_utc": CREATED_AT,
            "input_packet_manifest_sha256": sha256(OUTPUT / "d11_packet_manifest.json"),
            "input_reconciliation_manifest_sha256": sha256(ADJUDICATION / "d11_reconciliation_manifest.json"),
            "adjudication_validation": adjudication_validation,
            "consensus_rereview_validation": consensus_rereview_validation,
            "total_family_count": len(rows),
            "status_counts": dict(sorted(status_counts.items())),
            "fulltext_exclusion_code_counts": {str(key): value for key, value in sorted(exclusion_counts.items())},
            "ledger_sha256": sha256(ledger),
            "conservation_equation": "included_full_text + excluded_full_text + full_text_unavailable = 2076",
            "interpretation_boundary": "AI-assisted full-text eligibility decisions; agent agreement is not human inter-rater reliability. Unavailable reports do not contribute substantive evidence.",
            "security_boundary": "Local checksum-bound extracted text only; no network, credentials, Git history, package installation, or executable PDF content.",
        }
        path = staging / "d11_final_manifest.json"
        path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (staging / "d11_final_manifest.json.sha256").write_text(
            f"{sha256(path)}  d11_final_manifest.json\n", encoding="utf-8"
        )
        staging.rename(output_dir)
        return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def verify(output_dir: Path = FINAL) -> dict[str, Any]:
    path = output_dir / "d11_final_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest["adjudication_validation"] != validate_adjudication():
        raise FullTextScreeningError("D11 final no longer binds adjudication")
    if manifest["consensus_rereview_validation"] != validate_consensus_rereview():
        raise FullTextScreeningError("D11 final no longer binds consensus re-review")
    ledger = output_dir / "fulltext_eligibility_decisions.jsonl"
    if sha256(ledger) != manifest["ledger_sha256"]:
        raise FullTextScreeningError("D11 final ledger hash mismatch")
    rows = _read(ledger)
    if len(rows) != manifest["total_family_count"] or len({row["family_id"] for row in rows}) != len(rows):
        raise FullTextScreeningError("D11 final ledger conservation failed")
    if Counter(row["final_status"] for row in rows) != Counter(manifest["status_counts"]):
        raise FullTextScreeningError("D11 final status counts mismatch")
    if (output_dir / "d11_final_manifest.json.sha256").read_text().split()[0] != sha256(path):
        raise FullTextScreeningError("D11 final manifest sidecar mismatch")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("validate-adjudication", "finalize", "verify"))
    args = parser.parse_args()
    if args.command == "validate-adjudication":
        result = validate_adjudication()
    elif args.command == "finalize":
        result = finalize()
    else:
        result = verify()
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
