"""Fail-closed, project-local sanitization and static extraction for D14 PDFs.

The parser runs once per document in a bounded subprocess. Source PDFs are never
modified. A derivative is published only after structural and byte-level checks
and successful page-numbered text extraction.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from gate2.citation_chasing import OUTPUT, sha256
from gate2.d14_secure_fulltext import PDFS, QUARANTINE, active_indicators

FULLTEXT = OUTPUT / "fulltext"
SANITIZED = FULLTEXT / "sanitized"
TEXT = FULLTEXT / "sanitized_text"
RESULTS = FULLTEXT / "sanitization_results"
DEPENDENCY_MANIFEST = Path("gate2/pdf_dependency_manifest.json")
VERSION = "d14-pdf-sanitize/1.0.0"
MAX_SOURCE_BYTES = 50 * 1024 * 1024
MAX_OUTPUT_BYTES = 60 * 1024 * 1024
MAX_CPU_SECONDS = 30
MAX_WALL_SECONDS = 45
MAX_ADDRESS_SPACE = 1536 * 1024 * 1024


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def _replace_invalid_surrogates(value: str) -> tuple[str, int]:
    count = sum(0xD800 <= ord(char) <= 0xDFFF for char in value)
    if not count:
        return value, 0
    return "".join("\ufffd" if 0xD800 <= ord(char) <= 0xDFFF else char for char in value), count


def _dependency_record() -> dict[str, Any]:
    raw = DEPENDENCY_MANIFEST.read_bytes()
    manifest = json.loads(raw)
    wheel = Path(manifest["artifact"])
    if sha256(wheel) != manifest["sha256"]:
        raise ValueError("pypdf wheel checksum mismatch")
    for dep in manifest.get("runtime_dependencies", []):
        if sha256(Path(dep["artifact"])) != dep["sha256"]:
            raise ValueError(f"dependency wheel checksum mismatch: {dep['dependency']}")
    return {
        "manifest_path": str(DEPENDENCY_MANIFEST),
        "manifest_sha256": hashlib.sha256(raw).hexdigest(),
        "pypdf_version": manifest["version"],
        "pypdf_wheel_sha256": manifest["sha256"],
        "runtime_dependencies": [
            {"dependency": d["dependency"], "version": d["version"], "sha256": d["sha256"]}
            for d in manifest.get("runtime_dependencies", [])
        ],
    }


def _set_worker_limits() -> dict[str, bool]:
    def lower(kind: int, desired: int) -> None:
        _soft, hard = resource.getrlimit(kind)
        bounded = desired if hard == resource.RLIM_INFINITY else min(desired, hard)
        resource.setrlimit(kind, (bounded, hard))

    lower(resource.RLIMIT_CPU, MAX_CPU_SECONDS)
    lower(resource.RLIMIT_FSIZE, MAX_OUTPUT_BYTES)
    lower(resource.RLIMIT_NOFILE, 64)
    memory_enforced = True
    try:
        lower(resource.RLIMIT_AS, MAX_ADDRESS_SPACE)
    except (OSError, ValueError):
        # macOS reports RLIM_INFINITY but rejects lowering RLIMIT_AS. CPU,
        # output-size, descriptor, and parent wall-time limits remain enforced.
        memory_enforced = False
    return {"cpu": True, "output_size": True, "open_files": True, "address_space": memory_enforced}


def _worker(source: Path, target_pdf: Path, target_text: Path) -> dict[str, Any]:
    enforced_limits = _set_worker_limits()
    from pypdf import PdfReader, PdfWriter, __version__ as pypdf_version
    from pypdf.generic import DictionaryObject

    if not source.is_file() or source.stat().st_size > MAX_SOURCE_BYTES:
        raise ValueError("source missing or exceeds limit")
    reader = PdfReader(str(source), strict=False)
    if reader.is_encrypted:
        raise ValueError("encrypted PDF rejected")
    if not reader.pages:
        raise ValueError("zero-page PDF rejected")

    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page, excluded_keys=("/Annots", "/AA", "/A"))
    writer.remove_annotations(None)
    # A fresh writer avoids cloning document-level names, forms, outlines,
    # embedded files, open actions, JavaScript, and remote actions.
    for key in ("/OpenAction", "/AA", "/Names", "/AcroForm", "/Outlines", "/Perms"):
        writer.root_object.pop(key, None)
    # Some malformed PDFs carry additional actions in cloned resource objects.
    # Scrub those exact structural keys from every cloned dictionary. If an
    # action token survives serialization, the independent byte scan still
    # rejects the derivative.
    for obj in writer._objects:
        if not isinstance(obj, DictionaryObject):
            continue
        obj.pop("/AA", None)
        obj.pop("/OpenAction", None)
        obj.pop("/JS", None)
        action_type = obj.get("/S")
        if str(action_type) in {"/URI", "/GoToR", "/SubmitForm", "/ImportData", "/Sound", "/Movie", "/Rendition", "/JavaScript", "/Launch"}:
            obj.pop("/S", None)
            obj.pop("/URI", None)

    target_pdf.parent.mkdir(parents=True, exist_ok=True)
    pdf_tmp = target_pdf.with_suffix(".pdf.tmp")
    text_tmp = target_text.with_suffix(".json.tmp")
    try:
        with pdf_tmp.open("wb") as handle:
            writer.write(handle)
        data = pdf_tmp.read_bytes()
        if not data.startswith(b"%PDF-") or b"%%EOF" not in data[-8192:]:
            raise ValueError("derivative signature/EOF validation failed")
        indicators = active_indicators(data)
        if indicators:
            raise ValueError("active indicators remain: " + ",".join(indicators))

        check = PdfReader(str(pdf_tmp), strict=False)
        if check.is_encrypted or len(check.pages) != len(reader.pages):
            raise ValueError("derivative page/encryption validation failed")
        pages = []
        unicode_replacement_count = 0
        for number, page in enumerate(check.pages, 1):
            if "/Annots" in page or "/AA" in page or "/A" in page:
                raise ValueError(f"page action/annotation remains on page {number}")
            page_text, replacement_count = _replace_invalid_surrogates(page.extract_text() or "")
            unicode_replacement_count += replacement_count
            pages.append({"page": number, "text": page_text})
        payload = {
            "schema_version": "1.0",
            "source_sha256": sha256(source),
            "derivative_sha256": hashlib.sha256(data).hexdigest(),
            "page_count": len(pages),
            "character_count": sum(len(p["text"]) for p in pages),
            "unicode_replacement_count": unicode_replacement_count,
            "pages": pages,
        }
        text_tmp.parent.mkdir(parents=True, exist_ok=True)
        text_tmp.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
        # Re-read before publication so truncated JSON cannot be accepted.
        if len(json.loads(text_tmp.read_text(encoding="utf-8"))["pages"]) != len(pages):
            raise ValueError("text extraction reconciliation failed")
        pdf_tmp.replace(target_pdf)
        text_tmp.replace(target_text)
        return {
            "status": "sanitized_static_extraction_verified",
            "pypdf_version": pypdf_version,
            "source_sha256": payload["source_sha256"],
            "derivative_sha256": payload["derivative_sha256"],
            "text_sha256": sha256(target_text),
            "page_count": payload["page_count"],
            "character_count": payload["character_count"],
            "unicode_replacement_count": payload["unicode_replacement_count"],
            "active_indicators": [],
            "enforced_limits": enforced_limits,
        }
    finally:
        pdf_tmp.unlink(missing_ok=True)
        text_tmp.unlink(missing_ok=True)


def _run_one(source: Path) -> dict[str, Any]:
    fid = source.stem
    target_pdf = SANITIZED / f"{fid}.pdf"
    target_text = TEXT / f"{fid}.json"
    command = [sys.executable, "-m", "gate2.d14_pdf_sanitize", "worker", str(source), str(target_pdf), str(target_text)]
    try:
        completed = subprocess.run(
            command,
            cwd=Path.cwd(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=MAX_WALL_SECONDS,
            env={"PATH": os.environ.get("PATH", ""), "PYTHONPATH": str(Path.cwd())},
            check=False,
        )
        if completed.returncode != 0:
            return {"status": "sanitization_failed", "failure_type": "worker_failure", "returncode": completed.returncode}
        result = json.loads(completed.stdout)
    except subprocess.TimeoutExpired:
        return {"status": "sanitization_failed", "failure_type": "wall_timeout"}
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {"status": "sanitization_failed", "failure_type": type(exc).__name__}

    if result.get("status") != "sanitized_static_extraction_verified":
        return {"status": "sanitization_failed", "failure_type": "unexpected_worker_status"}
    if not target_pdf.exists() or not target_text.exists():
        return {"status": "sanitization_failed", "failure_type": "missing_derivative"}
    if sha256(target_pdf) != result["derivative_sha256"] or sha256(target_text) != result["text_sha256"]:
        return {"status": "sanitization_failed", "failure_type": "published_checksum_mismatch"}
    if active_indicators(target_pdf.read_bytes()):
        return {"status": "sanitization_failed", "failure_type": "published_active_indicator"}
    return result


def sanitize_quarantine(limit: int = 6) -> dict[str, Any]:
    dependency = _dependency_record()
    # Process both directly clean downloads and quarantined originals through
    # one derivative/extraction contract. A family can occur in only one source
    # directory; fail closed if that invariant is violated.
    by_id: dict[str, Path] = {}
    for source in sorted(list(PDFS.glob("CITFAM-*.pdf")) + list(QUARANTINE.glob("CITFAM-*.pdf"))):
        if source.stem in by_id:
            raise ValueError(f"duplicate PDF source for {source.stem}")
        by_id[source.stem] = source
    sources = [by_id[fid] for fid in sorted(by_id)][:limit]
    results = []
    for source in sources:
        result_path = RESULTS / f"{source.stem}.json"
        previous = json.loads(result_path.read_text(encoding="utf-8")) if result_path.exists() else None
        if previous and previous.get("status") == "sanitized_static_extraction_verified":
            result = previous
        else:
            result = {
                "citation_family_id": source.stem,
                "source_path": str(source),
                "source_sha256": sha256(source),
                "attempted_at_utc": _now(),
                "pipeline_version": VERSION,
                "dependency_manifest_sha256": dependency["manifest_sha256"],
                **_run_one(source),
            }
            if previous:
                result["previous_attempt"] = {
                    "attempted_at_utc": previous.get("attempted_at_utc"),
                    "status": previous.get("status"),
                    "failure_type": previous.get("failure_type"),
                    "returncode": previous.get("returncode"),
                }
            _atomic_json(result_path, result)
        results.append(result)
    manifest = {
        "status": "development_pilot_complete" if results else "no_quarantined_inputs",
        "pipeline_version": VERSION,
        "dependency": dependency,
        "source_count": len(results),
        "verified_count": sum(r["status"] == "sanitized_static_extraction_verified" for r in results),
        "failed_count": sum(r["status"] != "sanitized_static_extraction_verified" for r in results),
        "total_pages": sum(r.get("page_count", 0) for r in results),
        "total_characters": sum(r.get("character_count", 0) for r in results),
        "result_hashes": {p.name: sha256(p) for p in sorted(RESULTS.glob("CITFAM-*.json"))},
        "security_boundary": "Project-local pure-Python parser; one bounded subprocess per PDF; originals unchanged; no network, Git/history, secrets, embedded actions, PDF execution, or private systems.",
    }
    _atomic_json(FULLTEXT / "sanitization_manifest.json", manifest)
    return manifest


def verify() -> dict[str, Any]:
    manifest = json.loads((FULLTEXT / "sanitization_manifest.json").read_text(encoding="utf-8"))
    _dependency_record()
    files = sorted(RESULTS.glob("CITFAM-*.json"))
    if {p.name: sha256(p) for p in files} != manifest["result_hashes"]:
        raise ValueError("sanitization result checksum mismatch")
    verified = 0
    for result_path in files:
        result = json.loads(result_path.read_text(encoding="utf-8"))
        if result["status"] != "sanitized_static_extraction_verified":
            continue
        fid = result["citation_family_id"]
        source = Path(result["source_path"])
        derivative = SANITIZED / f"{fid}.pdf"
        text = TEXT / f"{fid}.json"
        if sha256(source) != result["source_sha256"] or sha256(derivative) != result["derivative_sha256"] or sha256(text) != result["text_sha256"]:
            raise ValueError(f"sanitization checksum mismatch: {fid}")
        if active_indicators(derivative.read_bytes()):
            raise ValueError(f"active indicator in derivative: {fid}")
        payload = json.loads(text.read_text(encoding="utf-8"))
        if len(payload["pages"]) != result["page_count"]:
            raise ValueError(f"text page reconciliation failed: {fid}")
        verified += 1
    if verified != manifest["verified_count"]:
        raise ValueError("verified count mismatch")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    pilot = sub.add_parser("pilot")
    pilot.add_argument("--limit", type=int, default=6)
    worker = sub.add_parser("worker")
    worker.add_argument("source", type=Path)
    worker.add_argument("target_pdf", type=Path)
    worker.add_argument("target_text", type=Path)
    sub.add_parser("verify")
    args = parser.parse_args()
    if args.command == "worker":
        print(json.dumps(_worker(args.source, args.target_pdf, args.target_text), sort_keys=True))
    elif args.command == "pilot":
        print(json.dumps(sanitize_quarantine(args.limit), sort_keys=True))
    else:
        print(json.dumps(verify(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
