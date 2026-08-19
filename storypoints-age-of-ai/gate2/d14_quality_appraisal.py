"""Build and validate local-only D14 quality-appraisal partitions."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import tempfile
from typing import Any

from gate2.citation_chasing import OUTPUT, sha256
from gate2.d12_appraisal_partition_b_local import FORMS
from gate2.d14_fulltext_dispositions import FINAL as DISPOSITIONS
from gate2.d14_fulltext_finalize import FINAL as FULLTEXT_FINAL, verify as verify_fulltext


FINAL = OUTPUT / "quality_appraisal"
PACKET = FINAL / "packet"
VERSION = "d14-quality-appraisal/1.0.0"


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def build_packet() -> dict[str, Any]:
    if PACKET.exists():
        raise ValueError(f"immutable D14 quality packet exists: {PACKET}")
    fulltext = verify_fulltext()
    included = [row for row in _read(FULLTEXT_FINAL / "final_fulltext_ledger.jsonl") if row["final_fulltext_decision"] == "include"]
    dispositions = {row["citation_family_id"]: row for row in _read(DISPOSITIONS / "fulltext_dispositions.jsonl")}
    if len(included) != 212:
        raise ValueError("D14 included population drift")
    rows = []
    for row in sorted(included, key=lambda value: value["citation_family_id"]):
        source = dispositions[row["citation_family_id"]]
        path = Path(source["sanitized_text_path"])
        payload = json.loads(path.read_text(encoding="utf-8"))
        if sha256(path) != source["sanitized_text_sha256"]:
            raise ValueError("D14 appraisal source checksum mismatch")
        rows.append({
            "family_id": row["citation_family_id"],
            "record_id": row["citation_family_id"],
            "title": row["title"],
            "doi": row["doi"],
            "arxiv_id": row["arxiv_id"],
            "source_text_path": source["sanitized_text_path"],
            "source_text_sha256": source["sanitized_text_sha256"],
            "page_count": len(payload["pages"]),
        })
    FINAL.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="d14-quality-packet-", dir=str(FINAL)))
    try:
        partitions = []
        for index, label in enumerate(("a", "b")):
            chunk = rows[index * 106:(index + 1) * 106]
            path = staging / f"appraisal_packet_{label}.jsonl"
            path.write_text("".join(json.dumps(value, sort_keys=True) + "\n" for value in chunk), encoding="utf-8")
            partitions.append({"partition": label, "row_count": len(chunk), "sha256": sha256(path), "path": str(PACKET / path.name)})
        manifest = {
            "status": "d14_quality_appraisal_packet_complete",
            "protocol_version": "1.3",
            "pipeline_version": VERSION,
            "family_count": len(rows),
            "partitions": partitions,
            "fulltext_manifest_sha256": sha256(FULLTEXT_FINAL / "final_fulltext_manifest.json"),
            "security_boundary": "Checksum-bound static extracted text only; no network, Git/history, secrets, installs, PDF execution, or private systems.",
        }
        manifest_path = staging / "packet_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (staging / "packet_manifest.json.sha256").write_text(f"{sha256(manifest_path)}  packet_manifest.json\n", encoding="ascii")
        staging.rename(PACKET)
        return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def verify_packet() -> dict[str, Any]:
    manifest_path = PACKET / "packet_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = []
    for partition in manifest["partitions"]:
        path = Path(partition["path"])
        chunk = _read(path)
        if len(chunk) != partition["row_count"] or sha256(path) != partition["sha256"]:
            raise ValueError("D14 quality packet partition mismatch")
        rows.extend(chunk)
    if len(rows) != 212 or len({row["family_id"] for row in rows}) != 212:
        raise ValueError("D14 quality packet population mismatch")
    for row in rows:
        if sha256(Path(row["source_text_path"])) != row["source_text_sha256"]:
            raise ValueError("D14 quality packet source drift")
    if (PACKET / "packet_manifest.json.sha256").read_text().split()[0] != sha256(manifest_path):
        raise ValueError("D14 quality packet sidecar mismatch")
    return manifest


def validate_appraisal(path: Path, partition: str, appraiser_id: str) -> dict[str, Any]:
    manifest = verify_packet()
    partition_row = next(row for row in manifest["partitions"] if row["partition"] == partition)
    expected_rows = _read(Path(partition_row["path"]))
    expected = {row["family_id"]: row for row in expected_rows}
    rows = _read(path)
    seen: set[str] = set()
    contexts: set[str] = set()
    for row in rows:
        family_id = row.get("family_id")
        if family_id not in expected or family_id in seen:
            raise ValueError("unknown or duplicate D14 appraisal family")
        seen.add(family_id)
        if row.get("record_id") != expected[family_id]["record_id"] or row.get("source_text_sha256") != expected[family_id]["source_text_sha256"]:
            raise ValueError("D14 appraisal source binding mismatch")
        if row.get("appraiser_agent_id") != appraiser_id:
            raise ValueError("D14 appraisal identity mismatch")
        context = row.get("review_context_id")
        if not isinstance(context, str) or context in contexts:
            raise ValueError("D14 appraisal context invalid")
        contexts.add(context)
        form = row.get("appraisal_form")
        if form not in FORMS:
            raise ValueError("D14 appraisal form invalid")
        criteria = row.get("criteria")
        expected_ids = [item[0] for item in FORMS[form]]
        if not isinstance(criteria, list) or [item.get("criterion_id") for item in criteria] != expected_ids:
            raise ValueError("D14 appraisal criteria mismatch")
        for item in criteria:
            if item.get("score") not in {0, 1, 2} or not item.get("justification") or not item.get("source_locator"):
                raise ValueError("D14 appraisal criterion invalid")
            locator = str(item["source_locator"])
            if not locator.startswith("page ") or not locator[5:].isdigit() or not 1 <= int(locator[5:]) <= expected[family_id]["page_count"]:
                raise ValueError("D14 appraisal locator out of range")
        points = sum(item["score"] for item in criteria)
        if row.get("applicable_points") != 20 or row.get("points_awarded") != points or abs(row.get("percent", -1) - points * 5.0) > 1e-9:
            raise ValueError("D14 appraisal arithmetic mismatch")
        critical = row.get("critical_flaw") is True
        expected_band = "low_contextual" if critical or row["percent"] < 50 else "moderate" if row["percent"] < 75 else "high"
        if row.get("evidence_band") != expected_band or (critical and not row.get("critical_flaw_basis")):
            raise ValueError("D14 appraisal band/critical-flaw mismatch")
        if not row.get("design_type") or row.get("evidence_nature") not in {"observed", "self-reported", "modeled", "conceptual"}:
            raise ValueError("D14 appraisal design/evidence nature invalid")
        if len(row.get("security_attestation", "")) < 30:
            raise ValueError("D14 appraisal security attestation incomplete")
    if seen != set(expected):
        raise ValueError(f"D14 appraisal partition incomplete: {len(set(expected) - seen)} missing")
    sidecar = path.with_suffix(path.suffix + ".sha256")
    if not sidecar.exists() or sidecar.read_text().split()[0] != sha256(path):
        raise ValueError("D14 appraisal sidecar mismatch")
    return {
        "status": "valid_complete_d14_appraisal_partition",
        "partition": partition,
        "family_count": len(rows),
        "forms": dict(Counter(row["appraisal_form"] for row in rows)),
        "bands": dict(Counter(row["evidence_band"] for row in rows)),
        "sha256": sha256(path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("build-packet")
    sub.add_parser("verify-packet")
    validate = sub.add_parser("validate-appraisal")
    validate.add_argument("path", type=Path)
    validate.add_argument("partition", choices=("a", "b"))
    validate.add_argument("appraiser_id")
    args = parser.parse_args()
    if args.command == "build-packet":
        result = build_packet()
    elif args.command == "verify-packet":
        result = verify_packet()
    else:
        result = validate_appraisal(args.path, args.partition, args.appraiser_id)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
