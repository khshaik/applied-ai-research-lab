from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).parents[1]
MATRIX=ROOT/"gate2/final_source_family_acceptance_matrix.json"

def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()

def test_c09_matrix_exactly_covers_approved_non_cartesian_allocation():
    data=json.loads(MATRIX.read_text())
    expected={
        ("S1","Semantic Scholar"),("S2","OpenAlex"),("S3","OpenAlex"),("S3","Semantic Scholar"),
        ("S4/S5R","OpenAlex"),("S4/S5R","Semantic Scholar"),("S4/S5R","arXiv"),
        ("S5T","OpenAlex"),("S5T","arXiv"),("S5S","OpenAlex"),("S5S","arXiv"),
        ("S6","OpenAlex"),("S6","arXiv"),("S7","OpenAlex"),("S7","Semantic Scholar"),
        ("S7","arXiv"),("S8","OpenAlex"),("S8","Semantic Scholar"),
    }
    assert data["approved_pair_count"]==18
    assert {(r["family_id"],r["source"]) for r in data["rows"]}==expected
    assert data["C09_disposition"]=="complete_for_protocol_reconciliation"
    assert data["next_gate"]=="D01"

def test_c09_every_row_reconciles_immutable_artifacts():
    data=json.loads(MATRIX.read_text())
    for row in data["rows"]:
        manifest=ROOT/row["manifest_path"]
        appraisal=ROOT/row["appraisal_path"]
        registry=ROOT/row["query_reference"]
        assert sha(manifest)==row["manifest_sha256"]
        assert sha(appraisal)==row["appraisal_sha256"]
        assert sha(registry)==row["registry_sha256"]
        payload=json.loads(manifest.read_text())
        assert payload["query_id"]==row["query_id"]
        assert payload["records_retrieved"]==row["records_retrieved"]
        assert row["complete"] is True and row["sentinel_acceptance"] is True
        assert row["systematic_rerun_required"] is True

def test_c09_preserves_bounded_union_and_claim_boundaries():
    data=json.loads(MATRIX.read_text())
    bounded=[row for row in data["rows"] if row["disposition"]=="accepted_bounded_integrative_union"]
    assert len(bounded)==1 and bounded[0]["family_id"]=="S2"
    row=bounded[0]
    assert row["fresh_union_platform_execution"] is False
    assert sha(ROOT/row["accepted_union_registry"])==row["accepted_union_registry_sha256"]
    assert sha(ROOT/row["bounded_union_control"])==row["bounded_union_control_sha256"]
    prohibited=data["coverage_boundary"]["prohibited_claims"]
    assert "all relevant literature was searched" in prohibited
    assert "developmental counts are PRISMA counts" in prohibited
    assert MATRIX.with_suffix(".sha256").read_text().split()[0]==sha(MATRIX)
