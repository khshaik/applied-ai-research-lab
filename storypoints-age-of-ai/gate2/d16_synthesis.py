"""Produce D16 descriptive synthesis and bounded novelty outputs."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from typing import Any

from gate2.citation_chasing import SYSTEMATIC, sha256
from gate2.d15_flow_reconcile import FINAL as D15, verify as verify_d15


FINAL = SYSTEMATIC / "d16_v2"
SOURCES = [
    ("systematic_open_index_search", SYSTEMATIC / "d13/final/evidence_matrix.jsonl"),
    ("citation_round_1", SYSTEMATIC / "d14/evidence_extraction/final/final_evidence_extraction.jsonl"),
    ("citation_recovery_supplement", SYSTEMATIC / "d14/newly_resolved_extraction_v2/extraction.jsonl"),
]
BAND_WEIGHT = {"high": 3, "moderate": 2, "low_contextual": 1}
FIELD_ALIASES = {
    "estimation_comparator": "baseline_estimator_comparator",
    "human_workload_or_oversight": "human_effort_time_workload",
    "planning_or_delivery": "delivery_flow",
    "readiness_gates": "readiness_gate",
    "reported_AI_assisted_software_finding": "principal_reported_finding",
    "review_or_quality": "review_quality",
    "review_testing_security_quality": "review_quality",
    "security_or_compliance": "review_quality",
    "testing_or_validation": "review_quality",
    "time_or_productivity": "human_effort_time_workload",
}
NATURE_ALIASES = {"self_reported": "self-reported"}


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _claim_candidates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    claim_fields = {
        "CL-001": {"human_effort_time_workload", "elapsed_time", "delivery_flow", "review_quality", "prompt_refinement_validation"},
        "CL-002": {"baseline_estimator_comparator", "prospective_retrospective_estimate"},
        "CL-003": {"human_effort_time_workload", "prompt_refinement_validation", "prospective_retrospective_estimate"},
        "CL-004": {"readiness_gate", "delivery_flow", "review_quality"},
    }
    candidates=[]
    for claim_id, fields in claim_fields.items():
        pool=[]
        for row in rows:
            title=(row["bibliographic_status"].get("title") or "").casefold()
            for finding in row["measures_findings"]:
                canonical_field = FIELD_ALIASES.get(finding["field_name"], finding["field_name"])
                if canonical_field not in fields: continue
                special=0
                if claim_id=="CL-003" and any(term in title for term in ("hybrid intelligence effort","human-ai effort","effort estimation")): special=4
                if claim_id=="CL-004" and any(term in title for term in ("agile v","lifecycle","life cycle","gate","orchestrat")): special=4
                score=BAND_WEIGHT[row["evidence_band"]]*10+int(bool(finding["quantitative"]))*3+int(finding["data_nature"] in {"observed","mixed"})*2+special
                pool.append((score,row,finding))
        used=set()
        for score,row,finding in sorted(pool,key=lambda x:(-x[0],x[1]["family_id"],x[2]["finding_id"])):
            if row["family_id"] in used: continue
            used.add(row["family_id"])
            b=row["bibliographic_status"]
            candidates.append({"claim_id":claim_id,"rank":len(used),"family_id":row["family_id"],"title":b.get("title"),"year":b.get("year"),"doi":b.get("doi"),"arxiv_id":b.get("arxiv_id"),
                               "evidence_band":row["evidence_band"],"finding_id":finding["finding_id"],"field_name":canonical_field,"source_field_name":finding["field_name"],"finding_value":finding["value"],"source_locator":finding["source_locator"],
                               "quantitative":finding["quantitative"],"reported_estimate":finding.get("reported_estimate"),"limitations":finding.get("limitations"),"selection_score":score,
                               "confirmation_status":"pending_accountable_author_D17"})
            if len(used)==5: break
    return candidates


def build() -> dict[str, Any]:
    if FINAL.exists(): raise ValueError("immutable D16 output exists")
    d15=verify_d15(); rows=[]
    for stream,path in SOURCES:
        for row in _read(path): row=dict(row); row["_source_stream"]=stream; rows.append(row)
    if len(rows)!=791 or len({r["family_id"] for r in rows})!=791: raise ValueError("D16 evidence population mismatch")
    lifecycle=Counter(); constructs={key:Counter() for key in ("PDD","RHTD","SAE","ERS","ARC","RCP","CQD","VDC")}; findings=Counter(); nature=Counter(); direction=Counter(); years=Counter(); forms=Counter(); bands=Counter(); streams=Counter()
    overlap=[]
    for row in rows:
        forms[row["appraisal_form"]]+=1; bands[row["evidence_band"]]+=1; streams[row["_source_stream"]]+=1
        year=row["bibliographic_status"].get("year"); years[str(year) if year else "unknown"]+=1
        for key,value in row["lifecycle_stages"].items():
            if value["present"]: lifecycle[key]+=1
        for key,value in row["vdcm_constructs"].items(): constructs[key][value["status"]]+=1
        for finding in row["measures_findings"]:
            findings[FIELD_ALIASES.get(finding["field_name"], finding["field_name"])]+=1
            nature[NATURE_ALIASES.get(finding["data_nature"], finding["data_nature"])]+=1; direction[finding["direction"]]+=1
        dims=row["novelty_assessment"]["dimensions"]; status_counts=Counter(v["status"] for v in dims.values()); score=status_counts["met"]*2+status_counts["partial"]
        b=row["bibliographic_status"]
        overlap.append({"family_id":row["family_id"],"title":b.get("title"),"year":b.get("year"),"doi":b.get("doi"),"arxiv_id":b.get("arxiv_id"),"source_stream":row["_source_stream"],"evidence_band":row["evidence_band"],
                        "same_planning_use":row["novelty_assessment"]["same_planning_use"],"novelty_risk":row["novelty_assessment"]["novelty_risk"],"weighted_overlap_score":score,
                        "dimensions":dims,"all_five_met_same_use":all(v["status"]=="met" for v in dims.values()) and row["novelty_assessment"]["same_planning_use"]=="yes"})
    overlap.sort(key=lambda r:(-r["weighted_overlap_score"],r["family_id"]))
    duplicates=[r["family_id"] for r in overlap if r["all_five_met_same_use"]]
    if duplicates: raise ValueError("D16 novelty stop rule triggered")
    candidates=_claim_candidates(rows)
    summary={"status":"d16_synthesis_complete_pending_D17_citation_confirmation","protocol_version":"1.3","family_count":791,"finding_count":sum(len(r["measures_findings"]) for r in rows),
             "quantitative_finding_count":sum(bool(f["quantitative"]) for r in rows for f in r["measures_findings"]),"source_stream_counts":dict(streams),"evidence_band_counts":dict(bands),"appraisal_form_counts":dict(forms),
             "lifecycle_stage_coverage_counts":dict(lifecycle),"vdcm_construct_status_counts":{k:dict(v) for k,v in constructs.items()},"finding_field_counts":dict(findings),"finding_data_nature_counts":dict(nature),"finding_direction_counts":dict(direction),"publication_year_counts":dict(sorted(years.items())),
             "novelty_dimension_counts":dict(Counter(v["status"] for r in overlap for v in r["dimensions"].values())),"same_planning_use_counts":dict(Counter(r["same_planning_use"] for r in overlap)),
             "substantively_duplicative_family_ids":duplicates,"closest_overlap_family_count":sum(r["weighted_overlap_score"]>0 for r in overlap),
             "bounded_novelty_conclusion":"No substantively duplicative framework was identified within the predeclared open scholarly indexes, repositories, and citation networks searched through the stated cutoff date and reported resource cap.",
             "interpretation_boundaries":["Coverage frequencies are descriptive and are not effect sizes or evidence votes.","Technical quality outcomes do not validate cognitive workload.","Synthetic simulation establishes conditional mechanism behavior only, not organizational superiority.","All material citations and locators remain pending accountable-author confirmation at D17.","The conclusion is bounded by open-index coverage, lawful full-text availability, API failures, inaccessible subscription databases, and the approved citation-chasing resource cap."]}
    FINAL.mkdir(parents=True); sp=FINAL/"evidence_synthesis_summary.json"; sp.write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    op=FINAL/"overlap_matrix.jsonl"; op.write_text("".join(json.dumps(r,sort_keys=True)+"\n" for r in overlap),encoding="utf-8")
    cp=FINAL/"material_citation_candidates.jsonl"; cp.write_text("".join(json.dumps(r,sort_keys=True)+"\n" for r in candidates),encoding="utf-8")
    md=FINAL/"D16_EVIDENCE_SYNTHESIS.md"
    top_lifecycle=", ".join(f"{k} ({v})" for k,v in lifecycle.most_common())
    top_findings=", ".join(f"{k} ({v})" for k,v in findings.most_common())
    md.write_text(f"""# D16 Evidence Synthesis and Bounded Novelty Conclusion

Status: complete, pending D17 accountable-author confirmation of material citations.

## Evidence-map population

The reconciled evidence map contains **791 unique study families** and **{summary['finding_count']:,} source-located findings**, including **{summary['quantitative_finding_count']:,} quantitative findings**. Evidence bands are **{bands['high']} high**, **{bands['moderate']} moderate**, and **{bands['low_contextual']} low/contextual**. These bands govern narrative weight; they are not eligibility decisions or additive certainty scores.

## Coverage profile

Lifecycle coverage is descriptive: {top_lifecycle}. Finding categories are: {top_findings}. Frequencies show where the accessible corpus concentrates; they do not demonstrate effect direction or magnitude.

## Framework overlap

Across {791*5:,} family-by-dimension judgments, the matrix contains **{summary['novelty_dimension_counts'].get('met',0)} met**, **{summary['novelty_dimension_counts'].get('partial',0)} partial**, and **{summary['novelty_dimension_counts'].get('not_met',0)} not-met** assessments. No study family met all five dimensions for the same pre-commitment planning use. Existing work therefore constrains and grounds the proposed framework but does not duplicate its complete role-stage demand, capacity/readiness/dependency, touch-versus-queue, and verified-completion forecast target.

## Bounded conclusion

> {summary['bounded_novelty_conclusion']}

This is not a claim that no prior research exists or that all relevant literature was searched. Subscription databases were unavailable; lawful full texts were unavailable for some candidates; five Semantic Scholar seeds remained API failures; seven source no-matches remained; and recursive citation chasing from the 221 D14 inclusions was not executed under the approved prospective cap.

## D17 boundary

The material-citation candidate ledger supplies ranked source-located candidates for author review. No outcome-bearing manuscript citation is publication-ready until its exact support is confirmed at D17.
""",encoding="utf-8")
    manifest={"status":"d16_v2_complete_pending_D17","protocol_version":"1.3","normalization_note":"Legacy extraction field/data-nature aliases were mapped to the canonical D14 vocabulary for descriptive aggregation only; source records remain unchanged.","d15_manifest_sha256":sha256(D15/"d15_manifest.json"),"source_hashes":{p.name:sha256(p) for _,p in SOURCES},
              "summary_sha256":sha256(sp),"overlap_matrix_sha256":sha256(op),"material_candidates_sha256":sha256(cp),"narrative_sha256":sha256(md),"family_count":791,"candidate_citation_count":len(candidates),
              "security_boundary":"Local checksum-bound synthesis only; no network, Git/history, secrets, installs, PDF execution, or private systems."}
    mp=FINAL/"d16_manifest.json"; mp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8"); (FINAL/"d16_manifest.json.sha256").write_text(f"{sha256(mp)}  d16_manifest.json\n",encoding="ascii")
    return {**manifest,"summary":summary}


def verify() -> dict[str, Any]:
    mp=FINAL/"d16_manifest.json"; m=json.loads(mp.read_text()); files={"summary_sha256":"evidence_synthesis_summary.json","overlap_matrix_sha256":"overlap_matrix.jsonl","material_candidates_sha256":"material_citation_candidates.jsonl","narrative_sha256":"D16_EVIDENCE_SYNTHESIS.md"}
    if any(sha256(FINAL/name)!=m[key] for key,name in files.items()) or (FINAL/"d16_manifest.json.sha256").read_text().split()[0]!=sha256(mp): raise ValueError("D16 artifact mismatch")
    if len(_read(FINAL/"overlap_matrix.jsonl"))!=m["family_count"]: raise ValueError("D16 overlap population mismatch")
    return m


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("command",choices=("build","verify")); args=parser.parse_args(); result=build() if args.command=="build" else verify(); print(json.dumps(result,sort_keys=True)); return 0


if __name__=="__main__": raise SystemExit(main())
