"""Frozen D05 search controller for the 18-pair open-evidence matrix."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from gate2 import arxiv_export, open_index_export
from gate2.frozen_paths import resolve_frozen_path


ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "gate2/frozen_protocol_package_v1.3.json"
MATRIX = ROOT / "gate2/final_source_family_acceptance_matrix.json"
OUTPUT = ROOT / "gate2/output/systematic/v1.3/20260816"
PLAN = ROOT / "gate2/d05_execution_manifest_v1.3.json"
SOURCE_KEYS = {"OpenAlex": "openalex", "Semantic Scholar": "semantic_scholar"}


class SystematicExportError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _verify_freeze() -> tuple[dict[str, Any], str]:
    package = json.loads(FROZEN.read_text(encoding="utf-8"))
    if package.get("status") != "frozen" or package.get("approval_decision") != "approve":
        raise SystematicExportError("protocol package is not frozen and approved")
    pre = package["approved_prefreeze_package"]
    pre_path = resolve_frozen_path(ROOT, pre["path"])
    if sha256(pre_path) != pre["sha256"]:
        raise SystematicExportError("approved prefreeze package hash mismatch")
    prefreeze = json.loads(pre_path.read_text(encoding="utf-8"))
    for row in prefreeze["artifacts"]:
        if sha256(resolve_frozen_path(ROOT, row["path"])) != row["sha256"]:
            raise SystematicExportError(f"frozen artifact hash mismatch: {row['path']}")
    approval = package["approval_record"]
    if sha256(resolve_frozen_path(ROOT, approval["path"])) != approval["sha256"]:
        raise SystematicExportError("approval record hash mismatch")
    return package, sha256(FROZEN)


def _registry_entry(row: dict[str, Any]) -> tuple[dict[str, Any], str, str]:
    declared_registry = row.get("accepted_union_registry", row["query_reference"])
    registry_path = resolve_frozen_path(ROOT, declared_registry)
    expected = row.get("accepted_union_registry_sha256", row["registry_sha256"])
    if sha256(registry_path) != expected:
        raise SystematicExportError(f"registry hash mismatch: {registry_path.relative_to(ROOT)}")
    if row["source"] in SOURCE_KEYS:
        query_id = "OA-S2I3" if row["family_id"] == "S2" else row["query_id"]
        entry, digest = open_index_export.resolve_registry_entry(
            registry_path, SOURCE_KEYS[row["source"]], query_id
        )
        if digest != expected:
            raise SystematicExportError("resolved registry digest mismatch")
        return entry, digest, query_id
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    query = registry.get("query")
    query_id = registry.get("source_query_id")
    if not query or query_id != row["query_id"]:
        raise SystematicExportError(f"invalid arXiv mapping registry for {row['query_id']}")
    sentinels = [s["arxiv_id"] for s in registry.get("sentinels", []) if s.get("arxiv_id")]
    return {"query": query, "query_mode": "arxiv_atom_query", "sentinels": sentinels}, expected, query_id


def build_plan() -> dict[str, Any]:
    package, freeze_hash = _verify_freeze()
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    if matrix.get("approved_pair_count") != 18 or len(matrix.get("rows", [])) != 18:
        raise SystematicExportError("frozen acceptance matrix must contain exactly 18 rows")
    runs = []
    seen = set()
    for sequence, row in enumerate(matrix["rows"], 1):
        entry, registry_hash, query_id = _registry_entry(row)
        declared_registry = row.get("accepted_union_registry", row["query_reference"])
        registry_path = resolve_frozen_path(ROOT, declared_registry)
        key = (row["family_id"], row["source"])
        if key in seen:
            raise SystematicExportError(f"duplicate source-family pair: {key}")
        seen.add(key)
        source_slug = SOURCE_KEYS.get(row["source"], "arxiv")
        output = OUTPUT / source_slug / query_id
        runs.append({
            "sequence": sequence,
            "family_id": row["family_id"],
            "source": row["source"],
            "source_key": source_slug,
            "query_id": query_id,
            "query": entry["query"],
            "query_sha256": hashlib.sha256(entry["query"].encode()).hexdigest(),
            "query_mode": entry.get("query_mode", "fulltext_search"),
            "result_sort": entry.get("result_sort", ""),
            "sentinels": entry.get("sentinels", []),
            # Preserve the frozen manifest's historical path spelling while
            # reading the byte-identical artifact through the relocation map.
            "registry_path": declared_registry,
            "registry_sha256": registry_hash,
            "acceptance_matrix_row_sha256": canonical_hash(row),
            "from_date": row["from_date"],
            "to_date": package["initial_search_cutoff_date"],
            "output_dir": str(output.relative_to(ROOT)),
            "developmental_source_query_id": row["query_id"],
            "fresh_systematic_execution_required": True,
        })
    return {
        "manifest_version": "1.0.0",
        "protocol_version": "1.3",
        "status": "prepared_frozen_systematic_execution",
        "freeze_package_path": str(FROZEN.relative_to(ROOT)),
        "freeze_package_sha256": freeze_hash,
        "acceptance_matrix_path": str(MATRIX.relative_to(ROOT)),
        "acceptance_matrix_sha256": sha256(MATRIX),
        "initial_search_cutoff_date": package["initial_search_cutoff_date"],
        "systematic_output_root": str(OUTPUT.relative_to(ROOT)),
        "run_count": len(runs),
        "runs": runs,
    }


def write_plan() -> dict[str, Any]:
    plan = build_plan()
    payload = json.dumps(plan, indent=2, sort_keys=True) + "\n"
    if PLAN.exists() and PLAN.read_text(encoding="utf-8") != payload:
        raise SystematicExportError("existing D05 execution manifest differs from frozen plan")
    if not PLAN.exists():
        PLAN.write_text(payload, encoding="utf-8")
        PLAN.with_suffix(PLAN.suffix + ".sha256").write_text(
            f"{sha256(PLAN)}  {PLAN.name}\n", encoding="utf-8"
        )
    return plan


def run_one(query_id: str) -> dict[str, Any]:
    plan = write_plan()
    matches = [r for r in plan["runs"] if r["query_id"] == query_id]
    if len(matches) != 1:
        raise SystematicExportError(f"plan must contain exactly one query_id {query_id}")
    run = matches[0]
    output = ROOT / run["output_dir"]
    common = dict(
        query_id=run["query_id"], query=run["query"], output_dir=output,
        status="systematic_frozen", registry_sha256=run["registry_sha256"],
        freeze_package_sha256=plan["freeze_package_sha256"],
        matrix_row_sha256=run["acceptance_matrix_row_sha256"],
        from_date=run["from_date"], to_date=run["to_date"],
    )
    if run["source_key"] == "arxiv":
        return arxiv_export.export_query(
            **common, expected_sentinels=tuple(run["sentinels"]), page_size=100,
        )
    return open_index_export.export_query(
        source=run["source_key"], **common, page_size=200 if run["source_key"] == "openalex" else 1000,
        query_mode=run["query_mode"], result_sort=run["result_sort"],
        api_key=os.environ.get("OPENALEX_API_KEY", "") if run["source_key"] == "openalex" else "",
    )


def reconcile() -> dict[str, Any]:
    plan = write_plan()
    completed = []
    missing = []
    for run in plan["runs"]:
        target = ROOT / run["output_dir"]
        manifest_path = target / "manifest.json"
        if not manifest_path.is_file():
            missing.append(run["query_id"])
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        checks = {
            "status": manifest.get("status") == "systematic_frozen",
            "complete": manifest.get("complete_pagination") is True,
            "scope": manifest.get("retrieval_scope") == "complete_systematic",
            "query": manifest.get("query_sha256") == run["query_sha256"],
            "registry": manifest.get("query_registry_sha256") == run["registry_sha256"],
            "freeze": manifest.get("freeze_package_sha256") == plan["freeze_package_sha256"],
            "row": manifest.get("acceptance_matrix_row_sha256") == run["acceptance_matrix_row_sha256"],
            "dates": manifest.get("from_date") == run["from_date"] and manifest.get("to_date") == run["to_date"],
            "manifest_sidecar": (target / "manifest.sha256").is_file() and
                (target / "manifest.sha256").read_text().split()[0] == sha256(manifest_path),
        }
        if not all(checks.values()):
            raise SystematicExportError(f"systematic run reconciliation failed for {run['query_id']}: {checks}")
        completed.append({
            "query_id": run["query_id"], "family_id": run["family_id"], "source": run["source"],
            "records_retrieved": manifest["records_retrieved"],
            "manifest_path": str(manifest_path.relative_to(ROOT)), "manifest_sha256": sha256(manifest_path),
        })
    result = {
        "status": "complete" if not missing else "incomplete",
        "protocol_version": "1.3", "freeze_package_sha256": plan["freeze_package_sha256"],
        "expected_runs": 18, "completed_runs": len(completed), "missing_query_ids": missing,
        "runs": completed,
        "interpretation_boundary": "Raw systematic discovery records only; not deduplicated, screened, eligible, or PRISMA inclusion counts.",
        "reconciled_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    if not missing:
        out = OUTPUT / "d05_reconciliation.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        sidecar = out.with_suffix(out.suffix + ".sha256")
        if out.exists():
            existing = json.loads(out.read_text(encoding="utf-8"))
            comparable_existing = {k: v for k, v in existing.items() if k != "reconciled_at_utc"}
            comparable_result = {k: v for k, v in result.items() if k != "reconciled_at_utc"}
            if comparable_existing != comparable_result:
                raise SystematicExportError("existing D05 reconciliation differs from current 18-run state")
            if not sidecar.is_file() or sidecar.read_text().split()[0] != sha256(out):
                raise SystematicExportError("existing D05 reconciliation sidecar mismatch")
            return existing
        out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        sidecar.write_text(f"{sha256(out)}  {out.name}\n", encoding="utf-8")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("prepare")
    run = sub.add_parser("run-one")
    run.add_argument("query_id")
    sub.add_parser("reconcile")
    args = parser.parse_args(argv)
    if args.command == "prepare":
        result = write_plan()
        print(json.dumps({"status": result["status"], "run_count": result["run_count"]}, sort_keys=True))
    elif args.command == "run-one":
        result = run_one(args.query_id)
        print(json.dumps({k: result[k] for k in ("status", "query_id", "records_retrieved", "complete_pagination")}, sort_keys=True))
    else:
        result = reconcile()
        print(json.dumps({k: result[k] for k in ("status", "expected_runs", "completed_runs", "missing_query_ids")}, sort_keys=True))
        if result["status"] != "complete":
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
