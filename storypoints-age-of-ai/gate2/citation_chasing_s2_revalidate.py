"""Revalidate ambiguous empty D14 Semantic Scholar relation checkpoints."""
from __future__ import annotations

import argparse,json,os,time
from pathlib import Path
from typing import Any

from gate2.citation_chasing import OUTPUT,sha256
from gate2.citation_chasing_s2 import FINAL as BASELINE,S2Error,_relations,verify as verify_baseline

FINAL=OUTPUT/"semantic_scholar_empty_relation_revalidation"
WORK=OUTPUT/".s2_empty_relation_revalidation_work"
VERSION="d14-s2-empty-revalidation/1.0.0"

def _read(path:Path)->list[dict[str,Any]]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").split("\n") if x]

def targets()->list[dict[str,str]]:
    seeds={r["family_id"]:r for r in _read(BASELINE/"fallback_seed_resolution.jsonl") if r.get("status")=="resolved"}
    out=[]
    for p in sorted((BASELINE/"relations").glob("*.json")):
        if json.loads(p.read_text(encoding="utf-8"))!=[]:continue
        stem=p.stem
        direction="backward" if stem.endswith("_backward") else "forward" if stem.endswith("_forward") else None
        if not direction:raise S2Error(f"unknown relation filename: {p.name}")
        fid=stem[:-(len(direction)+1)];seed=seeds.get(fid);paper=(seed or {}).get("s2_record") or {}
        if not paper.get("paperId"):raise S2Error(f"missing resolved seed for {p.name}")
        out.append({"family_id":fid,"direction":direction,"paper_id":paper["paperId"],"baseline_file":p.name,"baseline_sha256":sha256(p)})
    if len(out)!=13:raise S2Error(f"ambiguous empty-response population changed: {len(out)}")
    return out

def _atomic(path:Path,value:Any)->None:
    tmp=path.with_suffix(path.suffix+".tmp");tmp.write_text(json.dumps(value,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8");tmp.replace(path)

def run()->dict[str,Any]:
    if FINAL.exists():raise S2Error("immutable empty-response revalidation exists")
    verify_baseline();api_key=os.environ.get("SEMANTIC_SCHOLAR_API_KEY","");delay=1.0 if api_key else 3.0
    WORK.mkdir(parents=True,exist_ok=True);check=WORK/"responses";check.mkdir(exist_ok=True);consecutive=0
    population=targets();envelopes=[]
    for target in population:
        path=check/f"{target['family_id']}_{target['direction']}.json";previous=json.loads(path.read_text()) if path.exists() else None
        if previous and previous.get("status")=="complete":envelope=previous
        else:
            kind="references" if target["direction"]=="backward" else "citations"
            try:data=_relations(target["paper_id"],kind,api_key);envelope={**target,"status":"complete","data":data,"attempt_count":int((previous or {}).get("attempt_count",0))+1}
            except S2Error:envelope={**target,"status":"api_failure","data":[],"attempt_count":int((previous or {}).get("attempt_count",0))+1}
            _atomic(path,envelope);time.sleep(delay)
        envelopes.append(envelope);consecutive=consecutive+1 if envelope["status"]=="api_failure" else 0
        if consecutive>=3:
            status={"status":"paused_rate_limit","target_count":len(population),"checkpointed_count":len(list(check.glob('*.json'))),"complete_count":sum(json.loads(p.read_text()).get('status')=='complete' for p in check.glob('*.json')),"consecutive_api_failures":3,"next_action":"Resume after API cooldown; completed responses will not be repeated."};_atomic(WORK/"revalidation_status.json",status);return status
    if any(e["status"]!="complete" for e in envelopes):raise S2Error("revalidation cannot publish incomplete responses")
    rows=[]
    for e in envelopes:
        node_key="citedPaper" if e["direction"]=="backward" else "citingPaper"
        for edge in e["data"]:
            node=edge.get(node_key) or {}
            if node.get("paperId"):rows.append({"seed_family_id":e["family_id"],"seed_s2_id":e["paper_id"],"direction":e["direction"],"related_s2_id":node["paperId"]})
    ep=WORK/"response_envelopes.jsonl";rp=WORK/"revalidated_relationships.jsonl"
    ep.write_text("".join(json.dumps(e,sort_keys=True,ensure_ascii=False)+"\n" for e in envelopes),encoding="utf-8");rp.write_text("".join(json.dumps(r,sort_keys=True)+"\n" for r in rows),encoding="utf-8")
    m={"status":"d14_s2_empty_relations_revalidated","pipeline_version":VERSION,"protocol_version":"1.3","target_count":13,"valid_empty_count":sum(not e["data"] for e in envelopes),"nonempty_count":sum(bool(e["data"]) for e in envelopes),"relationship_count":len(rows),"envelopes_sha256":sha256(ep),"relationships_sha256":sha256(rp),"credential_handling":"Optional API key read from environment only; never printed or persisted.","security_boundary":"Public scholarly metadata only; no Git, PDFs, credential files, installs, or private systems."}
    mp=WORK/"revalidation_manifest.json";mp.write_text(json.dumps(m,indent=2,sort_keys=True)+"\n",encoding="utf-8");(WORK/"revalidation_manifest.json.sha256").write_text(f"{sha256(mp)}  revalidation_manifest.json\n",encoding="utf-8");WORK.replace(FINAL);return m

def verify()->dict[str,Any]:
    mp=FINAL/"revalidation_manifest.json";m=json.loads(mp.read_text())
    if sha256(FINAL/"response_envelopes.jsonl")!=m["envelopes_sha256"] or sha256(FINAL/"revalidated_relationships.jsonl")!=m["relationships_sha256"]:raise S2Error("revalidation hash mismatch")
    if len(_read(FINAL/"response_envelopes.jsonl"))!=13:raise S2Error("revalidation population mismatch")
    if (FINAL/"revalidation_manifest.json.sha256").read_text().split()[0]!=sha256(mp):raise S2Error("revalidation sidecar mismatch")
    return m

def main()->int:
    p=argparse.ArgumentParser();p.add_argument("command",choices=("run","verify"));a=p.parse_args();print(json.dumps(run() if a.command=="run" else verify(),sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
