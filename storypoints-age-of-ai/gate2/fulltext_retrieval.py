"""D10 lawful full-text candidate resolution and bounded retrieval."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile
import time
from datetime import datetime, timezone
from html import unescape
from typing import Any
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests


ROOT = Path(__file__).resolve().parents[1]
SYSTEMATIC = ROOT / "gate2/output/systematic/v1.3/20260816"
D06 = SYSTEMATIC / "d06"
D07 = SYSTEMATIC / "d07"
D09_FINAL = SYSTEMATIC / "d08/d09/final"
OUTPUT = SYSTEMATIC / "d10"
VERSION = "d10-lawful-fulltext/1.0.0"
PREPARED_AT = "2026-08-16T10:42:00Z"


class FullTextError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_doi(value: str | None) -> str:
    value = (value or "").strip().casefold()
    value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value)
    return value.removeprefix("doi:").strip().rstrip(". ")


def normalize_title(value: str | None) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", (value or "").casefold()).split())


def _load_json_pages(base: Path) -> list[dict[str, Any]]:
    rows = []
    for path in sorted(base.rglob("page_*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows.extend(payload.get("results", payload.get("data", [])))
    return rows


def _open_locations() -> tuple[dict[str, list[dict[str, str]]], dict[str, list[dict[str, str]]]]:
    by_doi: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_title: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in _load_json_pages(SYSTEMATIC / "openalex"):
        doi = normalize_doi(row.get("doi"))
        title = normalize_title(row.get("title"))
        locations = []
        best = row.get("best_oa_location") or {}
        if best.get("pdf_url"):
            locations.append({"url": best["pdf_url"], "basis": "openalex_best_oa_pdf",
                              "license": str(best.get("license") or ""), "version": str(best.get("version") or "")})
        for location in row.get("locations") or []:
            if location.get("is_oa") and location.get("pdf_url"):
                locations.append({"url": location["pdf_url"], "basis": "openalex_oa_location_pdf",
                                  "license": str(location.get("license") or ""), "version": str(location.get("version") or "")})
        for location in locations:
            if doi:
                by_doi[doi].append(location)
            if title:
                by_title[title].append(location)
    for row in _load_json_pages(SYSTEMATIC / "semantic_scholar"):
        pdf = row.get("openAccessPdf") or {}
        if not pdf.get("url"):
            continue
        location = {"url": pdf["url"], "basis": "semantic_scholar_open_access_pdf",
                    "license": str(pdf.get("license") or ""), "version": str(pdf.get("status") or "")}
        doi = normalize_doi((row.get("externalIds") or {}).get("DOI"))
        title = normalize_title(row.get("title"))
        if doi:
            by_doi[doi].append(location)
        if title:
            by_title[title].append(location)
    return by_doi, by_title


def _unique_locations(locations: list[dict[str, str]]) -> list[dict[str, str]]:
    seen, result = set(), []
    for row in locations:
        url = row["url"].replace("http://", "https://", 1)
        key = url.casefold()
        if key not in seen:
            seen.add(key)
            result.append({**row, "url": url})
    return result


def build_inventory(output_dir: Path = OUTPUT) -> dict[str, Any]:
    if output_dir.exists():
        raise FullTextError(f"immutable D10 inventory already exists: {output_dir}")
    decisions = [json.loads(line) for line in (D09_FINAL / "final_title_abstract_decisions.jsonl").read_text(encoding="utf-8").splitlines()]
    included = {row["family_id"] for row in decisions if row["final_title_abstract_decision"] == "include"}
    families = {row["family_id"]: row for row in (json.loads(line) for line in (D07 / "study_families.jsonl").read_text(encoding="utf-8").splitlines())}
    with (D06 / "canonical_records.csv").open(encoding="utf-8", newline="") as handle:
        reports = {row["canonical_id"]: row for row in csv.DictReader(handle)}
    by_doi, by_title = _open_locations()
    inventory = []
    for family_id in sorted(included):
        family = families[family_id]
        candidates = []
        member_records = [reports[record_id] for record_id in family["member_canonical_ids"]]
        for report in member_records:
            if report["arxiv_id"]:
                arxiv_id = report["arxiv_id"].split("v", 1)[0]
                candidates.append({"url": f"https://arxiv.org/pdf/{arxiv_id}", "basis": "arxiv_pdf",
                                   "license": "repository_terms", "version": "submitted_version"})
            doi = normalize_doi(report["doi"])
            candidates.extend(by_doi.get(doi, []))
            candidates.extend(by_title.get(normalize_title(report["title"]), []))
            if report["url"].casefold().endswith((".pdf", "/pdf")):
                candidates.append({"url": report["url"], "basis": "metadata_direct_pdf",
                                   "license": "requires_source_verification", "version": "unknown"})
        candidates = _unique_locations(candidates)
        representative = reports[family["representative_canonical_id"]]
        if candidates:
            preliminary = "open_candidate_identified"
        elif representative["url"]:
            preliminary = "landing_page_requires_lawful_access_check"
        else:
            preliminary = "no_location_identified"
        inventory.append({
            "family_id": family_id,
            "representative_canonical_id": family["representative_canonical_id"],
            "title": representative["title"],
            "doi": representative["doi"],
            "arxiv_id": representative["arxiv_id"],
            "landing_page_url": representative["url"],
            "member_canonical_ids": family["member_canonical_ids"],
            "candidate_locations": candidates,
            "preliminary_status": preliminary,
            "retrieval_status": "pending_network_verification",
            "retrieved_location": None,
            "lawful_access_basis": None,
            "attempts": [],
        })
    if len(inventory) != 2076 or len({row["family_id"] for row in inventory}) != 2076:
        raise FullTextError("D10 inventory does not reconcile to D09 includes")

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="d10-", dir=str(output_dir.parent)))
    try:
        inventory_path = staging / "retrieval_inventory.jsonl"
        inventory_path.write_text("".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in inventory), encoding="utf-8")
        counts = Counter(row["preliminary_status"] for row in inventory)
        basis_counts = Counter(location["basis"] for row in inventory for location in row["candidate_locations"])
        manifest = {
            "status": "inventory_complete_retrieval_pending",
            "protocol_version": "1.3", "pipeline_version": VERSION,
            "prepared_at_utc": PREPARED_AT,
            "input_d09_manifest_sha256": sha256(D09_FINAL / "d09_final_manifest.json"),
            "family_count": len(inventory),
            "preliminary_status_counts": dict(sorted(counts.items())),
            "candidate_location_basis_counts": dict(sorted(basis_counts.items())),
            "inventory_sha256": sha256(inventory_path),
            "lawful_access_rule": "Only repository, publisher-open, author-manuscript, preprint, or legitimately authorized locations may be retrieved. Authentication/paywall/technical controls are never bypassed. Metadata and landing pages are not full text.",
            "completion_boundary": "This manifest resolves candidates only. D10 remains incomplete until every family has a terminal retrieved_open, retrieved_authorized, paywalled, unavailable, or no_lawful_full_text status with attempt provenance.",
        }
        manifest_path = staging / "d10_inventory_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (staging / "d10_inventory_manifest.json.sha256").write_text(f"{sha256(manifest_path)}  d10_inventory_manifest.json\n", encoding="utf-8")
        staging.rename(output_dir)
        return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def verify_inventory(output_dir: Path = OUTPUT) -> dict[str, Any]:
    manifest_path = output_dir / "d10_inventory_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    inventory_path = output_dir / "retrieval_inventory.jsonl"
    rows = [json.loads(line) for line in inventory_path.read_text(encoding="utf-8").splitlines()]
    if len(rows) != 2076 or len({row["family_id"] for row in rows}) != 2076:
        raise FullTextError("D10 inventory count/identity mismatch")
    if sha256(inventory_path) != manifest["inventory_sha256"]:
        raise FullTextError("D10 inventory hash mismatch")
    if manifest["input_d09_manifest_sha256"] != sha256(D09_FINAL / "d09_final_manifest.json"):
        raise FullTextError("D10 inventory does not bind current D09")
    if (output_dir / "d10_inventory_manifest.json.sha256").read_text().split()[0] != sha256(manifest_path):
        raise FullTextError("D10 manifest sidecar mismatch")
    return manifest


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def _fetch_one(row: dict[str, Any], output_dir: Path, timeout: int = 60) -> dict[str, Any]:
    family_id = row["family_id"]
    result_path = output_dir / "results" / f"{family_id}.json"
    if result_path.exists():
        existing = json.loads(result_path.read_text(encoding="utf-8"))
        if existing.get("status") == "retrieved_open":
            return existing
    attempts = []
    for candidate in row["candidate_locations"]:
        url = candidate["url"]
        attempt = {"url": url, "basis": candidate["basis"], "attempted_at_utc": utc_now()}
        try:
            response = requests.get(
                url,
                timeout=timeout,
                allow_redirects=True,
                headers={"User-Agent": "VDCM-THINKAI-2026-evidence-map/1.0 (lawful-open-fulltext-retrieval)"},
            )
            attempt.update({"http_status": response.status_code, "final_url": response.url,
                            "content_type": response.headers.get("Content-Type", "")})
            if response.status_code == 429:
                attempt["outcome"] = "rate_limited"
                attempts.append(attempt)
                continue
            if response.status_code in {401, 402, 403}:
                attempt["outcome"] = "access_blocked_or_paywalled"
                attempts.append(attempt)
                continue
            if response.status_code != 200:
                attempt["outcome"] = "http_failure"
                attempts.append(attempt)
                continue
            content = response.content
            if len(content) > 50 * 1024 * 1024:
                attempt["outcome"] = "file_exceeds_50mb_safety_limit"
                attempts.append(attempt)
                continue
            if not content.startswith(b"%PDF-") or len(content) < 5000:
                attempt["outcome"] = "not_a_verified_pdf"
                attempt["bytes"] = len(content)
                attempts.append(attempt)
                continue
            pdf_path = output_dir / "pdf" / f"{family_id}.pdf"
            pdf_path.parent.mkdir(parents=True, exist_ok=True)
            temporary = pdf_path.with_suffix(".pdf.tmp")
            temporary.write_bytes(content)
            temporary.replace(pdf_path)
            attempt.update({"outcome": "retrieved_verified_pdf", "bytes": len(content),
                            "sha256": sha256(pdf_path)})
            attempts.append(attempt)
            result = {
                "family_id": family_id, "representative_canonical_id": row["representative_canonical_id"],
                "status": "retrieved_open", "lawful_access_basis": candidate["basis"],
                "retrieved_url": response.url, "pdf_path": str(pdf_path.relative_to(ROOT)),
                "pdf_sha256": sha256(pdf_path), "bytes": len(content), "attempts": attempts,
            }
            _atomic_json(result_path, result)
            return result
        except requests.RequestException as exc:
            attempt.update({"outcome": "network_error", "error_type": type(exc).__name__})
            attempts.append(attempt)
    result = {
        "family_id": family_id, "representative_canonical_id": row["representative_canonical_id"],
        "status": "candidate_locations_exhausted_no_verified_pdf", "lawful_access_basis": None,
        "retrieved_url": None, "pdf_path": None, "pdf_sha256": None, "bytes": 0,
        "attempts": attempts,
    }
    _atomic_json(result_path, result)
    return result


def fetch_candidates(limit: int | None = None, workers: int = 3, retry_failed: bool = False, output_dir: Path = OUTPUT) -> dict[str, Any]:
    verify_inventory(output_dir)
    rows = [json.loads(line) for line in (output_dir / "retrieval_inventory.jsonl").read_text(encoding="utf-8").splitlines()]
    candidates = [row for row in rows if row["candidate_locations"]]
    existing = {
        path.stem: json.loads(path.read_text(encoding="utf-8"))
        for path in (output_dir / "results").glob("FAM-*.json")
    } if (output_dir / "results").exists() else {}
    pending = [
        row for row in candidates
        if row["family_id"] not in existing
        or (retry_failed and existing[row["family_id"]].get("status") != "retrieved_open")
    ]
    if limit is not None:
        pending = pending[:limit]
    results = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(_fetch_one, row, output_dir): row["family_id"] for row in pending}
        for future in as_completed(futures):
            results.append(future.result())
            time.sleep(0.05)
    all_results = [json.loads(path.read_text(encoding="utf-8")) for path in sorted((output_dir / "results").glob("FAM-*.json"))]
    counts = Counter(row["status"] for row in all_results)
    summary = {
        "status": "retrieval_in_progress",
        "protocol_version": "1.3", "pipeline_version": VERSION,
        "inventory_family_count": len(rows), "candidate_family_count": len(candidates),
        "families_attempted": len(all_results), "this_run_attempted": len(results),
        "result_counts": dict(sorted(counts.items())),
        "pdf_bytes": sum(row.get("bytes", 0) for row in all_results if row["status"] == "retrieved_open"),
        "result_file_hashes": {path.name: sha256(path) for path in sorted((output_dir / "results").glob("FAM-*.json"))},
    }
    _atomic_json(output_dir / "retrieval_progress.json", summary)
    return summary


def migrate_batch_timestamp_label(output_dir: Path = OUTPUT) -> dict[str, Any]:
    """Correct the pre-final pilot label without pretending it was an exact request time."""
    changed = 0
    for path in sorted((output_dir / "results").glob("FAM-*.json")):
        row = json.loads(path.read_text(encoding="utf-8"))
        row_changed = False
        for attempt in row.get("attempts", []):
            if attempt.get("attempted_at_utc") == PREPARED_AT:
                attempt["retrieval_batch_declared_at_utc"] = attempt.pop("attempted_at_utc")
                attempt["timestamp_precision_note"] = "Pilot/batch declaration time; exact HTTP request time was not captured. Corrected before D10 freeze."
                row_changed = True
        if row_changed:
            _atomic_json(path, row)
            changed += 1
    audit = {
        "status": "transparent_pre_final_provenance_correction",
        "correction": "Renamed the fixed pilot timestamp from attempted_at_utc to retrieval_batch_declared_at_utc; no URL, response, status, content, decision, or PDF changed.",
        "corrected_result_files": changed,
        "corrected_at_utc": utc_now(),
        "result_file_hashes_after_correction": {path.name: sha256(path) for path in sorted((output_dir / "results").glob("FAM-*.json"))},
    }
    _atomic_json(output_dir / "timestamp_provenance_correction.json", audit)
    return audit


def _citation_pdf_urls(html: str, base_url: str) -> list[str]:
    from urllib.parse import urljoin
    patterns = (
        r'<meta[^>]+name=["\']citation_pdf_url["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']citation_pdf_url["\']',
    )
    urls = []
    for pattern in patterns:
        for match in re.findall(pattern, html, flags=re.IGNORECASE):
            urls.append(urljoin(base_url, unescape(match)))
    return list(dict.fromkeys(urls))


def _fallback_one(row: dict[str, Any], output_dir: Path, timeout: int = 60) -> dict[str, Any]:
    family_id = row["family_id"]
    result_path = output_dir / "results" / f"{family_id}.json"
    existing = json.loads(result_path.read_text(encoding="utf-8")) if result_path.exists() else None
    if existing and existing.get("status") == "retrieved_open":
        return existing
    attempts = list((existing or {}).get("attempts", []))
    landing_url = row.get("landing_page_url")
    if not landing_url:
        result = {
            "family_id": family_id, "representative_canonical_id": row["representative_canonical_id"],
            "status": "no_lawful_full_text_location_identified", "lawful_access_basis": None,
            "retrieved_url": None, "pdf_path": None, "pdf_sha256": None, "bytes": 0,
            "attempts": attempts,
        }
        _atomic_json(result_path, result)
        return result
    landing_attempt = {"url": landing_url, "basis": "representative_landing_page", "attempted_at_utc": utc_now()}
    try:
        response = requests.get(landing_url, timeout=timeout, allow_redirects=True,
                                headers={"User-Agent": "VDCM-THINKAI-2026-evidence-map/1.0 (lawful-open-fulltext-retrieval)"})
        landing_attempt.update({"http_status": response.status_code, "final_url": response.url,
                                "content_type": response.headers.get("Content-Type", "")})
        if response.status_code == 200 and response.content.startswith(b"%PDF-") and len(response.content) >= 5000:
            pdf_candidates = [(response.url, response.content, "landing_page_direct_pdf")]
        else:
            pdf_candidates = []
            if response.status_code == 200 and "html" in response.headers.get("Content-Type", "").casefold():
                for pdf_url in _citation_pdf_urls(response.text, response.url):
                    pdf_candidates.append((pdf_url, None, "citation_pdf_url_metadata"))
        if response.status_code in {401, 402, 403}:
            landing_attempt["outcome"] = "access_blocked_or_paywalled"
        elif response.status_code == 200:
            landing_attempt["outcome"] = "landing_page_inspected"
        else:
            landing_attempt["outcome"] = "http_failure"
        attempts.append(landing_attempt)
        for pdf_url, content, basis in pdf_candidates:
            pdf_attempt = {"url": pdf_url, "basis": basis, "attempted_at_utc": utc_now()}
            if content is None:
                pdf_response = requests.get(pdf_url, timeout=timeout, allow_redirects=True,
                                            headers={"User-Agent": "VDCM-THINKAI-2026-evidence-map/1.0 (lawful-open-fulltext-retrieval)"})
                content = pdf_response.content
                pdf_attempt.update({"http_status": pdf_response.status_code, "final_url": pdf_response.url,
                                    "content_type": pdf_response.headers.get("Content-Type", "")})
            if len(content) <= 50 * 1024 * 1024 and content.startswith(b"%PDF-") and len(content) >= 5000:
                pdf_path = output_dir / "pdf" / f"{family_id}.pdf"
                pdf_path.parent.mkdir(parents=True, exist_ok=True)
                temporary = pdf_path.with_suffix(".pdf.tmp"); temporary.write_bytes(content); temporary.replace(pdf_path)
                pdf_attempt.update({"outcome": "retrieved_verified_pdf", "bytes": len(content), "sha256": sha256(pdf_path)})
                attempts.append(pdf_attempt)
                result = {"family_id": family_id, "representative_canonical_id": row["representative_canonical_id"],
                          "status": "retrieved_open", "lawful_access_basis": basis,
                          "retrieved_url": pdf_url, "pdf_path": str(pdf_path.relative_to(ROOT)),
                          "pdf_sha256": sha256(pdf_path), "bytes": len(content), "attempts": attempts}
                _atomic_json(result_path, result)
                return result
            pdf_attempt.update({"outcome": "not_a_verified_pdf", "bytes": len(content)})
            attempts.append(pdf_attempt)
    except requests.RequestException as exc:
        landing_attempt.update({"outcome": "network_error", "error_type": type(exc).__name__})
        attempts.append(landing_attempt)
    outcomes = {attempt.get("outcome") for attempt in attempts}
    terminal = "paywalled_or_access_blocked" if "access_blocked_or_paywalled" in outcomes else "lawful_full_text_not_retrieved"
    result = {"family_id": family_id, "representative_canonical_id": row["representative_canonical_id"],
              "status": terminal, "lawful_access_basis": None, "retrieved_url": None,
              "pdf_path": None, "pdf_sha256": None, "bytes": 0, "attempts": attempts}
    _atomic_json(result_path, result)
    return result


def fallback_landings(workers: int = 3, timeout: int = 60, output_dir: Path = OUTPUT) -> dict[str, Any]:
    verify_inventory(output_dir)
    inventory = [json.loads(line) for line in (output_dir / "retrieval_inventory.jsonl").read_text(encoding="utf-8").splitlines()]
    existing = {path.stem: json.loads(path.read_text(encoding="utf-8")) for path in (output_dir / "results").glob("FAM-*.json")}
    pending = [
        row for row in inventory
        if existing.get(row["family_id"], {}).get("status") != "retrieved_open"
        and not any(
            attempt.get("basis") == "representative_landing_page"
            for attempt in existing.get(row["family_id"], {}).get("attempts", [])
        )
    ]
    results = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(_fallback_one, row, output_dir, timeout) for row in pending]
        for future in as_completed(futures):
            results.append(future.result()); time.sleep(0.05)
    all_results = [json.loads(path.read_text(encoding="utf-8")) for path in sorted((output_dir / "results").glob("FAM-*.json"))]
    counts = Counter(row["status"] for row in all_results)
    summary = {"status": "fallback_complete", "family_count": len(inventory), "fallback_attempted": len(results),
               "result_counts": dict(sorted(counts.items())),
               "pdf_bytes": sum(row.get("bytes", 0) for row in all_results if row["status"] == "retrieved_open")}
    _atomic_json(output_dir / "fallback_progress.json", summary)
    return summary


def finalize_d10(output_dir: Path = OUTPUT) -> dict[str, Any]:
    final_dir = output_dir / "final"
    if final_dir.exists():
        raise FullTextError(f"immutable D10 final output already exists: {final_dir}")
    inventory_manifest = verify_inventory(output_dir)
    inventory = {row["family_id"]: row for row in (json.loads(line) for line in (output_dir / "retrieval_inventory.jsonl").read_text(encoding="utf-8").splitlines())}
    result_paths = sorted((output_dir / "results").glob("FAM-*.json"))
    results = {path.stem: json.loads(path.read_text(encoding="utf-8")) for path in result_paths}
    if set(results) != set(inventory):
        raise FullTextError(f"D10 result coverage mismatch: missing={len(set(inventory)-set(results))}, extra={len(set(results)-set(inventory))}")
    allowed = {"retrieved_open", "paywalled_or_access_blocked", "lawful_full_text_not_retrieved", "no_lawful_full_text_location_identified"}
    ledger, pdf_hashes = [], {}
    for family_id in sorted(inventory):
        source, result = inventory[family_id], results[family_id]
        if result.get("status") not in allowed:
            raise FullTextError(f"nonterminal D10 status for {family_id}: {result.get('status')}")
        result_path = output_dir / "results" / f"{family_id}.json"
        if result["status"] == "retrieved_open":
            pdf_path = ROOT / result["pdf_path"]
            if not pdf_path.is_file() or not pdf_path.read_bytes()[:5] == b"%PDF-":
                raise FullTextError(f"retrieved D10 PDF missing/invalid: {family_id}")
            if sha256(pdf_path) != result["pdf_sha256"] or pdf_path.stat().st_size != result["bytes"]:
                raise FullTextError(f"retrieved D10 PDF checksum/size mismatch: {family_id}")
            pdf_hashes[pdf_path.name] = result["pdf_sha256"]
        elif result.get("pdf_path") or result.get("pdf_sha256") or result.get("bytes"):
            raise FullTextError(f"nonretrieved D10 result claims a PDF: {family_id}")
        if result["status"] != "no_lawful_full_text_location_identified" and not result.get("attempts"):
            raise FullTextError(f"D10 terminal result lacks attempt provenance: {family_id}")
        ledger.append({
            "family_id": family_id,
            "representative_canonical_id": result["representative_canonical_id"],
            "title": source["title"], "doi": source["doi"], "arxiv_id": source["arxiv_id"],
            "full_text_status": result["status"], "lawful_access_basis": result.get("lawful_access_basis"),
            "retrieved_url": result.get("retrieved_url"), "pdf_path": result.get("pdf_path"),
            "pdf_sha256": result.get("pdf_sha256"), "result_record_sha256": sha256(result_path),
            "attempt_count": len(result.get("attempts", [])),
        })
    counts = Counter(row["full_text_status"] for row in ledger)
    final_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="d10-final-", dir=str(final_dir.parent)))
    try:
        ledger_path = staging / "fulltext_retrieval_ledger.jsonl"
        ledger_path.write_text("".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in ledger), encoding="utf-8")
        manifest = {
            "status": "complete",
            "protocol_version": "1.3", "pipeline_version": VERSION,
            "finalized_at_utc": utc_now(), "family_count": len(ledger),
            "status_counts": dict(sorted(counts.items())),
            "retrieved_pdf_count": len(pdf_hashes),
            "retrieved_pdf_bytes": sum((output_dir / "pdf" / name).stat().st_size for name in pdf_hashes),
            "input_inventory_manifest_sha256": sha256(output_dir / "d10_inventory_manifest.json"),
            "timestamp_correction_record_sha256": sha256(output_dir / "timestamp_provenance_correction.json"),
            "ledger_sha256": sha256(ledger_path), "pdf_sha256": dict(sorted(pdf_hashes.items())),
            "conservation_pass": sum(counts.values()) == 2076,
            "interpretation_boundary": "Retrieval status is not full-text eligibility, evidence quality, novelty, or citation support. Unretrieved and paywalled reports remain visible in the study-flow ledger; no access control was bypassed.",
        }
        manifest_path = staging / "d10_final_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (staging / "d10_final_manifest.json.sha256").write_text(f"{sha256(manifest_path)}  d10_final_manifest.json\n", encoding="utf-8")
        staging.rename(final_dir)
        return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def verify_final(output_dir: Path = OUTPUT) -> dict[str, Any]:
    final_dir = output_dir / "final"
    manifest_path = final_dir / "d10_final_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    ledger_path = final_dir / "fulltext_retrieval_ledger.jsonl"
    ledger = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines()]
    if len(ledger) != manifest["family_count"] or sha256(ledger_path) != manifest["ledger_sha256"]:
        raise FullTextError("D10 final ledger count/hash mismatch")
    if Counter(row["full_text_status"] for row in ledger) != Counter(manifest["status_counts"]):
        raise FullTextError("D10 final status counts mismatch")
    for name, expected in manifest["pdf_sha256"].items():
        if sha256(output_dir / "pdf" / name) != expected:
            raise FullTextError(f"D10 frozen PDF mismatch: {name}")
    if (final_dir / "d10_final_manifest.json.sha256").read_text().split()[0] != sha256(manifest_path):
        raise FullTextError("D10 final manifest sidecar mismatch")
    if not manifest["conservation_pass"]:
        raise FullTextError("D10 conservation failed")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("inventory", "verify-inventory", "fetch", "migrate-timestamps", "fallback", "finalize", "verify-final"))
    parser.add_argument("--limit", type=int)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--retry-failed", action="store_true")
    args = parser.parse_args()
    result = (build_inventory() if args.command == "inventory" else
              verify_inventory() if args.command == "verify-inventory" else
              migrate_batch_timestamp_label() if args.command == "migrate-timestamps" else
              fallback_landings(args.workers, args.timeout) if args.command == "fallback" else
              finalize_d10() if args.command == "finalize" else
              verify_final() if args.command == "verify-final" else
              fetch_candidates(args.limit, args.workers, args.retry_failed))
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
