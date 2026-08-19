"""Finalize recovery eligibility and validate two full-population quality appraisals."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from typing import Any

from gate2.citation_chasing import OUTPUT, sha256
from gate2.d12_appraisal_partition_b_local import FORMS
from gate2.d14_new_candidate_consolidation import FINAL as CANDIDATES, verify as verify_candidates
from gate2.d14_new_fulltext_screening import FINAL as SCREEN, validate_pass, verify_packet as verify_screen
from gate2.d14_new_pdf_sanitize import FULLTEXT


FINAL = OUTPUT / "newly_resolved_quality_v2"
PACKET = FINAL / "packet"


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def prepare() -> dict[str, Any]:
    if FINAL.exists():
        raise ValueError("immutable recovery quality package exists")
    verify_screen(); verify_candidates()
    valid_a = validate_pass(SCREEN / "pass_a_decisions.jsonl", "pass-a")
    valid_b = validate_pass(SCREEN / "pass_b_decisions.jsonl", "pass-b")
    a = {row["family_id"]: row for row in _read(SCREEN / "pass_a_decisions.jsonl")}; b = {row["family_id"]: row for row in _read(SCREEN / "pass_b_decisions.jsonl")}
    if set(a) != set(b) or any(a[fid]["decision"] != "include" or b[fid]["decision"] != "include" for fid in a):
        raise ValueError("recovery full-text consensus mismatch")
    candidates = {row["citation_family_id"]: row for row in _read(CANDIDATES / "new_unique_candidates.jsonl")}
    rows = []
    for fid in sorted(a):
        source_result = json.loads((FULLTEXT / "sanitization_results" / f"{fid}.json").read_text())
        source_path = FULLTEXT / "sanitized_text" / f"{fid}.json"; payload = json.loads(source_path.read_text())
        if sha256(source_path) != source_result["text_sha256"]:
            raise ValueError("recovery quality source checksum mismatch")
        source = candidates[fid]
        rows.append({"family_id": fid, "record_id": fid, "title": source["title"], "doi": source.get("doi"), "arxiv_id": source.get("arxiv_id"),
                     "source_text_path": str(source_path), "source_text_sha256": source_result["text_sha256"], "page_count": len(payload["pages"])})
    PACKET.mkdir(parents=True)
    packet_path = PACKET / "quality_packet.jsonl"; packet_path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    eligibility = FINAL / "eligibility_ledger.jsonl"
    eligibility.write_text("".join(json.dumps({"family_id": fid, "final_fulltext_decision": "include", "decision_basis": "two_isolated_agent_consensus"}, sort_keys=True) + "\n" for fid in sorted(a)), encoding="utf-8")
    manifest = {"status": "d14_recovery_quality_packet_complete", "protocol_version": "1.3", "family_count": 9,
                "pass_a": valid_a, "pass_b": valid_b, "packet_path": str(packet_path), "packet_sha256": sha256(packet_path),
                "eligibility_sha256": sha256(eligibility),
                "security_boundary": "Checksum-bound action-free static text only; no network, Git/history, secrets, installs, or PDF execution."}
    manifest_path = PACKET / "manifest.json"; manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (PACKET / "manifest.json.sha256").write_text(f"{sha256(manifest_path)}  manifest.json\n", encoding="ascii")
    return manifest


def verify_packet() -> dict[str, Any]:
    path = PACKET / "manifest.json"; manifest = json.loads(path.read_text()); rows = _read(Path(manifest["packet_path"]))
    if len(rows) != 9 or len({r["family_id"] for r in rows}) != 9 or sha256(Path(manifest["packet_path"])) != manifest["packet_sha256"]:
        raise ValueError("recovery quality packet mismatch")
    for row in rows:
        if sha256(Path(row["source_text_path"])) != row["source_text_sha256"]:
            raise ValueError("recovery quality source drift")
    if (PACKET / "manifest.json.sha256").read_text().split()[0] != sha256(path):
        raise ValueError("recovery quality manifest mismatch")
    return manifest


def validate_appraisal(path: Path, pass_id: str, appraiser_id: str) -> dict[str, Any]:
    manifest = verify_packet(); expected = {r["family_id"]: r for r in _read(Path(manifest["packet_path"]))}; rows = _read(path); seen = set(); contexts = set()
    for row in rows:
        fid = row.get("family_id"); context = row.get("review_context_id")
        if fid not in expected or fid in seen or not context or context in contexts:
            raise ValueError("recovery appraisal identity/context mismatch")
        seen.add(fid); contexts.add(context)
        if row.get("record_id") != fid or row.get("source_text_sha256") != expected[fid]["source_text_sha256"] or row.get("appraiser_agent_id") != appraiser_id or row.get("appraisal_pass_id") != pass_id:
            raise ValueError("recovery appraisal provenance mismatch")
        form = row.get("appraisal_form"); criteria = row.get("criteria")
        if form not in FORMS or [x.get("criterion_id") for x in criteria or []] != [x[0] for x in FORMS[form]]:
            raise ValueError("recovery appraisal form mismatch")
        for item in criteria:
            locator = str(item.get("source_locator", ""))
            if item.get("score") not in {0, 1, 2} or not item.get("justification") or not locator.startswith("page ") or not locator[5:].isdigit() or not 1 <= int(locator[5:]) <= expected[fid]["page_count"]:
                raise ValueError("recovery appraisal criterion invalid")
        points = sum(x["score"] for x in criteria); critical = row.get("critical_flaw") is True
        expected_band = "low_contextual" if critical or points < 10 else "moderate" if points < 15 else "high"
        if row.get("applicable_points") != 20 or row.get("points_awarded") != points or row.get("percent") != points * 5.0 or row.get("evidence_band") != expected_band:
            raise ValueError("recovery appraisal arithmetic/band mismatch")
        if critical and not row.get("critical_flaw_basis"):
            raise ValueError("recovery critical flaw unsupported")
        if row.get("evidence_nature") not in {"observed", "self-reported", "modeled", "conceptual"} or len(row.get("security_attestation", "")) < 30:
            raise ValueError("recovery appraisal evidence/security invalid")
    if seen != set(expected):
        raise ValueError("recovery appraisal incomplete")
    sidecar = path.with_suffix(path.suffix + ".sha256")
    if not sidecar.exists() or sidecar.read_text().split()[0] != sha256(path):
        raise ValueError("recovery appraisal sidecar mismatch")
    return {"status": "valid_complete_recovery_appraisal", "pass_id": pass_id, "family_count": len(rows),
            "forms": dict(Counter(r["appraisal_form"] for r in rows)), "bands": dict(Counter(r["evidence_band"] for r in rows)), "sha256": sha256(path)}


def main() -> int:
    parser = argparse.ArgumentParser(); sub = parser.add_subparsers(dest="command", required=True); sub.add_parser("prepare"); sub.add_parser("verify-packet")
    val = sub.add_parser("validate-appraisal"); val.add_argument("path", type=Path); val.add_argument("pass_id", choices=("pass-a", "pass-b")); val.add_argument("appraiser_id")
    args = parser.parse_args(); result = prepare() if args.command == "prepare" else verify_packet() if args.command == "verify-packet" else validate_appraisal(args.path, args.pass_id, args.appraiser_id)
    print(json.dumps(result, sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
