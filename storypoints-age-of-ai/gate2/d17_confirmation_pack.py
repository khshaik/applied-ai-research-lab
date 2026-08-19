"""Build the accountable-author material-citation confirmation pack."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from gate2.citation_chasing import ROOT, SYSTEMATIC, sha256
from gate2.d16_synthesis import FINAL as D16, verify as verify_d16


FINAL = SYSTEMATIC / "d17"
EVIDENCE_SOURCES = [SYSTEMATIC/"d13/final/evidence_matrix.jsonl", SYSTEMATIC/"d14/evidence_extraction/final/final_evidence_extraction.jsonl", SYSTEMATIC/"d14/newly_resolved_extraction_v2/extraction.jsonl"]
SELECTIONS = {
    "CL-001": [("FAM-01886e2b8b8d2e755658","F1"),("FAM-8c75e12ec62f0b5842d6","F1"),("FAM-8c75e12ec62f0b5842d6","F2"),("CITFAM-667f8d892a5d11b62016","F4"),("CITFAM-667f8d892a5d11b62016","F5")],
    "CL-002": [("FAM-603d94d0b63da5961ba1","F1"),("FAM-603d94d0b63da5961ba1","F2"),("FAM-65283040904dbb9cd0e4","F4")],
    "CL-003": [("FAM-a640303a39a1b2b83393","F1"),("FAM-a640303a39a1b2b83393","F2"),("FAM-341a4a5dcacb866b6f8c","F1"),("FAM-341a4a5dcacb866b6f8c","F2")],
    "CL-004": [("FAM-060356fefa5c43ff3355","F1"),("FAM-060356fefa5c43ff3355","F2"),("FAM-ece31c9dcde367d342ea","F1"),("FAM-ece31c9dcde367d342ea","F3"),("FAM-21732030d4fa145cc1da","F1")],
}
CLAIMS = {
    "CL-001":"AI assistance changes activities heterogeneously; implementation or documentation gains do not justify assuming proportional end-to-end acceleration.",
    "CL-002":"Story Points and agile effort methods remain planning comparators, but the mapped evidence does not show that a scalar explicitly represents role-stage queues and evidence readiness.",
    "CL-003":"HIE and its conceptual predecessor already model LLM context, transformation/interaction and human oversight; VDCM treats them as foundations, not inventions of this paper.",
    "CL-004":"Existing lifecycle, gate, orchestration and agentic-cost frameworks constrain novelty; gates and human-in-the-loop costing are not new contributions.",
    "CL-005":"The proposed contribution is narrowly differentiated by the combined pre-commitment, multi-role lifecycle, touch/queue, capacity/readiness/dependency and verified-completion forecast target.",
    "CL-006":"No substantively duplicative framework was identified within the predeclared open sources and citation network through the cutoff and approved resource cap.",
    "CL-007":"Comparative forecast performance varies across the declared developmental synthetic worlds.",
    "CL-008":"Simpler comparators outperform the proposed model in some developmental synthetic scenarios.",
    "CL-009":"Developmental parameter-recovery absolute errors are 0.035693 and 0.075802.",
    "CL-010":"Route B cannot validate human cognition, organizational calibration, causal impact or ROI.",
}


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def build() -> dict[str, Any]:
    if FINAL.exists(): raise ValueError("immutable D17 pack exists")
    d16=verify_d16(); by_family={}; source_path={}
    for path in EVIDENCE_SOURCES:
        for row in _read(path): by_family[row["family_id"]]=row; source_path[row["family_id"]]=path
    records=[]
    for claim_id,claim in CLAIMS.items():
        supports=[]
        for fid,finding_id in SELECTIONS.get(claim_id,[]):
            row=by_family[fid]; finding=next(f for f in row["measures_findings"] if f["finding_id"]==finding_id); b=row["bibliographic_status"]
            supports.append({"support_type":"external_study","family_id":fid,"finding_id":finding_id,"title":b.get("title"),"year":b.get("year"),"doi":b.get("doi"),"arxiv_id":b.get("arxiv_id"),"evidence_band":row["evidence_band"],
                             "source_locator":finding["source_locator"],"finding_value":finding["value"],"reported_estimate":finding.get("reported_estimate"),"limitations":finding.get("limitations"),"source_extraction_path":str(source_path[fid]),"source_extraction_sha256":sha256(source_path[fid]),"source_text_sha256":row["source_text_sha256"]})
        if claim_id in {"CL-005","CL-006"}:
            supports.append({"support_type":"internal_evidence_map_result","artifact":str(D16/("overlap_matrix.jsonl" if claim_id=="CL-005" else "evidence_synthesis_summary.json")),"sha256":sha256(D16/("overlap_matrix.jsonl" if claim_id=="CL-005" else "evidence_synthesis_summary.json")),"locator":"family-level five-dimension matrix" if claim_id=="CL-005" else "bounded_novelty_conclusion and interpretation_boundaries"})
        if claim_id in {"CL-007","CL-008"}:
            for rel in ("scenario_summary.csv","scenario_model_brier.csv"):
                p=ROOT/"papers/thinkai-2026/results/developmental_simulation_v2"/rel; supports.append({"support_type":"internal_simulation_result","artifact":str(p),"sha256":sha256(p),"locator":"scenario rows and comparator Brier summaries"})
        if claim_id=="CL-009":
            p=ROOT/"simulation/output/development/parameter_recovery.csv"; supports.append({"support_type":"internal_simulation_result","artifact":str(p),"sha256":sha256(p),"locator":"recovery_service_low and recovery_service_high rows"})
        if claim_id=="CL-010":
            for p,locator in ((ROOT/"research-design/02_systematic_review_protocol.md","Route B and AI-assisted evidence-map boundaries"),(ROOT/"papers/thinkai-2026/results/developmental_simulation_v2/report_manifest.json","interpretation_boundary")):
                supports.append({"support_type":"method_boundary","artifact":str(p),"sha256":sha256(p),"locator":locator})
        records.append({"claim_id":claim_id,"material_claim":claim,"support":supports,"confirmation_status":"pending","accountable_author":"pending","confirmation_date":None,"author_notes":None})
    FINAL.mkdir(parents=True); ledger=FINAL/"material_claim_confirmation.jsonl"; ledger.write_text("".join(json.dumps(r,sort_keys=True)+"\n" for r in records),encoding="utf-8")
    md=FINAL/"D17_AUTHOR_CONFIRMATION.md"; lines=["# D17 Accountable-Author Material-Citation Confirmation","","Status: **Pending author confirmation**","","Review each claim and its listed source locator in the checksum-bound ledger. Confirm only that the cited evidence supports the bounded wording; do not infer causality, cognitive load, or universal organizational benefit.",""]
    for record in records:
        lines.extend([f"## {record['claim_id']}","",record["material_claim"],"",f"Decision: [ ] Confirm  [ ] Revise  [ ] Reject",""])
        for support in record["support"]:
            if support["support_type"]=="external_study":
                lines.append(f"- `{support['family_id']}/{support['finding_id']}` — {support['title']} ({support.get('year') or 'year unavailable'}), `{support['source_locator']}`, DOI/arXiv: `{support.get('doi') or support.get('arxiv_id') or 'none'}`, band: `{support['evidence_band']}`")
            else: lines.append(f"- `{support['support_type']}` — `{support['artifact']}`, locator: {support['locator']}")
        lines.append("")
    lines.extend(["## Approval phrase","","> Confirm D17 material claims CL-001 through CL-010 as bounded in the confirmation pack.","", "If any item needs revision, identify its claim ID and requested wording."])
    md.write_text("\n".join(lines)+"\n",encoding="utf-8")
    manifest={"status":"d17_confirmation_pack_ready","protocol_version":"1.3","claim_count":10,"external_support_count":sum(len(SELECTIONS.get(k,[])) for k in CLAIMS),"ledger_sha256":sha256(ledger),"review_document_sha256":sha256(md),"d16_manifest_sha256":sha256(D16/"d16_manifest.json"),
              "release_rule":"No material claim is publication-ready until the accountable author confirms its wording and exact support.","security_boundary":"Local checksum-bound pack generation only; no network, Git/history, secrets, installs, PDF execution, or private systems."}
    mp=FINAL/"d17_manifest.json"; mp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8"); (FINAL/"d17_manifest.json.sha256").write_text(f"{sha256(mp)}  d17_manifest.json\n",encoding="ascii"); return manifest


def verify() -> dict[str, Any]:
    mp=FINAL/"d17_manifest.json"; m=json.loads(mp.read_text()); rows=_read(FINAL/"material_claim_confirmation.jsonl")
    if len(rows)!=10 or {r["claim_id"] for r in rows}!={f"CL-{i:03d}" for i in range(1,11)} or sha256(FINAL/"material_claim_confirmation.jsonl")!=m["ledger_sha256"] or sha256(FINAL/"D17_AUTHOR_CONFIRMATION.md")!=m["review_document_sha256"]: raise ValueError("D17 pack mismatch")
    if (FINAL/"d17_manifest.json.sha256").read_text().split()[0]!=sha256(mp): raise ValueError("D17 manifest sidecar mismatch")
    return m


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("command",choices=("build","verify")); args=parser.parse_args(); result=build() if args.command=="build" else verify(); print(json.dumps(result,sort_keys=True)); return 0


if __name__=="__main__": raise SystemExit(main())
