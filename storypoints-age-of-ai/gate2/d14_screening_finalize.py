"""Validate D14 adjudication and publish the final title/abstract ledger."""
from __future__ import annotations
import argparse,json,shutil,tempfile
from pathlib import Path
from typing import Any
from gate2.citation_chasing import sha256
from gate2.d14_screening_reconcile import FINAL as ADJ,verify as verify_reconciliation

FINAL=ADJ/"final";VERSION="d14-screening-finalize/1.0.0";CODES={"E1","E2","E3","E4","E9","E10",None}
def _read(p:Path)->list[dict[str,Any]]:return [json.loads(x) for x in p.read_text(encoding='utf-8').split('\n') if x]
def validate_adjudication(path:Path=ADJ/'adjudicated_decisions.jsonl')->dict[str,Any]:
    m=verify_reconciliation();packet=_read(ADJ/'adjudication_packet.jsonl');expected={r['family']['family_id'] for r in packet};rows=_read(path);seen=set();counts={'include':0,'exclude':0}
    for r in rows:
        fid=r.get('family_id')
        if fid not in expected or fid in seen:raise ValueError(f'unknown/duplicate adjudication: {fid}')
        seen.add(fid)
        if r.get('record_id')!=fid or r.get('stage')!='title_abstract':raise ValueError(f'adjudication identity/stage mismatch: {fid}')
        if r.get('final_title_abstract_decision') not in counts or r.get('decision_basis')!='separate_ai_adjudication':raise ValueError(f'adjudication decision invalid: {fid}')
        if r.get('exclusion_code') not in CODES or (r['final_title_abstract_decision']=='include' and r.get('exclusion_code') is not None):raise ValueError(f'adjudication exclusion code invalid: {fid}')
        if r.get('adjudicator_type')!='ai_agent' or r.get('adjudicator_id')!='d14-adjudicator' or not str(r.get('adjudication_context_id','')).startswith('d14-adjudicator-'):raise ValueError(f'adjudicator provenance invalid: {fid}')
        if r.get('input_checksum')!=m['adjudication_packet_sha256'] or r.get('prior_fulltext_or_synthesis_visible') is not False:raise ValueError(f'adjudicator input/blinding invalid: {fid}')
        if not r.get('reason') or not r.get('source_locator') or len(r.get('independence_attestation',''))<30:raise ValueError(f'adjudicator support incomplete: {fid}')
        if not isinstance(r.get('confidence'),(int,float)) or not 0<=r['confidence']<=1:raise ValueError(f'adjudicator confidence invalid: {fid}')
        counts[r['final_title_abstract_decision']]+=1
    if seen!=expected:raise ValueError(f'adjudication incomplete: {len(expected-seen)} missing')
    side=Path(str(path)+'.sha256')
    if not side.exists() or side.read_text().split()[0]!=sha256(path):raise ValueError('adjudication sidecar mismatch')
    return {'status':'valid_complete_adjudication','family_count':len(rows),'decision_counts':counts,'sha256':sha256(path)}
def finalize()->dict[str,Any]:
    if FINAL.exists():raise ValueError('immutable D14 final screening ledger exists')
    rm=verify_reconciliation();va=validate_adjudication();cons=_read(ADJ/'consensus_decisions.jsonl');adj=_read(ADJ/'adjudicated_decisions.jsonl')
    rows=[]
    for r in cons:rows.append({'family_id':r['family_id'],'record_id':r['record_id'],'final_title_abstract_decision':r['final_title_abstract_decision'],'exclusion_code':None,'decision_basis':r['decision_basis'],'adjudication_reason':None})
    for r in adj:rows.append({'family_id':r['family_id'],'record_id':r['record_id'],'final_title_abstract_decision':r['final_title_abstract_decision'],'exclusion_code':r.get('exclusion_code'),'decision_basis':r['decision_basis'],'adjudication_reason':r['reason']})
    rows.sort(key=lambda r:r['family_id'])
    if len(rows)!=6017 or len({r['family_id'] for r in rows})!=6017:raise ValueError('final D14 screening conservation failure')
    FINAL.parent.mkdir(parents=True,exist_ok=True);st=Path(tempfile.mkdtemp(prefix='d14-screen-final-',dir=str(FINAL.parent)))
    try:
        lp=st/'final_title_abstract_decisions.jsonl';lp.write_text(''.join(json.dumps(r,sort_keys=True,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
        counts={d:sum(r['final_title_abstract_decision']==d for r in rows) for d in ('include','exclude')}
        m={'status':'d14_title_abstract_screening_complete','protocol_version':'1.3','pipeline_version':VERSION,'family_count':6017,'decision_counts':counts,'consensus_count':rm['consensus_without_unclear_count'],'adjudicated_count':va['family_count'],'reconciliation_manifest_sha256':sha256(ADJ/'reconciliation_manifest.json'),'adjudication_sha256':va['sha256'],'final_ledger_sha256':sha256(lp),'interpretation_boundary':'AI-assisted title/abstract decisions require lawful full-text assessment before evidence inclusion.'}
        mp=st/'final_screening_manifest.json';mp.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n',encoding='utf-8');(st/'final_screening_manifest.json.sha256').write_text(f"{sha256(mp)}  final_screening_manifest.json\n",encoding='utf-8');st.rename(FINAL);return m
    except Exception:shutil.rmtree(st,ignore_errors=True);raise
def verify()->dict[str,Any]:
    mp=FINAL/'final_screening_manifest.json';m=json.loads(mp.read_text());rows=_read(FINAL/'final_title_abstract_decisions.jsonl')
    if len(rows)!=m['family_count'] or sha256(FINAL/'final_title_abstract_decisions.jsonl')!=m['final_ledger_sha256']:raise ValueError('final D14 screening ledger mismatch')
    if (FINAL/'final_screening_manifest.json.sha256').read_text().split()[0]!=sha256(mp):raise ValueError('final D14 screening sidecar mismatch')
    return m
def main()->int:
    p=argparse.ArgumentParser();p.add_argument('command',choices=('validate-adjudication','finalize','verify'));a=p.parse_args();r=validate_adjudication() if a.command=='validate-adjudication' else finalize() if a.command=='finalize' else verify();print(json.dumps(r,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
