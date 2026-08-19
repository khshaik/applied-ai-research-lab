"""Prepare a local-only D14 full-text retrieval inventory."""
from __future__ import annotations
import argparse,csv,json
from collections import Counter
from pathlib import Path
from typing import Any
from gate2.citation_chasing import OUTPUT,normalized_title,sha256
from gate2.d14_candidate_consolidation import FINAL as CANDIDATES
from gate2.d14_screening_finalize import FINAL as SCREEN_FINAL,verify as verify_screening

FINAL=OUTPUT/"fulltext";D10=OUTPUT.parent/"d10/final/fulltext_retrieval_ledger.jsonl";VERSION="d14-fulltext-inventory/1.0.0"
def _read(p:Path)->list[dict[str,Any]]:return [json.loads(x) for x in p.read_text(encoding='utf-8').split('\n') if x]
def prepare()->dict[str,Any]:
    if FINAL.exists():raise ValueError('immutable D14 full-text inventory exists')
    sm=verify_screening();dec={r['family_id']:r for r in _read(SCREEN_FINAL/'final_title_abstract_decisions.jsonl')};families=_read(CANDIDATES/'candidate_families.jsonl')
    existing=_read(D10) if D10.exists() else [];existing_doi={(r.get('doi') or '').lower():r for r in existing if r.get('doi')};existing_title={normalized_title(r.get('title') or ''):r for r in existing if r.get('title')}
    rows=[]
    for f in families:
        if dec[f['citation_family_id']]['final_title_abstract_decision']!='include':continue
        doi=(f.get('doi') or '').lower();arxiv=f.get('arxiv_id') or '';title=f['normalized_title'];local=existing_doi.get(doi) if doi else existing_title.get(title)
        if local and local.get('full_text_status')=='retrieved_open':route='existing_lawful_local_copy'
        elif arxiv:route='arxiv_public_identifier'
        elif doi:route='doi_lawful_version_discovery'
        elif f.get('url'):route='record_url_lawful_access_check'
        else:route='no_retrieval_identifier'
        rows.append({'citation_family_id':f['citation_family_id'],'title':f['title'],'publication_year':f.get('publication_year'),'doi':doi,'arxiv_id':arxiv,'record_url':f.get('url'),'venue':f.get('venue'),'retrieval_route':route,'existing_local_pdf_path':(local or {}).get('pdf_path'),'retrieval_status':'pending','lawful_access_only':True})
    rows.sort(key=lambda r:r['citation_family_id']);FINAL.mkdir(parents=True)
    p=FINAL/'retrieval_inventory.jsonl';p.write_text(''.join(json.dumps(r,sort_keys=True,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8');counts=Counter(r['retrieval_route'] for r in rows)
    m={'status':'d14_fulltext_inventory_prepared','protocol_version':'1.3','pipeline_version':VERSION,'included_candidate_count':len(rows),'route_counts':dict(sorted(counts.items())),'screening_manifest_sha256':sha256(SCREEN_FINAL/'final_screening_manifest.json'),'candidate_manifest_sha256':sha256(CANDIDATES/'consolidation_manifest.json'),'inventory_sha256':sha256(p),'network_access_performed':False,'security_boundary':'Local metadata reconciliation only; no downloads, links opened, PDFs executed, Git, secrets, installs, or private systems.'}
    mp=FINAL/'inventory_manifest.json';mp.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n',encoding='utf-8');(FINAL/'inventory_manifest.json.sha256').write_text(f"{sha256(mp)}  inventory_manifest.json\n",encoding='utf-8');return m
def verify()->dict[str,Any]:
    mp=FINAL/'inventory_manifest.json';m=json.loads(mp.read_text());rows=_read(FINAL/'retrieval_inventory.jsonl')
    if len(rows)!=m['included_candidate_count'] or sha256(FINAL/'retrieval_inventory.jsonl')!=m['inventory_sha256']:raise ValueError('D14 full-text inventory mismatch')
    if len({r['citation_family_id'] for r in rows})!=len(rows):raise ValueError('D14 full-text inventory duplicate')
    if (FINAL/'inventory_manifest.json.sha256').read_text().split()[0]!=sha256(mp):raise ValueError('D14 full-text inventory sidecar mismatch')
    return m
def main()->int:
    p=argparse.ArgumentParser();p.add_argument('command',choices=('prepare','verify'));a=p.parse_args();print(json.dumps(prepare() if a.command=='prepare' else verify(),sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
