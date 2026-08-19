"""Hardened, resumable D14 lawful public PDF retrieval."""
from __future__ import annotations
import argparse,hashlib,ipaddress,json,re,socket,ssl,time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError,URLError
from urllib.parse import urljoin,urlparse
from urllib.request import HTTPSHandler,HTTPRedirectHandler,ProxyHandler,Request,build_opener
from gate2.citation_chasing import OUTPUT,sha256
from gate2.d14_fulltext_locations import FINAL as LOCATIONS,verify as verify_locations
from gate2.d14_fulltext_locations_v2 import FINAL as LOCATIONS_V2,verify as verify_locations_v2
try:
    from gate2.d14_fulltext_locations_v3 import FINAL as LOCATIONS_V3,verify as verify_locations_v3
except ImportError:
    LOCATIONS_V3=None

FINAL=OUTPUT/"fulltext";RESULTS=FINAL/"results";PDFS=FINAL/"pdf";QUARANTINE=FINAL/"quarantine";VERSION="d14-secure-fulltext/1.2.0";MAX_BYTES=50*1024*1024;MAX_REDIRECTS=5;MAX_WORKERS=3
ACTIVE_NAMES=(b'JavaScript',b'JS',b'Launch',b'EmbeddedFile',b'RichMedia',b'AA')
ACTIVE_ACTIONS=(b'URI',b'GoToR',b'SubmitForm',b'ImportData',b'Sound',b'Movie',b'Rendition',b'JavaScript',b'Launch')
NAME_BOUNDARY=rb'(?=[\x00\x09\x0a\x0c\x0d\x20()<>{}\[\]/%])'
def _read(p:Path)->list[dict[str,Any]]:return [json.loads(x) for x in p.read_text(encoding='utf-8').split('\n') if x]
def _location_rows()->list[dict[str,Any]]:
    location_root=LOCATIONS_V3 if LOCATIONS_V3 and LOCATIONS_V3.exists() else LOCATIONS_V2 if LOCATIONS_V2.exists() else LOCATIONS
    verify_locations_v3() if LOCATIONS_V3 and location_root==LOCATIONS_V3 else verify_locations_v2() if location_root==LOCATIONS_V2 else verify_locations()
    return _read(location_root/'location_candidates.jsonl')
def _now()->str:return datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
def _atomic_json(path:Path,value:Any)->None:
    path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n',encoding='utf-8');tmp.replace(path)
def validate_public_https(url:str)->str:
    parsed=urlparse(url)
    if parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password:raise ValueError('URL must be credential-free HTTPS')
    if parsed.port not in (None,443):raise ValueError('nonstandard HTTPS port rejected')
    host=parsed.hostname.casefold().rstrip('.')
    if host=='localhost' or host.endswith(('.local','.internal','.localhost')):raise ValueError('local hostname rejected')
    addresses={info[4][0] for info in socket.getaddrinfo(host,443,type=socket.SOCK_STREAM)}
    if not addresses:raise ValueError('hostname has no address')
    for value in addresses:
        ip=ipaddress.ip_address(value)
        if not ip.is_global:raise ValueError('non-public destination rejected')
    return url
def active_indicators(data:bytes)->list[str]:
    found=[]
    for name in ACTIVE_NAMES:
        if re.search(rb'/'+name+NAME_BOUNDARY,data):found.append('/'+name.decode('ascii'))
    for action in ACTIVE_ACTIONS:
        if re.search(rb'/S\s*/'+action+NAME_BOUNDARY,data):found.append('/S /'+action.decode('ascii'))
    return sorted(set(found))
class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):return None
def _download(url:str,target:Path,timeout:int=45)->dict[str,Any]:
    opener=build_opener(ProxyHandler({}),HTTPSHandler(context=ssl.create_default_context()),_NoRedirect());current=url;redirects=[]
    for _ in range(MAX_REDIRECTS+1):
        validate_public_https(current)
        request=Request(current,headers={'User-Agent':'VDCM-THINKAI-2026/1.0 lawful-static-PDF-retrieval','Accept':'application/pdf,application/octet-stream;q=0.8'})
        try:response=opener.open(request,timeout=timeout);status=response.getcode()
        except HTTPError as exc:response=exc;status=exc.code
        if status in {301,302,303,307,308}:
            location=response.headers.get('Location');response.close()
            if not location:raise ValueError('redirect without location')
            next_url=urljoin(current,location);validate_public_https(next_url);redirects.append(next_url);current=next_url;continue
        if status!=200:
            retry=response.headers.get('Retry-After');response.close();return {'status':'http_failure','http_status':status,'retry_after':retry,'final_url':current,'redirect_count':len(redirects)}
        length=response.headers.get('Content-Length')
        if length and int(length)>MAX_BYTES:response.close();return {'status':'size_rejected','declared_bytes':int(length),'final_url':current,'redirect_count':len(redirects)}
        target.parent.mkdir(parents=True,exist_ok=True);tmp=target.with_suffix('.pdf.download.tmp');total=0;digest=hashlib.sha256()
        try:
            with tmp.open('wb') as handle:
                while True:
                    chunk=response.read(65536)
                    if not chunk:break
                    total+=len(chunk)
                    if total>MAX_BYTES:raise ValueError('stream exceeds safety limit')
                    digest.update(chunk);handle.write(chunk)
        except Exception:
            tmp.unlink(missing_ok=True);raise
        finally:response.close()
        data=tmp.read_bytes()
        if total<5000 or not data.startswith(b'%PDF-') or b'%%EOF' not in data[-8192:]:tmp.unlink(missing_ok=True);return {'status':'invalid_pdf_signature','bytes':total,'final_url':current,'redirect_count':len(redirects)}
        indicators=active_indicators(data)
        if indicators:
            QUARANTINE.mkdir(parents=True,exist_ok=True);q=QUARANTINE/target.name;tmp.replace(q)
            return {'status':'quarantined_active_content','bytes':total,'sha256':digest.hexdigest(),'active_indicators':indicators,'quarantine_path':str(q),'final_url':current,'redirect_count':len(redirects)}
        tmp.replace(target);return {'status':'retrieved_static_pdf','bytes':total,'sha256':digest.hexdigest(),'active_indicators':[],'pdf_path':str(target),'final_url':current,'redirect_count':len(redirects)}
    raise ValueError('redirect limit exceeded')
def _fetch_row(row:dict[str,Any])->dict[str,Any]:
    fid=row['citation_family_id'];rp=RESULTS/f'{fid}.json';attempts=[];terminal=None
    for loc in row['candidate_locations']:
        try:out=_download(loc['url'],PDFS/f'{fid}.pdf')
        except (HTTPError,URLError,OSError,ValueError,socket.gaierror,ssl.SSLError) as exc:out={'status':'network_or_policy_failure','error_type':type(exc).__name__}
        attempts.append({'basis':loc['basis'],'attempted_at_utc':_now(),**out})
        if out['status'] in {'retrieved_static_pdf','quarantined_active_content'}:terminal=out;break
        if out.get('http_status')==429:break
        time.sleep(0.4)
    result={'citation_family_id':fid,'status':(terminal or attempts[-1])['status'],'attempts':attempts,'pdf_path':(terminal or {}).get('pdf_path'),'pdf_sha256':(terminal or {}).get('sha256'),'bytes':(terminal or {}).get('bytes',0),'security_attestation':'Static HTTPS retrieval only; public-IP validation, bounded redirects/size, signature and active-content checks; no PDF execution.'}
    _atomic_json(rp,result);return result
def fetch(limit:int=10,workers:int=1)->dict[str,Any]:
    if limit<0:raise ValueError('limit must be nonnegative')
    if workers<1 or workers>MAX_WORKERS:raise ValueError(f'workers must be between 1 and {MAX_WORKERS}')
    rows=_location_rows();RESULTS.mkdir(parents=True,exist_ok=True);pending=[]
    for row in rows:
        if len(pending)>=limit:break
        if (RESULTS/f"{row['citation_family_id']}.json").exists() or not row['candidate_locations']:continue
        pending.append(row)
    if workers==1:
        for row in pending:_fetch_row(row);time.sleep(0.8)
    else:
        with ThreadPoolExecutor(max_workers=workers,thread_name_prefix='d14-public-retrieval') as pool:list(pool.map(_fetch_row,pending))
    attempted=len(pending)
    all_results=[json.loads(p.read_text()) for p in sorted(RESULTS.glob('CITFAM-*.json'))];counts=Counter(r['status'] for r in all_results)
    progress={'status':'d14_secure_retrieval_in_progress','pipeline_version':VERSION,'concurrency_workers':workers,'location_family_count':len(rows),'families_with_candidates':sum(bool(r['candidate_locations']) for r in rows),'families_attempted':len(all_results),'this_run_attempted':attempted,'result_counts':dict(sorted(counts.items())),'verified_pdf_count':sum(r['status']=='retrieved_static_pdf' for r in all_results),'quarantined_count':sum(r['status']=='quarantined_active_content' for r in all_results),'pdf_bytes':sum(r.get('bytes',0) for r in all_results if r['status']=='retrieved_static_pdf'),'result_hashes':{p.name:sha256(p) for p in sorted(RESULTS.glob('CITFAM-*.json'))},'security_boundary':'No authentication, paywall bypass, Git, secrets, installs, PDF execution, embedded actions, or private network destinations. Concurrency is capped at three unique-family workers.'}
    _atomic_json(FINAL/'retrieval_progress.json',progress);return progress
def verify_progress()->dict[str,Any]:
    p=FINAL/'retrieval_progress.json';m=json.loads(p.read_text());files=sorted(RESULTS.glob('CITFAM-*.json'))
    if len(files)!=m['families_attempted'] or {x.name:sha256(x) for x in files}!=m['result_hashes']:raise ValueError('D14 retrieval progress mismatch')
    for rp in files:
        r=json.loads(rp.read_text());pdf=r.get('pdf_path')
        if r['status']=='retrieved_static_pdf':
            path=Path(pdf)
            if not path.exists() or sha256(path)!=r['pdf_sha256'] or active_indicators(path.read_bytes()):raise ValueError(f'D14 retrieved PDF verification failed: {r["citation_family_id"]}')
    return m
def reassess_quarantine()->dict[str,Any]:
    moved=0;retained=0
    for q in sorted(QUARANTINE.glob('CITFAM-*.pdf')) if QUARANTINE.exists() else []:
        fid=q.stem;rp=RESULTS/f'{fid}.json';r=json.loads(rp.read_text());data=q.read_bytes();indicators=active_indicators(data)
        event={'detector_version':VERSION,'reassessed_at_utc':_now(),'previous_status':r.get('status'),'exact_active_indicators':indicators,'original_quarantine_sha256':sha256(q)}
        if indicators:
            event['outcome']='retained_quarantine';retained+=1
        else:
            PDFS.mkdir(parents=True,exist_ok=True);target=PDFS/q.name;q.replace(target);event['outcome']='released_as_static_pdf';r['status']='retrieved_static_pdf';r['pdf_path']=str(target);r['pdf_sha256']=sha256(target);r['bytes']=target.stat().st_size;moved+=1
        r.setdefault('quarantine_reassessments',[]).append(event);_atomic_json(rp,r)
    all_results=[json.loads(p.read_text()) for p in sorted(RESULTS.glob('CITFAM-*.json'))];counts=Counter(r['status'] for r in all_results)
    location_rows=_location_rows();progress={'status':'d14_secure_retrieval_in_progress','pipeline_version':VERSION,'location_family_count':len(location_rows),'families_with_candidates':sum(bool(r['candidate_locations']) for r in location_rows),'families_attempted':len(all_results),'this_run_attempted':0,'result_counts':dict(sorted(counts.items())),'verified_pdf_count':sum(r['status']=='retrieved_static_pdf' for r in all_results),'quarantined_count':sum(r['status']=='quarantined_active_content' for r in all_results),'pdf_bytes':sum(r.get('bytes',0) for r in all_results if r['status']=='retrieved_static_pdf'),'result_hashes':{p.name:sha256(p) for p in sorted(RESULTS.glob('CITFAM-*.json'))},'security_boundary':'No authentication, paywall bypass, Git, secrets, installs, PDF execution, embedded actions, or private network destinations.','quarantine_reassessment':{'released':moved,'retained':retained,'detector_version':VERSION}}
    _atomic_json(FINAL/'retrieval_progress.json',progress);return progress
def main()->int:
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True);f=sub.add_parser('fetch');f.add_argument('--limit',type=int,default=10);f.add_argument('--workers',type=int,default=1);sub.add_parser('verify-progress');sub.add_parser('reassess-quarantine');a=p.parse_args();result=fetch(a.limit,a.workers) if a.command=='fetch' else verify_progress() if a.command=='verify-progress' else reassess_quarantine();print(json.dumps(result,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
