"""Build immutable D14 evidence-extraction partitions for 212 studies."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import tempfile
from typing import Any

from gate2.citation_chasing import OUTPUT, sha256
from gate2.d14_fulltext_dispositions import FINAL as DISPOSITIONS
from gate2.d14_quality_finalize import FINAL as QUALITY, verify as verify_quality


FINAL = OUTPUT / "evidence_extraction"
PACKET = FINAL / "packet"
VERSION = "d14-extraction-packet/1.0.0"


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def build() -> dict[str, Any]:
    if PACKET.exists():
        raise ValueError(f"immutable D14 extraction packet exists: {PACKET}")
    quality_manifest = verify_quality(); quality = _read(QUALITY / "final_quality_appraisals.jsonl")
    dispositions = {row["citation_family_id"]: row for row in _read(DISPOSITIONS / "fulltext_dispositions.jsonl")}
    if len(quality) != 212:
        raise ValueError("D14 extraction population drift")
    rows = []
    for appraisal in sorted(quality, key=lambda row: row["family_id"]):
        source = dispositions[appraisal["family_id"]]; path = Path(source["sanitized_text_path"])
        payload = json.loads(path.read_text(encoding="utf-8"))
        if sha256(path) != source["sanitized_text_sha256"]:
            raise ValueError("D14 extraction source checksum mismatch")
        rows.append({
            "family_id": appraisal["family_id"], "record_id": appraisal["record_id"], "title": source["title"],
            "doi": source["doi"], "arxiv_id": source["arxiv_id"], "source_text_path": source["sanitized_text_path"],
            "source_text_sha256": source["sanitized_text_sha256"], "page_count": len(payload["pages"]),
            "appraisal_form": appraisal["appraisal_form"], "design_type": appraisal["design_type"],
            "evidence_nature": appraisal["evidence_nature"], "evidence_band": appraisal["evidence_band"],
            "quality_appraisal_sha256": sha256(QUALITY / "final_quality_appraisals.jsonl"),
        })
    FINAL.mkdir(parents=True, exist_ok=True); staging = Path(tempfile.mkdtemp(prefix="d14-extraction-packet-", dir=str(FINAL)))
    try:
        partitions = []
        for index, label in enumerate(("a", "b")):
            chunk = rows[index * 106:(index + 1) * 106]; path = staging / f"extraction_packet_{label}.jsonl"
            path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in chunk), encoding="utf-8")
            partitions.append({"partition": label, "row_count": len(chunk), "sha256": sha256(path), "path": str(PACKET / path.name)})
        manifest = {"status": "d14_evidence_extraction_packet_complete", "protocol_version": "1.3", "pipeline_version": VERSION,
                    "family_count": len(rows), "partitions": partitions,
                    "quality_manifest_sha256": sha256(QUALITY / "final_quality_manifest.json"),
                    "security_boundary": "Checksum-bound static text and final quality ledger only; no network, Git/history, secrets, installs, PDF execution, or private systems."}
        path = staging / "packet_manifest.json"; path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (staging / "packet_manifest.json.sha256").write_text(f"{sha256(path)}  packet_manifest.json\n", encoding="ascii")
        staging.rename(PACKET); return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True); raise


def verify() -> dict[str, Any]:
    path = PACKET / "packet_manifest.json"; manifest = json.loads(path.read_text(encoding="utf-8")); rows = []
    for partition in manifest["partitions"]:
        p = Path(partition["path"]); chunk = _read(p)
        if len(chunk) != partition["row_count"] or sha256(p) != partition["sha256"]:
            raise ValueError("D14 extraction packet partition mismatch")
        rows.extend(chunk)
    if len(rows) != 212 or len({row["family_id"] for row in rows}) != 212:
        raise ValueError("D14 extraction packet conservation failure")
    for row in rows:
        if sha256(Path(row["source_text_path"])) != row["source_text_sha256"]:
            raise ValueError("D14 extraction source drift")
    if (PACKET / "packet_manifest.json.sha256").read_text().split()[0] != sha256(path):
        raise ValueError("D14 extraction packet sidecar mismatch")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("build", "verify")); args = parser.parse_args()
    print(json.dumps(build() if args.command == "build" else verify(), sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
