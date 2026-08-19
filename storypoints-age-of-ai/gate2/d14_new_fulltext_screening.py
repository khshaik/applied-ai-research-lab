"""Prepare and validate isolated full-text screening for D14 recovery reports."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from gate2.citation_chasing import OUTPUT, sha256
from gate2.d14_fulltext_screening import CRITERIA, DECISIONS, EXCLUSIONS, STRATA
from gate2.d14_new_candidate_consolidation import FINAL as CANDIDATES, verify as verify_candidates
from gate2.d14_new_pdf_sanitize import FULLTEXT


FINAL = OUTPUT / "newly_resolved_fulltext_screening_v2"
PACKET = FINAL / "packet"


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def build_packet() -> dict[str, Any]:
    if PACKET.exists():
        raise ValueError("immutable recovery full-text packet exists")
    verify_candidates()
    candidates = {row["citation_family_id"]: row for row in _read(CANDIDATES / "new_unique_candidates.jsonl")}
    results = [json.loads(path.read_text(encoding="utf-8")) for path in sorted((FULLTEXT / "sanitization_results").glob("*.json"))]
    results = [row for row in results if row["status"] == "sanitized_static_extraction_verified"]
    if len(results) != 9:
        raise ValueError("recovery full-text population drift")
    pairs = sorted((row["citation_family_id"], row["text_sha256"]) for row in results)
    checksum = hashlib.sha256(json.dumps({"criteria": CRITERIA, "families": pairs}, sort_keys=True).encode()).hexdigest()
    packet = []
    for result in sorted(results, key=lambda row: row["citation_family_id"]):
        fid = result["citation_family_id"]
        text_path = FULLTEXT / "sanitized_text" / f"{fid}.json"
        payload = json.loads(text_path.read_text(encoding="utf-8"))
        source = candidates[fid]
        packet.append({
            "family_id": fid, "record_id": fid, "title": source["title"], "doi": source.get("doi"),
            "arxiv_id": source.get("arxiv_id"), "stage": "full_text", "source_text_path": str(text_path),
            "source_text_sha256": result["text_sha256"], "page_count": len(payload["pages"]),
            "input_checksum": checksum, "frozen_criteria": CRITERIA,
        })
    PACKET.mkdir(parents=True)
    packet_path = PACKET / "packet.jsonl"
    packet_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in packet), encoding="utf-8")
    manifest = {"status": "d14_recovery_fulltext_packet_complete", "protocol_version": "1.3", "family_count": 9,
                "input_checksum": checksum, "packet_path": str(packet_path), "packet_sha256": sha256(packet_path),
                "security_boundary": "Checksum-bound action-free static text only; no network, Git/history, secrets, or PDF execution."}
    manifest_path = PACKET / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (PACKET / "manifest.json.sha256").write_text(f"{sha256(manifest_path)}  manifest.json\n", encoding="ascii")
    return manifest


def verify_packet() -> dict[str, Any]:
    manifest_path = PACKET / "manifest.json"; manifest = json.loads(manifest_path.read_text())
    rows = _read(Path(manifest["packet_path"]))
    if len(rows) != 9 or len({row["family_id"] for row in rows}) != 9 or sha256(Path(manifest["packet_path"])) != manifest["packet_sha256"]:
        raise ValueError("recovery full-text packet mismatch")
    for row in rows:
        if row["input_checksum"] != manifest["input_checksum"] or sha256(Path(row["source_text_path"])) != row["source_text_sha256"]:
            raise ValueError("recovery source binding mismatch")
    if (PACKET / "manifest.json.sha256").read_text().split()[0] != sha256(manifest_path):
        raise ValueError("recovery packet sidecar mismatch")
    return manifest


def validate_pass(path: Path, pass_id: str) -> dict[str, Any]:
    manifest = verify_packet(); expected = {row["family_id"]: row for row in _read(Path(manifest["packet_path"]))}
    rows = _read(path); seen = set(); contexts = set()
    for row in rows:
        fid = row.get("family_id"); context = row.get("review_context_id")
        if fid not in expected or fid in seen or not context or context in contexts:
            raise ValueError("unknown, duplicate, or invalid recovery decision")
        seen.add(fid); contexts.add(context)
        if row.get("record_id") != fid or row.get("input_checksum") != manifest["input_checksum"]:
            raise ValueError("recovery decision binding mismatch")
        if row.get("stage") != "full_text" or row.get("review_pass_id") != pass_id or row.get("prior_screening_decisions_visible") is not False:
            raise ValueError("recovery review provenance mismatch")
        if row.get("reviewer_type") != "ai_agent" or not row.get("reviewer_id") or len(row.get("independence_attestation", "")) < 30:
            raise ValueError("recovery reviewer provenance incomplete")
        if row.get("decision") not in DECISIONS or row.get("evidence_stratum") not in STRATA or not row.get("reason") or not row.get("source_locator"):
            raise ValueError("recovery decision invalid")
        if not isinstance(row.get("confidence"), (int, float)) or not 0 <= row["confidence"] <= 1:
            raise ValueError("recovery confidence invalid")
        code = row.get("exclusion_code")
        if (row["decision"] == "exclude" and code not in EXCLUSIONS) or (row["decision"] != "exclude" and code is not None):
            raise ValueError("recovery exclusion-code mismatch")
    if seen != set(expected):
        raise ValueError("recovery pass incomplete")
    sidecar = path.with_suffix(path.suffix + ".sha256")
    if not sidecar.exists() or sidecar.read_text().split()[0] != sha256(path):
        raise ValueError("recovery pass checksum mismatch")
    return {"status": "valid_complete_agent_pass", "pass_id": pass_id, "family_count": len(rows),
            "decision_counts": dict(Counter(row["decision"] for row in rows)), "sha256": sha256(path)}


def main() -> int:
    parser = argparse.ArgumentParser(); sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("build-packet"); sub.add_parser("verify-packet")
    check = sub.add_parser("validate-pass"); check.add_argument("path", type=Path); check.add_argument("pass_id", choices=("pass-a", "pass-b"))
    args = parser.parse_args()
    result = build_packet() if args.command == "build-packet" else verify_packet() if args.command == "verify-packet" else validate_pass(args.path, args.pass_id)
    print(json.dumps(result, sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
