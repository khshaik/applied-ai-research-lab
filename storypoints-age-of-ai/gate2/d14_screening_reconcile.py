"""Reconcile isolated D14 passes and prepare separate adjudication."""
from __future__ import annotations
import argparse,json,shutil,tempfile
from collections import Counter
from pathlib import Path
from typing import Any
from gate2.citation_chasing import sha256
from gate2.d14_screening import FINAL as SCREEN,validate_pass,verify_packet

FINAL=SCREEN/"adjudication"
VERSION="d14-screening-reconcile/1.0.0"
def _read(p:Path)->list[dict[str,Any]]:return [json.loads(x) for x in p.read_text(encoding='utf-8').split('\n') if x]
def prepare()->dict[str,Any]:
    if FINAL.exists():raise ValueError('immutable D14 adjudication packet exists')
    va=validate_pass(SCREEN/'pass_a_decisions.jsonl','pass-a');vb=validate_pass(SCREEN/'pass_b_decisions.jsonl','pass-b');pm=verify_packet()
    a={r['family_id']:r for r in _read(SCREEN/'pass_a_decisions.jsonl')};b={r['family_id']:r for r in _read(SCREEN/'pass_b_decisions.jsonl')};families={}
    for s in pm['shards']:
        for r in _read(SCREEN/s['path']):families[r['family_id']]=r
    candidates=[];consensus=[];pairs=Counter()
    for fid in sorted(families):
        ar,br=a[fid],b[fid];pairs[f"{ar['decision']}|{br['decision']}"]+=1
        if ar['decision']!=br['decision'] or 'unclear' in {ar['decision'],br['decision']}:
            candidates.append({'family':families[fid],'pass_a':ar,'pass_b':br,'adjudication_reason':'disagreement' if ar['decision']!=br['decision'] else 'consensus_unclear'})
        else:consensus.append({'family_id':fid,'record_id':fid,'final_title_abstract_decision':ar['decision'],'decision_basis':'agent_consensus_no_unclear','pass_a_screening_sha256':va['sha256'],'pass_b_screening_sha256':vb['sha256']})
    FINAL.parent.mkdir(parents=True,exist_ok=True);st=Path(tempfile.mkdtemp(prefix='d14-adjudication-',dir=str(FINAL.parent)))
    try:
        ap=st/'adjudication_packet.jsonl';cp=st/'consensus_decisions.jsonl';ap.write_text(''.join(json.dumps(r,sort_keys=True,ensure_ascii=False)+'\n' for r in candidates),encoding='utf-8');cp.write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in consensus),encoding='utf-8')
        m={'status':'prepared_for_separate_adjudication','protocol_version':'1.3','pipeline_version':VERSION,'family_count':len(families),'pass_a':va,'pass_b':vb,'agent_concordance_count':sum(a[f]['decision']==b[f]['decision'] for f in families),'agent_concordance_rate':sum(a[f]['decision']==b[f]['decision'] for f in families)/len(families),'decision_pair_counts':dict(sorted(pairs.items())),'consensus_without_unclear_count':len(consensus),'adjudication_candidate_count':len(candidates),'adjudication_packet_sha256':sha256(ap),'consensus_decisions_sha256':sha256(cp),'interpretation_boundary':'AI-agent concordance, not human inter-rater reliability; all disagreement/unclear rows require a distinct adjudicator.'}
        mp=st/'reconciliation_manifest.json';mp.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n',encoding='utf-8');(st/'reconciliation_manifest.json.sha256').write_text(f"{sha256(mp)}  reconciliation_manifest.json\n",encoding='utf-8');st.rename(FINAL);return m
    except Exception:shutil.rmtree(st,ignore_errors=True);raise
def verify()->dict[str,Any]:
    mp=FINAL/'reconciliation_manifest.json';m=json.loads(mp.read_text());
    if m['pass_a']!=validate_pass(SCREEN/'pass_a_decisions.jsonl','pass-a') or m['pass_b']!=validate_pass(SCREEN/'pass_b_decisions.jsonl','pass-b'):raise ValueError('D14 pass binding drift')
    if sha256(FINAL/'adjudication_packet.jsonl')!=m['adjudication_packet_sha256'] or sha256(FINAL/'consensus_decisions.jsonl')!=m['consensus_decisions_sha256']:raise ValueError('D14 reconciliation hash mismatch')
    if m['consensus_without_unclear_count']+m['adjudication_candidate_count']!=m['family_count']:raise ValueError('D14 reconciliation conservation failure')
    if (FINAL/'reconciliation_manifest.json.sha256').read_text().split()[0]!=sha256(mp):raise ValueError('D14 reconciliation sidecar mismatch')
    return m
def main()->int:
    p=argparse.ArgumentParser();p.add_argument('command',choices=('prepare','verify'));a=p.parse_args();print(json.dumps(prepare() if a.command=='prepare' else verify(),sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
