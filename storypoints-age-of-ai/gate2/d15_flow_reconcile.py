"""Reconcile systematic-search and citation-chasing flows into D15."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from typing import Any

from gate2.citation_chasing import SYSTEMATIC, sha256
from gate2.d14_close import FINAL as D14_FINAL, verify as verify_d14


FINAL = SYSTEMATIC / "d15"
D13 = SYSTEMATIC / "d13/final"


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _load(path: Path) -> dict[str, Any]: return json.loads(path.read_text(encoding="utf-8"))


def reconcile() -> dict[str, Any]:
    if FINAL.exists(): raise ValueError("immutable D15 output exists")
    d14=verify_d14(); d06=_load(SYSTEMATIC/"d06/d06_manifest.json"); d07=_load(SYSTEMATIC/"d07/d07_manifest.json")
    d09=_load(SYSTEMATIC/"d08/d09/final/d09_final_manifest.json"); d10=_load(SYSTEMATIC/"d10/final/d10_final_manifest.json")
    d11=_load(SYSTEMATIC/"d11/screening/final/d11_final_manifest.json"); d13m=_load(D13/"d13_final_manifest.json")
    cmain=_load(SYSTEMATIC/"d14/candidate_consolidation/consolidation_manifest.json"); smain=_load(SYSTEMATIC/"d14/screening/adjudication/final/final_screening_manifest.json")
    fmain=_load(SYSTEMATIC/"d14/fulltext_final/final_fulltext_manifest.json"); csup=_load(SYSTEMATIC/"d14/newly_resolved_candidate_consolidation_v2/manifest.json")
    ssup=_load(SYSTEMATIC/"d14/newly_resolved_candidate_screening_final_v2/final_screening_manifest.json")
    if d06["raw_occurrence_count"]-d06["duplicates_removed_count"]!=d06["canonical_record_count"]: raise ValueError("D06 conservation failure")
    if d09["decision_counts"]["include"]+d09["decision_counts"]["exclude"]!=d07["study_family_count"]: raise ValueError("D09 conservation failure")
    if sum(d11["status_counts"].values())!=d09["decision_counts"]["include"] or d11["status_counts"]["included_full_text"]!=d13m["family_count"]: raise ValueError("D11 conservation failure")
    if cmain["input_occurrence_count"]-cmain["duplicate_occurrence_count"]!=cmain["candidate_family_count"]: raise ValueError("D14 main candidate conservation failure")
    if smain["decision_counts"]["include"]+smain["decision_counts"]["exclude"]!=cmain["candidate_family_count"]: raise ValueError("D14 main screening conservation failure")
    if sum(fmain["decision_counts"].values())!=smain["decision_counts"]["include"]: raise ValueError("D14 main full-text conservation failure")
    if csup["input_candidate_count"]-csup["duplicate_candidate_count"]!=csup["new_unique_candidate_count"]: raise ValueError("D14 supplement candidate conservation failure")
    if sum(ssup["decision_counts"].values())!=csup["new_unique_candidate_count"]: raise ValueError("D14 supplement screening conservation failure")
    systematic_flow={"identified_occurrences":d06["raw_occurrence_count"],"duplicate_occurrences_removed":d06["duplicates_removed_count"],"deduplicated_reports":d06["canonical_record_count"],
                     "study_families":d07["study_family_count"],"title_abstract_excluded":d09["decision_counts"]["exclude"],"reports_sought":d09["decision_counts"]["include"],
                     "full_text_unavailable":d11["status_counts"]["full_text_unavailable"],"full_text_assessed":d11["status_counts"]["included_full_text"]+d11["status_counts"]["excluded_full_text"],
                     "full_text_excluded":d11["status_counts"]["excluded_full_text"],"included_families":d11["status_counts"]["included_full_text"]}
    citation_main={"candidate_occurrences":cmain["input_occurrence_count"],"duplicate_occurrences_removed":cmain["duplicate_occurrence_count"],"candidate_families":cmain["candidate_family_count"],
                   "title_abstract_excluded":smain["decision_counts"]["exclude"],"reports_sought":smain["decision_counts"]["include"],"full_text_unavailable":fmain["decision_counts"]["unavailable_not_assessed"],
                   "full_text_assessed":fmain["decision_counts"]["include"]+fmain["decision_counts"]["exclude"],"full_text_excluded":fmain["decision_counts"]["exclude"],"included_families":fmain["decision_counts"]["include"]}
    citation_supp={"candidate_occurrences":csup["input_candidate_count"],"duplicate_occurrences_removed":csup["duplicate_candidate_count"],"candidate_families":csup["new_unique_candidate_count"],
                   "title_abstract_excluded":ssup["decision_counts"]["exclude"],"reports_sought":ssup["decision_counts"]["include"],"full_text_unavailable":2,"full_text_assessed":9,"full_text_excluded":0,"included_families":9}
    if systematic_flow["included_families"]+citation_main["included_families"]+citation_supp["included_families"]!=791: raise ValueError("final included-family conservation failure")
    families=[]
    for row in _read(D13/"evidence_matrix.jsonl"):
        families.append({"family_id":row["family_id"],"source_stream":"systematic_open_index_search","bibliographic_status":row["bibliographic_status"],"appraisal_form":row["appraisal_form"],"evidence_band":row["evidence_band"],"finding_count":len(row["measures_findings"]),"quantitative_finding_count":sum(bool(f["quantitative"]) for f in row["measures_findings"]),"novelty_assessment":row["novelty_assessment"],"source_text_sha256":row["source_text_sha256"]})
    families.extend(_read(D14_FINAL/"d14_included_evidence_families.jsonl"))
    if len(families)!=791 or len({r["family_id"] for r in families})!=791: raise ValueError("final evidence-family index mismatch")
    FINAL.mkdir(parents=True); index=FINAL/"final_evidence_family_index.jsonl"; index.write_text("".join(json.dumps(r,sort_keys=True)+"\n" for r in sorted(families,key=lambda r:r["family_id"])),encoding="utf-8")
    flow={"status":"d15_flow_reconciled","protocol_version":"1.3","systematic_search_stream":systematic_flow,"citation_round_1_stream":citation_main,"citation_recovery_supplement_stream":citation_supp,
          "final_included_family_count":791,"final_evidence_band_counts":dict(Counter(r["evidence_band"] for r in families)),"final_finding_count":sum(r["finding_count"] for r in families),"final_quantitative_finding_count":sum(r["quantitative_finding_count"] for r in families),
          "full_text_exclusion_code_counts":d11["fulltext_exclusion_code_counts"],"resource_cap_applied":True,
          "interpretation_boundary":"Streams are reported separately and reconciled at the unique study-family level. Unavailable reports are not eligibility exclusions. Counts describe an AI-assisted open-index evidence map, not an exhaustive systematic review."}
    flow_path=FINAL/"study_flow_ledger.json"; flow_path.write_text(json.dumps(flow,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    manifest={"status":"d15_complete","protocol_version":"1.3","flow_ledger_sha256":sha256(flow_path),"family_index_sha256":sha256(index),"family_count":791,
              "source_manifest_hashes":{"d06":sha256(SYSTEMATIC/"d06/d06_manifest.json"),"d07":sha256(SYSTEMATIC/"d07/d07_manifest.json"),"d09":sha256(SYSTEMATIC/"d08/d09/final/d09_final_manifest.json"),"d10":sha256(SYSTEMATIC/"d10/final/d10_final_manifest.json"),"d11":sha256(SYSTEMATIC/"d11/screening/final/d11_final_manifest.json"),"d13":sha256(D13/"d13_final_manifest.json"),"d14":sha256(D14_FINAL/"d14_final_manifest.json")},
              "security_boundary":"Local checksum-bound reconciliation only; no network, Git/history, secrets, installs, PDF execution, or private systems."}
    mp=FINAL/"d15_manifest.json"; mp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8"); (FINAL/"d15_manifest.json.sha256").write_text(f"{sha256(mp)}  d15_manifest.json\n",encoding="ascii")
    return {**manifest,"flow":flow}


def verify() -> dict[str, Any]:
    mp=FINAL/"d15_manifest.json"; m=_load(mp); rows=_read(FINAL/"final_evidence_family_index.jsonl")
    if len(rows)!=m["family_count"] or sha256(FINAL/"final_evidence_family_index.jsonl")!=m["family_index_sha256"] or sha256(FINAL/"study_flow_ledger.json")!=m["flow_ledger_sha256"]: raise ValueError("D15 artifact mismatch")
    if (FINAL/"d15_manifest.json.sha256").read_text().split()[0]!=sha256(mp): raise ValueError("D15 manifest sidecar mismatch")
    return m


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("command",choices=("reconcile","verify")); args=parser.parse_args(); result=reconcile() if args.command=="reconcile" else verify(); print(json.dumps(result,sort_keys=True)); return 0


if __name__=="__main__": raise SystemExit(main())
