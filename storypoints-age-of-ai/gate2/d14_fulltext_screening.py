"""Prepare and validate isolated D14 full-text eligibility passes."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from gate2.citation_chasing import OUTPUT, sha256
from gate2.d14_fulltext_dispositions import FINAL as DISPOSITIONS, verify as verify_dispositions

FINAL = OUTPUT / "fulltext_screening"
PACKET = FINAL / "packet"
VERSION = "d14-fulltext-screening/1.0.0"
DECISIONS = {"include", "exclude", "unclear"}
STRATA = {"peer_reviewed_scholarly", "preprint", "secondary_review", "conceptual", "industry_grey", "indirect_foundational"}
EXCLUSIONS = {f"E{index}" for index in range(1, 11)}
CRITERIA = {
    "inclusion": {
        "I1": "professional or realistically simulated software engineering/development/delivery",
        "I2": "generative AI, LLM assistant, or agentic coding system is material",
        "I3": "measures, models, or substantively analyzes human work, planning, readiness, flow, oversight, or quality consequences",
        "I4": "inspectable method, framework definition, dataset, or evidence trail",
        "I5": "English full text available",
        "I6": "within date window or intentionally foundational",
        "I7": "most complete accessible study version",
    },
    "exclusion": {
        "E1": "non-software domain without transferable SE construct",
        "E2": "code-generation benchmark only, without human/process/delivery implication",
        "E3": "education-only without validated professional transfer",
        "E4": "opinion/marketing/news without traceable evidence or construct",
        "E5": "abstract/poster/slides only",
        "E6": "duplicate or superseded version",
        "E7": "non-English without reliable translation",
        "E8": "claimed empirical result has no transparent method",
        "E9": "traditional Story-Point prediction only, without evidence that AI changes work or estimation validity",
        "E10": "building AI/ML products rather than AI assistance in software delivery",
    },
    "borderline": "Include requirements/architecture/testing/review/security/operations only when human work or lifecycle evidence is relevant. Technical quality evidence may support assurance/readiness/rework/risk but cannot validate human workload.",
}


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"); tmp.replace(path)


def _atomic_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8"); tmp.replace(path)


def build_packet() -> dict[str, Any]:
    if PACKET.exists():
        raise ValueError("immutable D14 full-text packet exists")
    verify_dispositions()
    rows = [row for row in _read(DISPOSITIONS / "fulltext_dispositions.jsonl") if row["eligible_for_fulltext_screening"]]
    if len(rows) != 337:
        raise ValueError("D14 screenable population drift")
    input_checksum = hashlib.sha256(json.dumps({"criteria": CRITERIA, "families": [(row["citation_family_id"], row["sanitized_text_sha256"]) for row in rows]}, sort_keys=True).encode()).hexdigest()
    packet = []
    for row in rows:
        text_payload = json.loads(Path(row["sanitized_text_path"]).read_text(encoding="utf-8"))
        packet.append({
            "family_id": row["citation_family_id"],
            "record_id": row["citation_family_id"],
            "title": row["title"],
            "doi": row["doi"],
            "arxiv_id": row["arxiv_id"],
            "stage": "full_text",
            "source_text_path": row["sanitized_text_path"],
            "source_text_sha256": row["sanitized_text_sha256"],
            "page_count": len(text_payload["pages"]),
            "input_checksum": input_checksum,
            "frozen_criteria": CRITERIA,
        })
    shards=[]
    for index in range(0, len(packet), 50):
        path=PACKET/f"packet_{index//50+1:02d}.jsonl"; chunk=packet[index:index+50]; _atomic_jsonl(path,chunk)
        shards.append({"path":str(path),"row_count":len(chunk),"sha256":sha256(path)})
    manifest={
        "status":"d14_fulltext_packet_complete","pipeline_version":VERSION,"family_count":len(packet),
        "input_checksum":input_checksum,"criteria":CRITERIA,"shards":shards,
        "disposition_manifest_sha256":sha256(DISPOSITIONS/"disposition_manifest.json"),
        "security_boundary":"Checksum-bound static text only; no network, Git/history, credentials, PDF execution, or private systems.",
    }
    path=PACKET/"packet_manifest.json"; _atomic_json(path,manifest)
    (PACKET/"packet_manifest.json.sha256").write_text(f"{sha256(path)}  packet_manifest.json\n",encoding="ascii")
    return manifest


def verify_packet() -> dict[str, Any]:
    path=PACKET/"packet_manifest.json"; manifest=json.loads(path.read_text(encoding="utf-8")); rows=[]
    for shard in manifest["shards"]:
        p=Path(shard["path"]); chunk=_read(p)
        if len(chunk)!=shard["row_count"] or sha256(p)!=shard["sha256"]:raise ValueError("D14 packet shard mismatch")
        rows.extend(chunk)
    if len(rows)!=337 or len({row["family_id"] for row in rows})!=337:raise ValueError("D14 packet population mismatch")
    for row in rows:
        if row["input_checksum"]!=manifest["input_checksum"] or sha256(Path(row["source_text_path"]))!=row["source_text_sha256"]:raise ValueError("D14 packet binding mismatch")
    if (PACKET/"packet_manifest.json.sha256").read_text().split()[0]!=sha256(path):raise ValueError("D14 packet sidecar mismatch")
    return manifest


def validate_pass(path: Path, pass_id: str) -> dict[str, Any]:
    manifest=verify_packet(); packet=[]
    for shard in manifest["shards"]:packet.extend(_read(Path(shard["path"])))
    expected={row["family_id"]:row for row in packet}; decisions=_read(path); seen=set()
    for row in decisions:
        fid=row.get("family_id")
        if fid not in expected or fid in seen:raise ValueError("unknown or duplicate D14 full-text decision")
        seen.add(fid)
        if row.get("record_id")!=expected[fid]["record_id"] or row.get("input_checksum")!=manifest["input_checksum"]:raise ValueError("D14 full-text decision binding mismatch")
        if row.get("stage")!="full_text" or row.get("review_pass_id")!=pass_id or row.get("prior_screening_decisions_visible") is not False:raise ValueError("D14 full-text pass provenance mismatch")
        if row.get("reviewer_type")!="ai_agent" or not row.get("reviewer_id") or not row.get("review_context_id") or len(row.get("independence_attestation", ""))<30:raise ValueError("D14 full-text reviewer provenance incomplete")
        if row.get("decision") not in DECISIONS or row.get("evidence_stratum") not in STRATA or not row.get("reason") or not row.get("source_locator"):raise ValueError("D14 full-text decision invalid")
        if not isinstance(row.get("confidence"),(int,float)) or not 0<=row["confidence"]<=1:raise ValueError("D14 full-text confidence invalid")
        code=row.get("exclusion_code")
        if row["decision"]=="exclude" and code not in EXCLUSIONS:raise ValueError("D14 full-text exclusion code required")
        if row["decision"]!="exclude" and code is not None:raise ValueError("D14 full-text exclusion code only allowed for exclusion")
    if seen!=set(expected):raise ValueError(f"D14 full-text pass incomplete: {len(set(expected)-seen)} missing")
    return {"status":"valid_complete_agent_pass","pass_id":pass_id,"family_count":len(decisions),"decision_counts":dict(Counter(row["decision"] for row in decisions)),"sha256":sha256(path)}


def main() -> int:
    parser=argparse.ArgumentParser(); sub=parser.add_subparsers(dest="command",required=True); sub.add_parser("build-packet"); sub.add_parser("verify-packet"); val=sub.add_parser("validate-pass"); val.add_argument("path",type=Path); val.add_argument("pass_id",choices=("pass-a","pass-b")); args=parser.parse_args()
    result=build_packet() if args.command=="build-packet" else verify_packet() if args.command=="verify-packet" else validate_pass(args.path,args.pass_id)
    print(json.dumps(result,sort_keys=True)); return 0


if __name__=="__main__":raise SystemExit(main())
