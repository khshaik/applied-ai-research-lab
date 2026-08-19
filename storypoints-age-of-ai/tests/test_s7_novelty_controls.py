from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from gate2.arxiv_mapping import appraise_mapping
from gate2.query_appraisal import appraise, deterministic_sample_positions


ROOT = Path(__file__).parents[1]
REGISTRY_PATH = ROOT / "studies/vdcm/evidence-map/registries/s7_novelty_queries_v0.4.json"
CASES = [
    (
        "openalex",
        "OA-S7R4",
        ROOT / "gate2/output/development/openalex/OA-S7R4-20260816-pilot1",
        ROOT / "gate2/output/development/query_appraisals/OA-S7R4-20260816-query-decisions-v1.json",
        ROOT / "gate2/output/development/query_appraisals/OA-S7R4-20260816-query-appraisal-v1.json",
        49,
    ),
    (
        "semantic_scholar",
        "S2-S7R4",
        ROOT / "gate2/output/development/semantic_scholar/S2-S7R4-20260816-pilot1",
        ROOT / "gate2/output/development/query_appraisals/S2-S7R4-20260816-query-decisions-v1.json",
        ROOT / "gate2/output/development/query_appraisals/S2-S7R4-20260816-query-appraisal-v1.json",
        19,
    ),
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_s7_v04_registry_manifest_and_raw_export_integrity():
    registry_hash = sha(REGISTRY_PATH)
    for _, query_id, export, _, _, population in CASES:
        manifest_path = export / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert manifest["query_id"] == query_id
        assert manifest["query_registry_sha256"] == registry_hash
        assert manifest["complete_pagination"] is True
        assert manifest["records_retrieved"] == manifest["total_reported"] == population
        assert sha(export / manifest["records_csv"]["file"]) == manifest["records_csv"]["sha256"]
        for page in manifest["pages"]:
            assert sha(export / page["file"]) == page["sha256"]
        recorded = (export / "manifest.sha256").read_text(encoding="utf-8").split()[0]
        assert recorded == sha(manifest_path)


def test_s7_v04_samples_bind_exact_positions_order_and_seed():
    for source, _, export, decision_path, _, population in CASES:
        artifact = json.loads(decision_path.read_text(encoding="utf-8"))
        rows = list(csv.DictReader((export / "records.csv").open(encoding="utf-8", newline="")))
        positions, seed = deterministic_sample_positions(population, source, "S7", "0.4")
        assert positions == list(range(population))
        ordered = [rows[position]["source_id"] for position in positions]
        assert artifact["sampling_seed_sha256"] == seed
        assert artifact["sample_positions_zero_based"] == positions
        assert artifact["ordered_sample_source_ids"] == ordered
        assert [row["source_id"] for row in artifact["decisions"]] == ordered


def test_s7_v04_appraisals_rederive_and_recall_balanced_controls():
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    for _, _, export, decision_path, result_path, population in CASES:
        decisions = json.loads(decision_path.read_text(encoding="utf-8"))["decisions"]
        derived = appraise(export, registry, decisions)
        checked = json.loads(result_path.read_text(encoding="utf-8"))
        assert derived == checked
        assert derived["sample_size"] == population
        assert derived["freeze_ready"] is True
        assert derived["positive_sentinel_recall_pass"] is True
        assert derived["neutral_disconfirming_recall_pass"] is True
        assert derived["negative_boundary_pass"] is True


def test_semantic_scholar_acem_title_fallback_is_explicit_and_exact():
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    sentinel = next(row for row in registry["sentinels"] if row["sentinel_id"] == "S7-P3-ACEM")
    expected_id = sentinel["documentary_source_record_ids"]["semantic_scholar"]
    rows = list(csv.DictReader((CASES[1][2] / "records.csv").open(encoding="utf-8", newline="")))
    match = next(row for row in rows if row["source_id"] == expected_id)
    assert match["doi"] == ""
    assert " ".join(match["title"].casefold().split()) == " ".join(sentinel["title"].casefold().split())
    result = json.loads(CASES[1][4].read_text(encoding="utf-8"))
    check = next(row for row in result["sentinel_checks"] if row["sentinel_id"] == "S7-P3-ACEM")
    assert check["present"] is True
    assert check["match_basis"] == "title"


def test_s7_arxiv_resolved_blocker_preserves_failure_history():
    blocker = json.loads((ROOT / "gate2/output/development/arxiv/AX-S7R4-20260816-blocker.json").read_text(encoding="utf-8"))
    assert blocker["status"] == "development_export_blocker_resolved"
    assert blocker["target_directory_created"] is False
    assert blocker["error_class"] == "DNS_resolution_failure"
    assert blocker["resolution"]["complete_pagination"] is True
    assert blocker["resolution"]["records_retrieved"] == 7
    assert (ROOT / blocker["resolution"]["successful_export"]).is_dir()


def test_s7_arxiv_export_sample_and_appraisal_rederive_exactly():
    export = ROOT / "gate2/output/development/arxiv/AX-S7R4-20260816-retry2"
    mapping_path = ROOT / "studies/vdcm/evidence-map/registries/arxiv_s7_mapping_v0.4.json"
    decisions_path = ROOT / "gate2/output/development/query_appraisals/AX-S7R4-20260816-query-decisions-v1.json"
    result_path = ROOT / "gate2/output/development/query_appraisals/AX-S7R4-20260816-query-appraisal-v1.json"
    manifest = json.loads((export / "manifest.json").read_text(encoding="utf-8"))
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    artifact = json.loads(decisions_path.read_text(encoding="utf-8"))
    rows = list(csv.DictReader((export / "records.csv").open(encoding="utf-8", newline="")))
    positions, seed = deterministic_sample_positions(7, "arxiv", "S7", "0.4")
    assert manifest["complete_pagination"] is True
    assert manifest["records_retrieved"] == manifest["total_reported"] == 7
    assert manifest["query"] == mapping["query"] == registry["arxiv_query"]["query"]
    assert sha(export / manifest["records_csv"]["file"]) == manifest["records_csv"]["sha256"]
    assert artifact["sampling_seed_sha256"] == seed
    assert artifact["sample_positions_zero_based"] == positions
    ordered = [rows[position]["arxiv_id_version"] for position in positions]
    assert artifact["ordered_sample_source_ids"] == ordered
    assert [row["source_id"] for row in artifact["decisions"]] == ordered
    derived = appraise_mapping(export, mapping_path, artifact["decisions"])
    assert derived == json.loads(result_path.read_text(encoding="utf-8"))
    assert derived["sample_likely_relevant"] == 5
    assert derived["sample_uncertain"] == 2
    assert derived["freeze_ready"] is True
