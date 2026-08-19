"""Full-pagination arXiv Atom exporter for developmental and frozen D05 runs.

The public CLI remains developmental. Frozen mode is available only through the
D05 controller with exact freeze, registry, and matrix-row hashes.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile
import time
from typing import Callable
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


ENDPOINT = "https://export.arxiv.org/api/query"
ATOM = "{http://www.w3.org/2005/Atom}"
OPEN_SEARCH = "{http://a9.com/-/spec/opensearch/1.1/}"


class ExportError(RuntimeError):
    pass


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _http_fetch(url: str, attempts: int = 3) -> bytes:
    request = Request(url, headers={"User-Agent": "THINKAI-Gate2-development-pilot/0.1"})
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            with urlopen(request, timeout=30) as response:  # nosec: public arXiv endpoint
                return response.read()
        except Exception as exc:  # retry transient API/network failures
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(3 * (attempt + 1))
    raise ExportError(f"arXiv request failed after {attempts} attempts: {last_error}")


def _text(entry: ET.Element, name: str) -> str:
    node = entry.find(ATOM + name)
    return "" if node is None or node.text is None else " ".join(node.text.split())


def _parse_page(payload: bytes) -> tuple[int, int, int, list[dict[str, str]]]:
    try:
        root = ET.fromstring(payload)
        total = int(root.findtext(OPEN_SEARCH + "totalResults", "0"))
        start = int(root.findtext(OPEN_SEARCH + "startIndex", "0"))
        items = int(root.findtext(OPEN_SEARCH + "itemsPerPage", "0"))
    except (ET.ParseError, ValueError) as exc:
        raise ExportError("invalid arXiv Atom/OpenSearch response") from exc
    records: list[dict[str, str]] = []
    for entry in root.findall(ATOM + "entry"):
        record_id = _text(entry, "id")
        if not record_id:
            raise ExportError("arXiv entry lacks an id")
        records.append({
            "arxiv_url": record_id,
            "arxiv_id_version": record_id.rstrip("/").rsplit("/", 1)[-1],
            "title": _text(entry, "title"),
            "abstract": _text(entry, "summary"),
            "published": _text(entry, "published"),
            "updated": _text(entry, "updated"),
            "authors": "; ".join(_text(author, "name") for author in entry.findall(ATOM + "author")),
            "categories": "; ".join(node.attrib.get("term", "") for node in entry.findall(ATOM + "category")),
        })
    return total, start, items, records


def export_query(
    *, query_id: str, query: str, output_dir: str | Path,
    page_size: int = 100, status: str = "development_pilot",
    expected_sentinels: tuple[str, ...] = (),
    fetcher: Callable[[str], bytes] = _http_fetch, pause_seconds: float = 3.0,
    registry_sha256: str = "", freeze_package_sha256: str = "",
    matrix_row_sha256: str = "", from_date: str = "2019-01-01",
    to_date: str = "2026-08-16",
) -> dict[str, object]:
    if status not in {"development_pilot", "systematic_frozen"}:
        raise ExportError("status must be development_pilot or systematic_frozen")
    if not query_id or not query or page_size < 1 or page_size > 2000:
        raise ExportError("query_id/query are required and page_size must be 1..2000")
    target = Path(output_dir)
    if status == "systematic_frozen":
        if not registry_sha256 or not freeze_package_sha256 or not matrix_row_sha256:
            raise ExportError("systematic export requires freeze, matrix-row, and registry hashes")
        if "gate2/output/systematic/v1.3/" not in target.as_posix():
            raise ExportError("systematic export target must be under gate2/output/systematic/v1.3")
    if target.exists():
        raise ExportError(f"immutable export target already exists: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f"arxiv-{status}-", dir=str(target.parent)))
    records: list[dict[str, str]] = []
    pages: list[dict[str, object]] = []
    expected_total: int | None = None
    start = 0
    try:
        while expected_total is None or start < expected_total:
            parameters = {
                "search_query": query, "start": start, "max_results": page_size,
                "sortBy": "submittedDate", "sortOrder": "descending",
            }
            url = ENDPOINT + "?" + urlencode(parameters)
            payload = fetcher(url)
            total, response_start, _, page_records = _parse_page(payload)
            if response_start != start:
                raise ExportError(f"pagination mismatch: requested {start}, response {response_start}")
            if expected_total is None:
                expected_total = total
            elif total != expected_total:
                raise ExportError(f"volatile totalResults during export: {expected_total} -> {total}")
            if not page_records and start < total:
                raise ExportError("empty page before totalResults was exhausted")
            page_name = f"page_{start:07d}.atom"
            (staging / page_name).write_bytes(payload)
            pages.append({"start": start, "records": len(page_records),
                          "file": page_name, "sha256": sha256_bytes(payload)})
            records.extend(page_records)
            start += len(page_records)
            if start < total:
                time.sleep(max(0.0, pause_seconds))

        ids = [record["arxiv_id_version"] for record in records]
        if len(ids) != len(set(ids)):
            raise ExportError("duplicate versioned arXiv ids encountered during pagination")
        base_ids = {re.sub(r"v\d+$", "", record_id) for record_id in ids}
        if status == "systematic_frozen":
            outside = [record["arxiv_id_version"] for record in records
                       if not from_date <= record["published"][:10] <= to_date]
            if outside:
                raise ExportError(f"systematic arXiv results outside frozen date window: {outside[:5]}")
        sentinel_checks = {
            sentinel: re.sub(r"v\d+$", "", sentinel) in base_ids
            for sentinel in expected_sentinels
        }
        fields = ["arxiv_url", "arxiv_id_version", "title", "abstract", "published", "updated", "authors", "categories"]
        csv_path = staging / "records.csv"
        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(records)
        manifest: dict[str, object] = {
            "status": status,
            "interpretation_boundary": (
                "Frozen systematic discovery export; not yet screened, deduplicated, eligible, or a PRISMA inclusion count."
                if status == "systematic_frozen" else
                "Public arXiv query-development export; not frozen and not a PRISMA corpus."
            ),
            "query_id": query_id,
            "query": query,
            "query_sha256": sha256_bytes(query.encode()),
            "query_registry_sha256": registry_sha256,
            "freeze_package_sha256": freeze_package_sha256,
            "acceptance_matrix_row_sha256": matrix_row_sha256,
            "from_date": from_date,
            "to_date": to_date,
            "endpoint": ENDPOINT,
            "sortBy": "submittedDate", "sortOrder": "descending",
            "page_size": page_size,
            "executed_at_utc": datetime.now(timezone.utc).isoformat(),
            "total_reported": expected_total or 0,
            "records_retrieved": len(records),
            "complete_pagination": len(records) == (expected_total or 0),
            "retrieval_scope": "complete_systematic" if status == "systematic_frozen" else "complete",
            "sentinel_checks": sentinel_checks,
            "sentinel_recall_pass": all(sentinel_checks.values()),
            "pages": pages,
            "records_csv": {"file": "records.csv", "sha256": sha256_bytes(csv_path.read_bytes())},
        }
        manifest_path = staging / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (staging / "manifest.sha256").write_text(sha256_bytes(manifest_path.read_bytes()) + "  manifest.json\n", encoding="utf-8")
        staging.rename(target)
        return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("query_id")
    parser.add_argument("query")
    parser.add_argument("output_dir")
    parser.add_argument("--page-size", type=int, default=100)
    parser.add_argument("--sentinel", action="append", default=[])
    args = parser.parse_args()
    manifest = export_query(query_id=args.query_id, query=args.query,
                            output_dir=args.output_dir, page_size=args.page_size,
                            expected_sentinels=tuple(args.sentinel))
    print(json.dumps({key: manifest[key] for key in
                      ("status", "query_id", "total_reported", "records_retrieved", "complete_pagination")},
                     sort_keys=True))


if __name__ == "__main__":
    main()
