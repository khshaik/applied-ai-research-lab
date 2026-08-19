"""Resolve D14 lawful PDF candidates from frozen local metadata only."""
from __future__ import annotations
import argparse,json
from collections import Counter,defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from gate2.citation_chasing import OUTPUT,sha256
from gate2.d14_candidate_consolidation import FINAL as CONSOLIDATED
from gate2.d14_fulltext_inventory import FINAL as FULLTEXT,verify as verify_inventory

FINAL=FULLTEXT/"locations";OA=OUTPUT/"round1_openalex";VERSION="d14-fulltext-locations/1.0.0"
def _read(p:Path)->list[dict[str,Any]]:return [json.loads(x) for x in p.read_text(encoding='utf-8').split('\n') if x]
def _https_pdf(url:str)->bool:
    u=urlparse(url or '');return u.scheme=='https' and bool(u.hostname) and (u.path.casefold().endswith('.pdf') or '/pdf' in u.path.casefold())
def _oa_records()->dict[str,dict[str,Any]]:
    out={}
    for p in sorted(OA.rglob('*_page_*.json')):
        d=json.loads(p.read_text(encoding='utf-8'))
        for r in d.get('results') or []:
            if r.get('id'):out[r['id']]=r
    for p in sorted(OA.rglob('*.complete.json')):
        d=json.loads(p.read_text(encoding='utf-8'))
        for r in d.get('records') or []:
            if r.get('id'):out[r['id']]=r
    return out
def prepare()->dict[str,Any]:
    if FINAL.exists():raise ValueError('immutable D14 location artifact exists')
    im=verify_inventory();inventory=_read(FULLTEXT/'retrieval_inventory.jsonl');occ=_read(CONSOLIDATED/'candidate_occurrences.jsonl');oa=_oa_records();byfam=defaultdict(list)
    for r in occ:byfam[r['citation_family_id']].append(r)
    rows=[]
    for item in inventory:
        locations=[]
        if item.get('arxiv_id'):
            aid=item['arxiv_id'].split('v',1)[0];locations.append({'url':f'https://arxiv.org/pdf/{aid}','basis':'arxiv_public_pdf','license_status':'repository_terms'})
        for member in byfam[item['citation_family_id']]:
            if member['discovery_source']!='OpenAlex':continue
            record=oa.get(member['source_record_id']) or {};loc=record.get('primary_location') or {};url=loc.get('pdf_url') or ''
            if loc.get('is_oa') and _https_pdf(url):locations.append({'url':url,'basis':'frozen_openalex_primary_oa_pdf','license_status':str(loc.get('license') or 'openalex_is_oa')})
        if _https_pdf(item.get('record_url') or ''):locations.append({'url':item['record_url'],'basis':'frozen_metadata_direct_https_pdf','license_status':'requires_source_verification'})
        unique=[];seen=set()
        for loc in locations:
            if loc['url'] not in seen:seen.add(loc['url']);unique.append(loc)
        rows.append({'citation_family_id':item['citation_family_id'],'title':item['title'],'candidate_locations':unique,'location_status':'candidate_identified' if unique else 'lawful_location_discovery_pending'})
    rows.sort(key=lambda r:r['citation_family_id']);FINAL.mkdir(parents=True);p=FINAL/'location_candidates.jsonl';p.write_text(''.join(json.dumps(r,sort_keys=True,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8');counts=Counter(r['location_status'] for r in rows);basis=Counter(x['basis'] for r in rows for x in r['candidate_locations'])
    m={'status':'d14_local_location_resolution_complete','pipeline_version':VERSION,'protocol_version':'1.3','family_count':len(rows),'status_counts':dict(sorted(counts.items())),'location_basis_counts':dict(sorted(basis.items())),'inventory_manifest_sha256':sha256(FULLTEXT/'inventory_manifest.json'),'candidate_occurrences_sha256':sha256(CONSOLIDATED/'candidate_occurrences.jsonl'),'locations_sha256':sha256(p),'network_access_performed':False,'lawful_access_boundary':'Only frozen arXiv or OpenAlex-is_oa HTTPS PDF locations are automatically eligible; other routes require explicit verification.'}
    mp=FINAL/'locations_manifest.json';mp.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n',encoding='utf-8');(FINAL/'locations_manifest.json.sha256').write_text(f"{sha256(mp)}  locations_manifest.json\n",encoding='utf-8');return m
def verify()->dict[str,Any]:
    mp=FINAL/'locations_manifest.json';m=json.loads(mp.read_text());rows=_read(FINAL/'location_candidates.jsonl')
    if len(rows)!=m['family_count'] or sha256(FINAL/'location_candidates.jsonl')!=m['locations_sha256']:raise ValueError('D14 location artifact mismatch')
    if (FINAL/'locations_manifest.json.sha256').read_text().split()[0]!=sha256(mp):raise ValueError('D14 location sidecar mismatch')
    return m
def main()->int:
    p=argparse.ArgumentParser();p.add_argument('command',choices=('prepare','verify'));a=p.parse_args();print(json.dumps(prepare() if a.command=='prepare' else verify(),sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
