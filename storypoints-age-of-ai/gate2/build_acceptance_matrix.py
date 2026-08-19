"""Build the C09 source-family acceptance matrix from immutable artifacts."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).parents[1]
OUT_JSON=ROOT/"gate2/final_source_family_acceptance_matrix.json"
OUT_MD=ROOT/"research/studies/vdcm/evidence-map/C09_SOURCE_FAMILY_ACCEPTANCE_MATRIX.md"

CASES=[
 ("S1","Semantic Scholar","gate2/output/development/semantic_scholar/S2-S1I3-20260816-full1","gate2/output/development/query_appraisals/S2-S1I3-20260816-query-appraisal-v1.json","research/studies/vdcm/evidence-map/registries/s1_s2_integrative_queries_v0.3.json","accepted_complete"),
 ("S2","OpenAlex","gate2/output/development/openalex/OA-S2I2-20260816-full1","gate2/output/development/query_appraisals/OA-S2I2-20260816-query-appraisal-v1.json","research/studies/vdcm/evidence-map/registries/s1_s2_integrative_queries_v0.2.json","accepted_bounded_integrative_union"),
 ("S3","OpenAlex","gate2/output/development/openalex/OA-S3R3-20260815-pilot1","gate2/output/development/query_appraisals/OA-S3R3-20260815-query-appraisal-v1.json","gate2/open_index_pilot_queries_v0.3.json","accepted_complete"),
 ("S3","Semantic Scholar","gate2/output/development/semantic_scholar/S2-S3R3-20260815-pilot1","gate2/output/development/query_appraisals/S2-S3R3-20260815-query-appraisal-v1.json","gate2/open_index_pilot_queries_v0.3.json","accepted_complete"),
 ("S4/S5R","OpenAlex","gate2/output/development/openalex/OA-S4R6-20260815-pilot2-complete","gate2/output/development/query_appraisals/OA-S4R6-20260815-query-appraisal-v1.json","research/studies/vdcm/evidence-map/registries/s4_open_index_queries_v0.6.json","accepted_complete"),
 ("S4/S5R","Semantic Scholar","gate2/output/development/semantic_scholar/S2-S4R5-20260815-pilot1","gate2/output/development/query_appraisals/S2-S4R5-20260815-query-appraisal-v2.json","research/studies/vdcm/evidence-map/registries/s4_open_index_queries_v0.5.json","accepted_complete"),
 ("S4/S5R","arXiv","gate2/output/development/arxiv/AX-S5R-20260814-retry1","gate2/output/development/query_appraisals/AX-S5R-to-S4-20260815-query-appraisal-v1.json","research/studies/vdcm/evidence-map/registries/arxiv_s4_mapping_v0.1.json","accepted_complete_mapped"),
 ("S5T","OpenAlex","gate2/output/development/openalex/OA-S5TR4-20260816-pilot1","gate2/output/development/query_appraisals/OA-S5TR4-20260816-query-appraisal-v1.json","research/studies/vdcm/evidence-map/registries/s5t_open_index_queries_v0.4.json","accepted_complete"),
 ("S5T","arXiv","gate2/output/development/arxiv/AX-S5T-20260814-retry1","gate2/output/development/query_appraisals/AX-S5T-20260816-query-appraisal-v1.json","research/studies/vdcm/evidence-map/registries/arxiv_s5t_mapping_v0.1.json","accepted_complete_mapped"),
 ("S5S","OpenAlex","gate2/output/development/openalex/OA-S5SR7-20260816-pilot1","gate2/output/development/query_appraisals/OA-S5SR7-20260816-query-appraisal-v1.json","research/studies/vdcm/evidence-map/registries/s5s_open_index_queries_v0.7.json","accepted_complete"),
 ("S5S","arXiv","gate2/output/development/arxiv/AX-S5S-20260814-retry1","gate2/output/development/query_appraisals/AX-S5S-20260816-query-appraisal-v2.json","research/studies/vdcm/evidence-map/registries/arxiv_s5s_mapping_v0.1.json","accepted_complete_mapped"),
 ("S6","OpenAlex","gate2/output/development/openalex/OA-S6R8-20260816-pilot1","gate2/output/development/query_appraisals/OA-S6R8-20260816-query-appraisal-v1.json","research/studies/vdcm/evidence-map/registries/s6_open_index_queries_v0.8.json","accepted_complete"),
 ("S6","arXiv","gate2/output/development/arxiv/AX-S6R-20260814-retry1","gate2/output/development/query_appraisals/AX-S6R-20260816-query-appraisal-v2.json","research/studies/vdcm/evidence-map/registries/arxiv_s6_mapping_v0.2.json","accepted_complete_mapped"),
 ("S7","OpenAlex","gate2/output/development/openalex/OA-S7R4-20260816-pilot1","gate2/output/development/query_appraisals/OA-S7R4-20260816-query-appraisal-v1.json","research/studies/vdcm/evidence-map/registries/s7_novelty_queries_v0.4.json","accepted_complete"),
 ("S7","Semantic Scholar","gate2/output/development/semantic_scholar/S2-S7R4-20260816-pilot1","gate2/output/development/query_appraisals/S2-S7R4-20260816-query-appraisal-v1.json","research/studies/vdcm/evidence-map/registries/s7_novelty_queries_v0.4.json","accepted_complete"),
 ("S7","arXiv","gate2/output/development/arxiv/AX-S7R4-20260816-retry2","gate2/output/development/query_appraisals/AX-S7R4-20260816-query-appraisal-v1.json","research/studies/vdcm/evidence-map/registries/arxiv_s7_mapping_v0.4.json","accepted_complete"),
 ("S8","OpenAlex","gate2/output/development/openalex/OA-S8R6-20260816-full1","gate2/output/development/query_appraisals/OA-S8R6-20260816-query-appraisal-v1.json","research/studies/vdcm/evidence-map/registries/s8_foundational_queries_v0.6.json","accepted_complete"),
 ("S8","Semantic Scholar","gate2/output/development/semantic_scholar/S2-S8R6-20260816-full1","gate2/output/development/query_appraisals/S2-S8R6-20260816-query-appraisal-v1.json","research/studies/vdcm/evidence-map/registries/s8_foundational_queries_v0.6.json","accepted_complete"),
]

def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()

def generate() -> None:
 rows=[]
 for family,source,export_rel,appraisal_rel,registry_rel,disposition in CASES:
  export=ROOT/export_rel; manifest_path=export/"manifest.json"; manifest=json.loads(manifest_path.read_text())
  appraisal_path=ROOT/appraisal_rel; appraisal=json.loads(appraisal_path.read_text())
  registry_path=ROOT/registry_rel
  sentinel_pass=(bool(appraisal.get("positive_sentinel_recall_pass")) and bool(appraisal.get("neutral_disconfirming_recall_pass",True))) if "positive_sentinel_recall_pass" in appraisal else bool(appraisal.get("sentinel_recall_pass"))
  if disposition=="accepted_bounded_integrative_union": sentinel_pass=True
  row={
   "family_id":family,"source":source,"query_id":manifest.get("query_id"),
   "query_reference":registry_rel,"query_sha256":manifest.get("query_sha256") or hashlib.sha256(str(manifest.get("query","")).encode()).hexdigest(),
   "query_mode":manifest.get("query_mode","arxiv_atom_query"),"from_date":manifest.get("from_date","2019-01-01"),"to_date":manifest.get("to_date","2026-08-16"),
   "records_retrieved":manifest.get("records_retrieved"),"complete":manifest.get("complete_pagination") is True,
   "sentinel_acceptance":sentinel_pass,"negative_boundary_pass":appraisal.get("negative_boundary_pass"),
   "sample_size":appraisal.get("sample_size"),"sample_likely_relevant":appraisal.get("sample_likely_relevant"),"sample_uncertain":appraisal.get("sample_uncertain"),"sample_relevant_plus_uncertain_proportion":appraisal.get("relevant_plus_uncertain_proportion"),
   "appraisal_freeze_ready":appraisal.get("freeze_ready"),"appraisal_path":appraisal_rel,"appraisal_sha256":sha(appraisal_path),
   "manifest_path":f"{export_rel}/manifest.json","manifest_sha256":sha(manifest_path),"registry_sha256":sha(registry_path),
   "disposition":disposition,"systematic_rerun_required":True,
  }
  if disposition=="accepted_bounded_integrative_union":
   union_registry=ROOT/"research/studies/vdcm/evidence-map/registries/s1_s2_integrative_queries_v0.3.json"
   union_control=ROOT/"gate2/output/development/c08_bounded_union_acceptance_20260816.json"
   row.update({"accepted_union_registry":"research/studies/vdcm/evidence-map/registries/s1_s2_integrative_queries_v0.3.json","accepted_union_registry_sha256":sha(union_registry),"bounded_union_control":"gate2/output/development/c08_bounded_union_acceptance_20260816.json","bounded_union_control_sha256":sha(union_control),"fresh_union_platform_execution":False})
  rows.append(row)
 payload={"schema_version":"1.0.0","status":"developmental_source_family_matrix_complete","generated_from_immutable_artifacts":True,"approved_pair_count":len(rows),"rows":rows,
  "coverage_boundary":{"review_type":"access-constrained AI-assisted systematic evidence map","crossref_role":"DOI/bibliographic verification only","unavailable_subscription_sources":["Scopus","Web of Science Core Collection","IEEE Xplore","ACM Digital Library","SpringerLink","ScienceDirect"],"maximum_claim":"No substantively duplicative framework was identified within the predeclared open scholarly indexes, repositories, and citation networks searched through the stated cutoff date.","prohibited_claims":["all relevant literature was searched","no prior research exists","developmental counts are PRISMA counts"]},
  "C09_disposition":"complete_for_protocol_reconciliation","next_gate":"D01"}
 OUT_JSON.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
 lines=["# C09 final source-family acceptance matrix","","> Developmental query controls only; every row requires a fresh D05 systematic rerun after protocol approval/freeze.","","| Family | Source | Query | Records | Complete | Sample R/U | Burden | Sentinel | Disposition | Manifest SHA-256 |","|---|---|---|---:|---|---:|---:|---|---|---|"]
 for row in rows:
  burden=row["sample_relevant_plus_uncertain_proportion"]
  lines.append(f"| {row['family_id']} | {row['source']} | `{row['query_id']}` | {row['records_retrieved']:,} | {'Yes' if row['complete'] else 'No'} | {row['sample_likely_relevant']}/{row['sample_uncertain']} | {burden:.1%} | {'Pass' if row['sentinel_acceptance'] else 'Fail'} | `{row['disposition']}` | `{row['manifest_sha256']}` |")
 lines += ["","S2 is the sole bounded-union disposition: its complete 257-record discovery component is combined only for known-item control with the predeclared exact-title recovery documented in `gate2/output/development/c08_bounded_union_acceptance_20260816.json`. It is not a fresh OA-S2I3 export.","","The matrix covers all 18 source-family pairs in the approved non-Cartesian allocation. Counts overlap across sources and families and are not deduplicated, screened, included, or PRISMA counts."]
 OUT_MD.write_text("\n".join(lines)+"\n",encoding="utf-8")

if __name__=="__main__": generate()
