"""Prepare and validate D11 isolated full-text screening passes."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SYSTEMATIC = ROOT / "gate2/output/systematic/v1.3/20260816"
D06 = SYSTEMATIC / "d06"
D07 = SYSTEMATIC / "d07"
D10 = SYSTEMATIC / "d10"
EXTRACTION = SYSTEMATIC / "d11/extraction"
OUTPUT = SYSTEMATIC / "d11/screening"
VERSION = "d11-fulltext-screening-controller/1.0.0"
PREPARED_AT = "2026-08-17T00:30:00Z"
SHARD_SIZE = 50
DECISIONS = {"include", "exclude", "unclear"}
EXCLUSION_CODES = {f"E{number}" for number in range(1, 11)}
STRATA = {"peer_reviewed_scholarly", "preprint_scholarly", "grey_practitioner", "method_reference"}


class FullTextScreeningError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(output_dir: Path = OUTPUT) -> dict[str, Any]:
    if output_dir.exists():
        raise FullTextScreeningError(f"immutable D11 packet already exists: {output_dir}")
    d10_ledger = [json.loads(line) for line in (D10 / "final/fulltext_retrieval_ledger.jsonl").read_text(encoding="utf-8").splitlines()]
    extraction_index = {row["family_id"]: row for row in (json.loads(line) for line in (EXTRACTION / "extraction_index.jsonl").read_text(encoding="utf-8").splitlines())}
    families = {row["family_id"]: row for row in (json.loads(line) for line in (D07 / "study_families.jsonl").read_text(encoding="utf-8").splitlines())}
    with (D06 / "canonical_records.csv").open(encoding="utf-8", newline="") as handle:
        reports = {row["canonical_id"]: row for row in csv.DictReader(handle)}
    packet_rows, unavailable = [], []
    for retrieval in sorted(d10_ledger, key=lambda row: row["family_id"]):
        family_id = retrieval["family_id"]
        family = families[family_id]
        report = reports[family["representative_canonical_id"]]
        extraction = extraction_index.get(family_id)
        if retrieval["full_text_status"] != "retrieved_open" or not extraction or extraction["status"] != "text_extracted":
            reason = "retrieval_unavailable" if retrieval["full_text_status"] != "retrieved_open" else "encrypted_or_unextractable_full_text"
            unavailable.append({"family_id": family_id, "record_id": family["representative_canonical_id"],
                                "full_text_decision": "unavailable", "reason": reason,
                                "retrieval_status": retrieval["full_text_status"], "exclusion_code": "E7" if reason == "encrypted_or_unextractable_full_text" else None})
            continue
        text_path = EXTRACTION / "text" / f"{family_id}.json"
        packet_rows.append({
            "family_id": family_id, "record_id": family["representative_canonical_id"],
            "stage": "full_text", "title": report["title"], "authors": report["authors"],
            "published": report["published"], "doi": report["doi"], "arxiv_id": report["arxiv_id"],
            "search_families": report["search_families"],
            "evidence_stratum_candidate": ("preprint_scholarly" if report["evidence_stratum_candidate"] == "preprint_scholarly" else "peer_reviewed_scholarly"),
            "extracted_text_path": str(text_path.relative_to(ROOT)), "extracted_text_sha256": sha256(text_path),
            "pdf_path": retrieval["pdf_path"], "pdf_sha256": retrieval["pdf_sha256"],
            "page_count": extraction["page_count"],
            "frozen_criteria": {
                "I1": "professional or realistically simulated software engineering/development/delivery",
                "I2": "generative AI/LLM/agentic assistance is material, except intentionally foundational S8 evidence",
                "I3": "measures, models, or substantively analyzes human effort/attention/oversight, estimation/planning, readiness, flow, or quality consequences",
                "I4": "inspectable method, framework definition, dataset, or evidence trail",
                "I5": "lawful English full text available",
                "I6": "date window or intentionally retained foundational evidence",
                "I7": "most complete accessible study version",
                "exclusion_codes": {
                    "E1": "non-software domain without transferable construct", "E2": "code-generation accuracy benchmark only",
                    "E3": "education-only without transferable/professional relevance", "E4": "opinion/marketing/news without traceable evidence",
                    "E5": "abstract/poster/slides only without adequate evidence", "E6": "duplicate/earlier superseded version",
                    "E7": "non-English/unreadable full text", "E8": "no inspectable method for empirical claim",
                    "E9": "traditional Story-Point prediction only", "E10": "building AI/ML products, not AI assistance in delivery",
                },
            },
        })
    if len(packet_rows) != 1604 or len(unavailable) != 472 or len(packet_rows) + len(unavailable) != 2076:
        raise FullTextScreeningError("D11 assessment/unavailable conservation failed")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="d11-screening-", dir=str(output_dir.parent)))
    try:
        shards = []
        for start in range(0, len(packet_rows), SHARD_SIZE):
            rows = packet_rows[start:start + SHARD_SIZE]
            name = f"fulltext_packet_{start // SHARD_SIZE + 1:03d}.jsonl"
            path = staging / name
            path.write_text("".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
            shards.append({"path": name, "sha256": sha256(path), "row_count": len(rows)})
        unavailable_path = staging / "unavailable_fulltexts.jsonl"
        unavailable_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in unavailable), encoding="utf-8")
        manifest = {
            "status": "prepared_for_two_isolated_fulltext_passes", "protocol_version": "1.3",
            "controller_version": VERSION, "prepared_at_utc": PREPARED_AT,
            "input_d10_manifest_sha256": sha256(D10 / "final/d10_final_manifest.json"),
            "input_extraction_manifest_sha256": sha256(EXTRACTION / "extraction_manifest.json"),
            "assessable_family_count": len(packet_rows), "unavailable_family_count": len(unavailable),
            "total_family_count": len(packet_rows) + len(unavailable), "shard_count": len(shards),
            "unavailable_sha256": sha256(unavailable_path), "shards": shards,
            "security_boundary": "Local extracted text only. No PDF actions, links, attachments, scripts, macros, network, credentials, or Git history are used by screening agents.",
            "isolation_contract": "Passes A and B receive the same checksum-bound packet and text files in distinct contexts and cannot inspect each other's decisions. Concordance is not human inter-rater reliability.",
        }
        manifest_path = staging / "d11_packet_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (staging / "d11_packet_manifest.json.sha256").write_text(f"{sha256(manifest_path)}  d11_packet_manifest.json\n", encoding="utf-8")
        staging.rename(output_dir)
        return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def verify_packet(output_dir: Path = OUTPUT) -> dict[str, Any]:
    manifest_path = output_dir / "d11_packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    total, ids = 0, set()
    for shard in manifest["shards"]:
        path = output_dir / shard["path"]
        if sha256(path) != shard["sha256"]:
            raise FullTextScreeningError(f"D11 shard hash mismatch: {path.name}")
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        if len(rows) != shard["row_count"]:
            raise FullTextScreeningError(f"D11 shard count mismatch: {path.name}")
        for row in rows:
            text_path = ROOT / row["extracted_text_path"]
            if sha256(text_path) != row["extracted_text_sha256"]:
                raise FullTextScreeningError(f"D11 extracted text mismatch: {row['family_id']}")
            ids.add(row["family_id"])
        total += len(rows)
    if total != manifest["assessable_family_count"] or len(ids) != total:
        raise FullTextScreeningError("D11 packet identity/count mismatch")
    if (output_dir / "d11_packet_manifest.json.sha256").read_text().split()[0] != sha256(manifest_path):
        raise FullTextScreeningError("D11 manifest sidecar mismatch")
    return manifest


def validate_pass(path: Path, pass_id: str, output_dir: Path = OUTPUT) -> dict[str, Any]:
    if pass_id not in {"pass-a", "pass-b"}:
        raise FullTextScreeningError("invalid D11 pass ID")
    manifest = verify_packet(output_dir)
    expected = {}
    for shard in manifest["shards"]:
        for row in (json.loads(line) for line in (output_dir / shard["path"]).read_text(encoding="utf-8").splitlines()):
            expected[row["family_id"]] = (row, shard["sha256"])
    decisions = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    seen = set(); counts = {"include": 0, "exclude": 0, "unclear": 0}
    for row in decisions:
        family_id = row.get("family_id")
        if family_id not in expected or family_id in seen:
            raise FullTextScreeningError(f"unknown/duplicate D11 family: {family_id}")
        seen.add(family_id); packet, checksum = expected[family_id]
        if row.get("record_id") != packet["record_id"] or row.get("input_checksum") != checksum:
            raise FullTextScreeningError(f"D11 record/checksum mismatch: {family_id}")
        if row.get("stage") != "full_text" or row.get("review_pass_id") != pass_id:
            raise FullTextScreeningError(f"D11 stage/pass mismatch: {family_id}")
        if row.get("decision") not in DECISIONS:
            raise FullTextScreeningError(f"D11 decision unresolved/invalid: {family_id}")
        if row["decision"] == "exclude" and row.get("exclusion_code") not in EXCLUSION_CODES:
            raise FullTextScreeningError(f"D11 exclusion lacks E1-E10: {family_id}")
        if row["decision"] in {"include", "unclear"} and row.get("exclusion_code") is not None:
            raise FullTextScreeningError(f"D11 include/unclear decision carries exclusion code: {family_id}")
        if row.get("evidence_stratum") not in STRATA or not row.get("reason"):
            raise FullTextScreeningError(f"D11 reason/stratum missing: {family_id}")
        if not re.search(r"\bpage(?:s)?\s+\d+", row.get("source_locator", ""), flags=re.I):
            raise FullTextScreeningError(f"D11 locator lacks page number: {family_id}")
        if row.get("reviewer_type") != "ai_agent" or row.get("prior_screening_decisions_visible") is not False:
            raise FullTextScreeningError(f"D11 blindness declaration missing: {family_id}")
        if not row.get("reviewer_id") or not row.get("review_context_id") or len(row.get("independence_attestation", "")) < 30:
            raise FullTextScreeningError(f"D11 provenance incomplete: {family_id}")
        confidence = row.get("confidence")
        if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            raise FullTextScreeningError(f"D11 confidence invalid: {family_id}")
        counts[row["decision"]] += 1
    if seen != set(expected):
        raise FullTextScreeningError(f"D11 pass incomplete: missing {len(set(expected)-seen)}")
    return {"status": "valid_complete_fulltext_agent_pass", "pass_id": pass_id,
            "family_count": len(seen), "decision_counts": counts, "sha256": sha256(path)}


def main() -> int:
    parser = argparse.ArgumentParser(); sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("prepare"); sub.add_parser("verify-packet")
    validation = sub.add_parser("validate-pass"); validation.add_argument("path", type=Path); validation.add_argument("pass_id")
    args = parser.parse_args()
    result = prepare() if args.command == "prepare" else verify_packet() if args.command == "verify-packet" else validate_pass(args.path, args.pass_id)
    print(json.dumps(result, sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
