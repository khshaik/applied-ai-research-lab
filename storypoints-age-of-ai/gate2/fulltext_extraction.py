"""D11 safe local extraction controller for D10-retrieved PDFs."""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
D10 = ROOT / "gate2/output/systematic/v1.3/20260816/d10"
OUTPUT = ROOT / "gate2/output/systematic/v1.3/20260816/d11/extraction"
VERSION = "d11-static-pdf-extraction/1.0.0"


class ExtractionError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _extract_one(row: dict, timeout: int) -> dict:
    family_id = row["family_id"]
    pdf_path = ROOT / row["pdf_path"]
    output_path = OUTPUT / "text" / f"{family_id}.json"
    if output_path.exists():
        existing = json.loads(output_path.read_text(encoding="utf-8"))
        if existing.get("pdf_sha256") == row["pdf_sha256"]:
            return {"family_id": family_id, "status": existing["status"], "output_sha256": sha256(output_path),
                    "page_count": existing["page_count"], "extracted_char_count": existing["extracted_char_count"]}
    env = dict(os.environ)
    env["PYTHONPYCACHEPREFIX"] = "/private/tmp/storypoints-pdf-pycache"
    command = [sys.executable, "-m", "gate2.pdf_extract_worker", str(pdf_path), str(output_path)]
    try:
        process = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=timeout, check=False)
        if process.returncode != 0 or not output_path.exists():
            return {"family_id": family_id, "status": "extraction_failed", "error_type": "worker_failure",
                    "returncode": process.returncode, "stderr_tail": process.stderr[-500:]}
        extracted = json.loads(output_path.read_text(encoding="utf-8"))
        if extracted["pdf_sha256"] != row["pdf_sha256"]:
            raise ExtractionError(f"source PDF hash mismatch after extraction: {family_id}")
        return {"family_id": family_id, "status": extracted["status"], "output_sha256": sha256(output_path),
                "page_count": extracted["page_count"], "extracted_char_count": extracted["extracted_char_count"]}
    except subprocess.TimeoutExpired:
        return {"family_id": family_id, "status": "extraction_failed", "error_type": "timeout"}


def run(workers: int = 4, timeout: int = 45) -> dict:
    manifest = json.loads((D10 / "final/d10_final_manifest.json").read_text(encoding="utf-8"))
    ledger = [json.loads(line) for line in (D10 / "final/fulltext_retrieval_ledger.jsonl").read_text(encoding="utf-8").splitlines()]
    rows = [row for row in ledger if row["full_text_status"] == "retrieved_open"]
    if len(rows) != manifest["retrieved_pdf_count"] or len(rows) != 1605:
        raise ExtractionError("D11 extraction input does not reconcile to D10")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    results = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(_extract_one, row, timeout) for row in rows]
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda row: row["family_id"])
    counts = Counter(row["status"] for row in results)
    index_path = OUTPUT / "extraction_index.jsonl"
    temporary = index_path.with_suffix(".jsonl.tmp")
    temporary.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in results), encoding="utf-8")
    temporary.replace(index_path)
    summary = {
        "status": "complete" if not counts.get("extraction_failed") else "complete_with_recorded_failures",
        "protocol_version": "1.3", "pipeline_version": VERSION,
        "input_d10_manifest_sha256": sha256(D10 / "final/d10_final_manifest.json"),
        "pdf_count": len(rows), "result_counts": dict(sorted(counts.items())),
        "total_pages": sum(row.get("page_count", 0) for row in results),
        "total_extracted_chars": sum(row.get("extracted_char_count", 0) for row in results),
        "index_sha256": sha256(index_path),
        "security_boundary": "Each PDF was parsed in a time-limited child process for static text only. No embedded action, JavaScript, attachment, link, or macro was executed.",
    }
    summary_path = OUTPUT / "extraction_manifest.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUTPUT / "extraction_manifest.json.sha256").write_text(f"{sha256(summary_path)}  extraction_manifest.json\n", encoding="utf-8")
    return summary


def verify() -> dict:
    manifest_path = OUTPUT / "extraction_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    index_path = OUTPUT / "extraction_index.jsonl"
    rows = [json.loads(line) for line in index_path.read_text(encoding="utf-8").splitlines()]
    if len(rows) != manifest["pdf_count"] or sha256(index_path) != manifest["index_sha256"]:
        raise ExtractionError("D11 extraction index mismatch")
    for row in rows:
        if row["status"] in {"text_extracted", "no_extractable_text"}:
            path = OUTPUT / "text" / f"{row['family_id']}.json"
            if sha256(path) != row["output_sha256"]:
                raise ExtractionError(f"D11 extracted-text hash mismatch: {row['family_id']}")
    if (OUTPUT / "extraction_manifest.json.sha256").read_text().split()[0] != sha256(manifest_path):
        raise ExtractionError("D11 extraction manifest sidecar mismatch")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("run", "verify"))
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=45)
    args = parser.parse_args()
    result = run(args.workers, args.timeout) if args.command == "run" else verify()
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
