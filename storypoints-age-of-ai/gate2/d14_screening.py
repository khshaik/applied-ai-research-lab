"""Prepare and validate isolated D14 citation-candidate screening passes."""
from __future__ import annotations

import argparse, hashlib, json, shutil, tempfile
from pathlib import Path
from typing import Any

from gate2.citation_chasing import OUTPUT, sha256
from gate2.d14_candidate_consolidation import FINAL as CONSOLIDATED, verify as verify_consolidation

FINAL=OUTPUT/"screening"
VERSION="d14-screening-controller/1.0.0"
SHARD_SIZE=100
DECISIONS={"include","exclude","unclear"}
STRATA={"peer_reviewed_scholarly","preprint_scholarly","grey_practitioner","method_reference"}


def _read(path:Path)->list[dict[str,Any]]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").split("\n") if x]


def _stratum(row:dict[str,Any])->str:
    venue=(row.get("venue") or "").casefold(); url=(row.get("url") or "").casefold()
    if row.get("arxiv_id") or "arxiv" in venue or "arxiv" in url: return "preprint_scholarly"
    if any(x in venue for x in ("repository","thesis","dissertation")): return "grey_practitioner"
    return "peer_reviewed_scholarly"


def prepare()->dict[str,Any]:
    if FINAL.exists(): raise ValueError("immutable D14 screening packet exists")
    cm=verify_consolidation(); families=_read(CONSOLIDATED/"candidate_families.jsonl")
    criteria={"include":{"I1":"professional or realistically simulated software engineering/development/delivery","I2":"generative AI, LLM assistant, or agentic coding system is material, unless deliberately foundational S8 evidence","I3":"measures, models, or substantively analyzes human effort/attention/oversight, estimation/planning, lifecycle readiness, flow, or quality consequences","I4":"inspectable method, framework definition, dataset, or evidence trail is indicated","I6":"within date window or intentionally retained foundational evidence"},"exclude":{"E1":"non-software domain without transferable software-engineering construct","E2":"code-generation accuracy benchmark only, without human/process/delivery implication","E3":"education-only without transferable measure or professional relevance","E4":"opinion/marketing/news without distinct traceable evidence or construct","E9":"only predicts traditional Story Points without evidence that AI changes work or estimation validity","E10":"building AI/ML products generally, not AI assistance in software delivery"},"unclear_rule":"retain as unclear when supplied title/abstract metadata cannot safely resolve inclusion; do not infer missing evidence"}
    packet=[]
    for row in families:
        packet.append({"family_id":row["citation_family_id"],"record_id":row["citation_family_id"],"stage":"title_abstract","search_families":"D14_citation_chasing","evidence_stratum_candidate":_stratum(row),"member_count":row["occurrence_count"],"title":row["title"],"abstract":row["abstract"],"authors":row["authors"],"publication_year":row["publication_year"],"doi":row["doi"],"arxiv_id":row["arxiv_id"],"venue":row["venue"],"url":row["url"],"frozen_criteria":criteria})
    packet.sort(key=lambda r:r["family_id"]); FINAL.parent.mkdir(parents=True,exist_ok=True)
    staging=Path(tempfile.mkdtemp(prefix="d14-screening-",dir=str(FINAL.parent)))
    try:
        shards=[]
        for start in range(0,len(packet),SHARD_SIZE):
            rows=packet[start:start+SHARD_SIZE]; name=f"screening_packet_{start//SHARD_SIZE+1:03d}.jsonl"; p=staging/name
            p.write_text("".join(json.dumps(r,sort_keys=True,ensure_ascii=False)+"\n" for r in rows),encoding="utf-8")
            shards.append({"path":name,"sha256":sha256(p),"row_count":len(rows),"first_family_id":rows[0]["family_id"],"last_family_id":rows[-1]["family_id"]})
        manifest={"status":"prepared_for_two_isolated_agent_passes","protocol_version":"1.3","controller_version":VERSION,"input_consolidation_manifest_sha256":sha256(CONSOLIDATED/"consolidation_manifest.json"),"family_count":len(packet),"shard_size":SHARD_SIZE,"shard_count":len(shards),"screening_unit":"citation_candidate_family","prompt_a":{"path":"evidence_review/prompts/screening_agent_a_v1.1.0.md","sha256":sha256(Path(__file__).resolve().parents[1]/"evidence_review/prompts/screening_agent_a_v1.1.0.md")},"prompt_b":{"path":"evidence_review/prompts/screening_agent_b_v1.1.0.md","sha256":sha256(Path(__file__).resolve().parents[1]/"evidence_review/prompts/screening_agent_b_v1.1.0.md")},"isolation_contract":"Byte-identical shards, distinct contexts, no cross-pass visibility; concordance is agent concordance, not human inter-rater reliability.","shards":shards}
        mp=staging/"screening_manifest.json";mp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8");(staging/"screening_manifest.json.sha256").write_text(f"{sha256(mp)}  screening_manifest.json\n",encoding="utf-8");staging.rename(FINAL);return manifest
    except Exception:
        shutil.rmtree(staging,ignore_errors=True);raise


def verify_packet()->dict[str,Any]:
    mp=FINAL/"screening_manifest.json";m=json.loads(mp.read_text())
    if m["input_consolidation_manifest_sha256"]!=sha256(CONSOLIDATED/"consolidation_manifest.json"):raise ValueError("D14 screening input drift")
    ids=[]
    for s in m["shards"]:
        p=FINAL/s["path"];rows=_read(p)
        if sha256(p)!=s["sha256"] or len(rows)!=s["row_count"]:raise ValueError(f"D14 screening shard mismatch: {p.name}")
        ids.extend(r["family_id"] for r in rows)
    if len(ids)!=m["family_count"] or len(set(ids))!=len(ids):raise ValueError("D14 screening population mismatch")
    if (FINAL/"screening_manifest.json.sha256").read_text().split()[0]!=sha256(mp):raise ValueError("D14 screening manifest sidecar mismatch")
    return m


def validate_pass(path:Path,pass_id:str)->dict[str,Any]:
    if pass_id not in {"pass-a","pass-b"}:raise ValueError("invalid pass")
    m=verify_packet();expected={}
    for s in m["shards"]:
        for r in _read(FINAL/s["path"]):expected[r["family_id"]]=(r["record_id"],s["sha256"])
    rows=_read(path);seen=set();counts={x:0 for x in sorted(DECISIONS)}
    for r in rows:
        fid=r.get("family_id")
        if fid not in expected or fid in seen:raise ValueError(f"unknown/duplicate D14 decision: {fid}")
        seen.add(fid);rid,checksum=expected[fid]
        if r.get("record_id")!=rid or r.get("input_checksum")!=checksum:raise ValueError(f"D14 decision binding mismatch: {fid}")
        if r.get("stage")!="title_abstract" or r.get("review_pass_id")!=pass_id:raise ValueError(f"D14 stage/pass mismatch: {fid}")
        if r.get("model_prompt_version")!=f"screening-agent-{pass_id[-1]}/1.1.0":raise ValueError(f"D14 prompt mismatch: {fid}")
        if r.get("reviewer_type")!="ai_agent" or r.get("prior_screening_decisions_visible") is not False:raise ValueError(f"D14 blindness mismatch: {fid}")
        if not r.get("reviewer_id") or not r.get("review_context_id") or len(r.get("independence_attestation", ""))<30:raise ValueError(f"D14 provenance incomplete: {fid}")
        if r.get("decision") not in DECISIONS or r.get("evidence_stratum") not in STRATA or not r.get("reason") or not r.get("source_locator"):raise ValueError(f"D14 decision invalid: {fid}")
        if not isinstance(r.get("confidence"),(int,float)) or not 0<=r["confidence"]<=1:raise ValueError(f"D14 confidence invalid: {fid}")
        counts[r["decision"]]+=1
    if seen!=set(expected):raise ValueError(f"D14 screening pass incomplete: {len(set(expected)-seen)} missing")
    return {"status":"valid_complete_agent_pass","pass_id":pass_id,"family_count":len(rows),"decision_counts":counts,"sha256":sha256(path)}


def main()->int:
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="command",required=True);sub.add_parser("prepare");sub.add_parser("verify-packet");v=sub.add_parser("validate-pass");v.add_argument("path",type=Path);v.add_argument("pass_id",choices=("pass-a","pass-b"));a=p.parse_args()
    result=prepare() if a.command=="prepare" else verify_packet() if a.command=="verify-packet" else validate_pass(a.path,a.pass_id);print(json.dumps(result,sort_keys=True));return 0


if __name__=="__main__":raise SystemExit(main())
