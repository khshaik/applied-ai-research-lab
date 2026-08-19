"""Reconcile and freeze the two D14 evidence-extraction partitions."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
from typing import Any, Optional

from gate2.citation_chasing import OUTPUT, sha256
from gate2.d14_extraction_packet import PACKET, verify as verify_packet


ROOT = OUTPUT / "evidence_extraction"
FINAL = ROOT / "final"
SCHEMA = Path("gate2/d14_extraction_schema.json")


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _literal_span(value: str, page_text: str) -> Optional[str]:
    """Return the exact page span when only whitespace differs from value."""
    if value in page_text:
        return value
    compact_value = "".join(value.split())
    compact_page = []
    positions = []
    for index, char in enumerate(page_text):
        if not char.isspace():
            compact_page.append(char); positions.append(index)
    start = "".join(compact_page).find(compact_value)
    if start < 0:
        return None
    return page_text[positions[start]:positions[start + len(compact_value) - 1] + 1]


def _validate_row(row: dict[str, Any], expected: dict[str, Any], schema: dict[str, Any]) -> int:
    if set(schema["top_level_required"]) - set(row):
        raise ValueError(f"missing extraction fields: {row.get('family_id')}")
    if row["record_id"] != expected["record_id"] or row["source_text_sha256"] != expected["source_text_sha256"]:
        raise ValueError("extraction packet binding mismatch")
    security = row["security_attestation"]
    if any(security.get(key) is not False for key in schema["security_required_false"]):
        raise ValueError("extraction security attestation failure")
    pages = {page["page"]: page["text"] for page in json.loads(Path(expected["source_text_path"]).read_text(encoding="utf-8"))["pages"]}
    finding_ids = set()
    whitespace_repairs = 0
    for finding in row["measures_findings"]:
        if set(schema["finding_required"]) - set(finding) or finding["field_name"] not in schema["finding_field_name_enum"]:
            raise ValueError("invalid extraction finding schema")
        if finding["finding_id"] in finding_ids:
            raise ValueError("duplicate extraction finding ID")
        finding_ids.add(finding["finding_id"])
        locator = finding["source_locator"]
        if isinstance(locator, dict):
            page_number = locator.get("page")
        else:
            match = re.search(r"\bpage\s+(\d+)\b", str(locator), flags=re.IGNORECASE)
            page_number = int(match.group(1)) if match else None
        if page_number not in pages:
            raise ValueError(f"finding locator/value mismatch: {row['family_id']}")
        literal = _literal_span(finding["value"], pages[page_number])
        if literal is None:
            raise ValueError(f"finding locator/value mismatch: {row['family_id']}")
        if literal != finding["value"]:
            finding["value"] = literal
            whitespace_repairs += 1
        if finding["quantitative"]:
            estimate = finding.get("reported_estimate")
            numeric_tokens = re.findall(r"(?<!\w)[<>]?\s*\d[\d,]*(?:\.\d+)?%?", estimate or "")
            compact_page = "".join(pages[page_number].split())
            if not numeric_tokens or any("".join(token.split()) not in compact_page for token in numeric_tokens):
                raise ValueError(f"quantitative finding unsupported: {row['family_id']}")
    dimensions = row["novelty_assessment"]["dimensions"]
    if set(dimensions) != set(schema["novelty_dimension_keys"]):
        raise ValueError("novelty dimension mismatch")
    if any(value["status"] not in schema["novelty_status_enum"] for value in dimensions.values()):
        raise ValueError("novelty status invalid")
    return whitespace_repairs


def finalize() -> dict[str, Any]:
    if FINAL.exists():
        raise ValueError("immutable final D14 extraction already exists")
    packet_manifest = verify_packet(); schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    expected = {}
    for entry in packet_manifest["partitions"]:
        for row in _read(Path(entry["path"])):
            expected[row["family_id"]] = row
    parts = [ROOT / "extraction_part_a.jsonl", ROOT / "extraction_part_b.jsonl"]
    rows = []
    for path in parts:
        sidecar = path.with_suffix(path.suffix + ".sha256")
        if sidecar.read_text().split()[0] != sha256(path):
            raise ValueError("extraction partition checksum mismatch")
        rows.extend(_read(path))
    if len(rows) != 212 or len({row["family_id"] for row in rows}) != 212 or set(expected) != {row["family_id"] for row in rows}:
        raise ValueError("D14 extraction population mismatch")
    rows.sort(key=lambda row: row["family_id"])
    whitespace_repairs = sum(_validate_row(row, expected[row["family_id"]], schema) for row in rows)
    FINAL.mkdir(parents=True)
    ledger = FINAL / "final_evidence_extraction.jsonl"
    ledger.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    novelty = Counter(value["status"] for row in rows for value in row["novelty_assessment"]["dimensions"].values())
    findings = sum(len(row["measures_findings"]) for row in rows)
    manifest = {
        "status": "d14_evidence_extraction_complete", "protocol_version": "1.3", "study_count": 212,
        "finding_count": findings, "quantitative_finding_count": sum(f["quantitative"] for row in rows for f in row["measures_findings"]),
        "novelty_dimension_counts": dict(novelty),
        "literal_excerpt_whitespace_repairs": whitespace_repairs,
        "same_planning_use_counts": dict(Counter(row["novelty_assessment"]["same_planning_use"] for row in rows)),
        "part_hashes": {path.name: sha256(path) for path in parts}, "schema_sha256": sha256(SCHEMA),
        "packet_manifest_sha256": sha256(PACKET / "packet_manifest.json"), "ledger_sha256": sha256(ledger),
        "interpretation_boundary": "Extraction is source-located evidence coding. It does not by itself establish construct equivalence, exhaustive coverage, or novelty.",
    }
    manifest_path = FINAL / "final_extraction_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (FINAL / "final_extraction_manifest.json.sha256").write_text(f"{sha256(manifest_path)}  final_extraction_manifest.json\n", encoding="ascii")
    return manifest


def verify() -> dict[str, Any]:
    manifest_path = FINAL / "final_extraction_manifest.json"; manifest = json.loads(manifest_path.read_text())
    if sha256(FINAL / "final_evidence_extraction.jsonl") != manifest["ledger_sha256"]:
        raise ValueError("final extraction ledger mismatch")
    if (FINAL / "final_extraction_manifest.json.sha256").read_text().split()[0] != sha256(manifest_path):
        raise ValueError("final extraction manifest mismatch")
    if len(_read(FINAL / "final_evidence_extraction.jsonl")) != manifest["study_count"]:
        raise ValueError("final extraction count mismatch")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("finalize", "verify")); args = parser.parse_args()
    result = finalize() if args.command == "finalize" else verify()
    print(json.dumps(result, sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
