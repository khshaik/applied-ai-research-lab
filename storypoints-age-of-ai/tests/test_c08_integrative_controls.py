from __future__ import annotations
import csv, hashlib, json
from pathlib import Path
from gate2.query_appraisal import appraise, deterministic_sample_positions

ROOT=Path(__file__).parents[1]

def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()

def test_c08_s1_exact_sample_rederives_and_passes():
    reg=json.loads((ROOT/"studies/vdcm/evidence-map/registries/s1_s2_integrative_queries_v0.3.json").read_text())
    export=ROOT/"gate2/output/development/semantic_scholar/S2-S1I3-20260816-full1"
    rows=list(csv.DictReader((export/"records.csv").open(encoding="utf-8",newline="")))
    artifact=json.loads((ROOT/"gate2/output/development/query_appraisals/S2-S1I3-20260816-query-decisions-v1.json").read_text())
    positions,seed=deterministic_sample_positions(331,"semantic_scholar","S1","0.3")
    assert artifact["sampling_seed_sha256"]==seed
    assert artifact["sample_positions_zero_based"]==positions
    assert artifact["ordered_sample_source_ids"]==[rows[p]["source_id"] for p in positions]
    derived=appraise(export,reg,artifact["decisions"])
    checked=json.loads((ROOT/"gate2/output/development/query_appraisals/S2-S1I3-20260816-query-appraisal-v1.json").read_text())
    assert derived==checked
    assert (derived["sample_likely_relevant"],derived["sample_uncertain"])==(16,3)
    assert derived["freeze_ready"] is True

def test_c08_s2_discovery_component_is_complete_precise_and_has_one_declared_miss():
    reg=json.loads((ROOT/"studies/vdcm/evidence-map/registries/s1_s2_integrative_queries_v0.2.json").read_text())
    export=ROOT/"gate2/output/development/openalex/OA-S2I2-20260816-full1"
    manifest=json.loads((export/"manifest.json").read_text())
    assert manifest["complete_pagination"] is True
    assert manifest["records_retrieved"]==manifest["total_reported"]==257
    artifact=json.loads((ROOT/"gate2/output/development/query_appraisals/OA-S2I2-20260816-query-decisions-v1.json").read_text())
    derived=appraise(export,reg,artifact["decisions"])
    assert (derived["sample_likely_relevant"],derived["sample_uncertain"])==(38,6)
    missed=[row["sentinel_id"] for row in derived["sentinel_checks"] if row["role"] in {"scope_positive","neutral_disconfirming"} and not row["present"]]
    assert missed==["S2-P2-ORCHESTRATION"]
    assert derived["freeze_ready"] is False

def test_c08_predeclared_recovery_is_exact_and_bounded_union_is_transparent():
    record=ROOT/"gate2/output/development/c08_bounded_union_acceptance_20260816.json"
    decision=json.loads(record.read_text())
    assert decision["C08_disposition"]=="complete_for_developmental_query_control"
    assert decision["S2"]["disposition"]=="accepted_bounded_integrative_union"
    assert decision["blocked_fresh_union_execution"]["published_target"] is False
    assert decision["blocked_fresh_union_execution"]["partial_records_used"] is False
    source=ROOT/decision["S2"]["predeclared_targeted_recovery_component"]["source_artifact"]
    assert sha(source/"manifest.json")==decision["S2"]["predeclared_targeted_recovery_component"]["source_manifest_sha256"]
    assert sha(source/"records.csv")==decision["S2"]["predeclared_targeted_recovery_component"]["source_records_sha256"]
    rows=list(csv.DictReader((source/"records.csv").open(encoding="utf-8",newline="")))
    matches={r["source_id"] for r in rows if "Orchestrating Human-AI Software Delivery" in r["title"]}
    assert matches==set(decision["S2"]["predeclared_targeted_recovery_component"]["matching_openalex_ids"])
    for suffix in ("full1","full2","full3"):
        assert not (ROOT/f"gate2/output/development/openalex/OA-S2I3-20260816-{suffix}").exists()
