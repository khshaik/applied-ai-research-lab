from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from gate2.query_appraisal import appraise, deterministic_sample_positions

ROOT = Path(__file__).parents[1]
REGISTRY = ROOT / "studies/vdcm/evidence-map/registries/s8_foundational_queries_v0.6.json"
CASES = [
    ("openalex", "OA-S8R6", ROOT / "gate2/output/development/openalex/OA-S8R6-20260816-full1", 1097, 100),
    ("semantic_scholar", "S2-S8R6", ROOT / "gate2/output/development/semantic_scholar/S2-S8R6-20260816-full1", 794, 50),
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_s8_v06_registry_sidecar_and_export_integrity():
    registry_hash = sha(REGISTRY)
    recorded = REGISTRY.with_suffix(".sha256").read_text(encoding="utf-8").split()[0]
    assert recorded == registry_hash
    for _, query_id, export, population, _ in CASES:
        manifest = json.loads((export / "manifest.json").read_text(encoding="utf-8"))
        assert manifest["query_id"] == query_id
        assert manifest["query_registry_sha256"] == registry_hash
        assert manifest["complete_pagination"] is True
        assert manifest["records_retrieved"] == manifest["total_reported"] == population
        assert sha(export / manifest["records_csv"]["file"]) == manifest["records_csv"]["sha256"]
        for page in manifest["pages"]:
            assert sha(export / page["file"]) == page["sha256"]
        assert (export / "manifest.sha256").read_text(encoding="utf-8").split()[0] == sha(export / "manifest.json")
    oa = json.loads((CASES[0][2] / "manifest.json").read_text(encoding="utf-8"))
    assert oa["result_sort"] == "publication_date:desc"


def test_s8_v06_samples_bind_exact_positions_ids_and_seeds():
    for source, query_id, export, population, sample_size in CASES:
        decisions_path = ROOT / f"gate2/output/development/query_appraisals/{query_id}-20260816-query-decisions-v1.json"
        artifact = json.loads(decisions_path.read_text(encoding="utf-8"))
        rows = list(csv.DictReader((export / "records.csv").open(encoding="utf-8", newline="")))
        positions, seed = deterministic_sample_positions(population, source, "S8", "0.6")
        assert len(positions) == sample_size
        assert artifact["sampling_seed_sha256"] == seed
        assert artifact["sample_positions_zero_based"] == positions
        ordered = [rows[position]["source_id"] for position in positions]
        assert artifact["ordered_sample_source_ids"] == ordered
        assert [row["source_id"] for row in artifact["decisions"]] == ordered


def test_s8_v06_appraisals_rederive_and_pass_balanced_controls():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    expected = {"OA-S8R6": (39, 9, 0.48), "S2-S8R6": (18, 3, 0.42)}
    for _, query_id, export, _, _ in CASES:
        decisions_path = ROOT / f"gate2/output/development/query_appraisals/{query_id}-20260816-query-decisions-v1.json"
        result_path = ROOT / f"gate2/output/development/query_appraisals/{query_id}-20260816-query-appraisal-v1.json"
        decisions = json.loads(decisions_path.read_text(encoding="utf-8"))["decisions"]
        derived = appraise(export, registry, decisions)
        checked = json.loads(result_path.read_text(encoding="utf-8"))
        assert derived == checked
        relevant, uncertain, burden = expected[query_id]
        assert (derived["sample_likely_relevant"], derived["sample_uncertain"]) == (relevant, uncertain)
        assert derived["relevant_plus_uncertain_proportion"] == burden
        assert derived["positive_sentinel_recall_pass"] is True
        assert derived["neutral_disconfirming_recall_pass"] is True
        assert derived["negative_boundary_pass"] is True
        assert derived["freeze_ready"] is True
        for path in (decisions_path, result_path):
            assert path.with_suffix(".json.sha256").read_text(encoding="utf-8").split()[0] == sha(path)


def test_s8_little_law_is_method_anchor_not_discovery_recall_sentinel():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    assert all(row["sentinel_id"] != "S8-M1-LITTLES-LAW" for row in registry["sentinels"])
    anchor = registry["targeted_method_anchors"][0]
    assert anchor["doi"] == "10.1287/opre.9.3.383"
    assert "not a discovery-query recall sentinel" in anchor["use_boundary"]
