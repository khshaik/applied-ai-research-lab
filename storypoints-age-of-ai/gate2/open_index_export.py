"""Fail-closed exporters for public scholarly indexes.

The exporters preserve raw API pages, produce a small source-neutral CSV, and
publish an immutable manifest atomically. Development remains the CLI default;
the systematic mode is available only to the frozen D05 controller with exact
freeze-package and acceptance-row hashes.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import time
from typing import Any, Callable
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ENDPOINTS = {
    "openalex": "https://api.openalex.org/works",
    "semantic_scholar": "https://api.semanticscholar.org/graph/v1/paper/search/bulk",
    "crossref": "https://api.crossref.org/works",
}
FIELDS = ["source", "source_id", "doi", "title", "abstract", "published", "authors",
          "venue", "record_type", "cited_by_count", "url"]


class OpenIndexExportError(RuntimeError):
    """A fail-closed retrieval, parsing, or completeness error."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _http_fetch(url: str, attempts: int = 3) -> bytes:
    request = Request(url, headers={
        "User-Agent": "THINKAI-Gate2-open-evidence-development/0.1",
        "Accept": "application/json",
    })
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            with urlopen(request, timeout=30) as response:  # nosec: fixed public scholarly APIs
                return response.read()
        except HTTPError as exc:
            last_error = exc
            if exc.code == 429 and attempt + 1 < attempts:
                retry_after = exc.headers.get("Retry-After", "")
                delay = float(retry_after) if retry_after.isdigit() else 2 ** attempt
                time.sleep(min(60.0, max(1.0, delay)))
                continue
            if 500 <= exc.code < 600 and attempt + 1 < attempts:
                time.sleep(min(30.0, 2 ** attempt))
                continue
            break
        except Exception as exc:  # transient DNS, timeout, TLS, and connection errors
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(min(30.0, 2 ** attempt))
    raise OpenIndexExportError(f"public API request failed after {attempts} attempts: {last_error}")


def _json(payload: bytes) -> dict[str, Any]:
    try:
        value = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise OpenIndexExportError("API returned invalid JSON") from exc
    if not isinstance(value, dict):
        raise OpenIndexExportError("API response root must be an object")
    return value


def _doi(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().lower().removeprefix("https://doi.org/").removeprefix("http://doi.org/").removeprefix("doi:")


def _join_names(authorships: Any, *, crossref: bool = False) -> str:
    if not isinstance(authorships, list):
        return ""
    names: list[str] = []
    for row in authorships:
        if not isinstance(row, dict):
            continue
        if crossref:
            name = " ".join(part for part in (row.get("given", ""), row.get("family", "")) if part)
        else:
            author = row.get("author", row)
            name = author.get("display_name", author.get("name", "")) if isinstance(author, dict) else ""
        if name:
            names.append(str(name).strip())
    return "; ".join(names)


def _openalex_abstract(inverted: Any) -> str:
    if not isinstance(inverted, dict):
        return ""
    positioned: list[tuple[int, str]] = []
    for word, positions in inverted.items():
        if isinstance(positions, list):
            positioned.extend((position, str(word)) for position in positions if isinstance(position, int))
    return " ".join(word for _, word in sorted(positioned))


def _normalize_openalex(row: dict[str, Any]) -> dict[str, Any]:
    primary = row.get("primary_location") or {}
    source = primary.get("source") or {} if isinstance(primary, dict) else {}
    return {
        "source": "OpenAlex", "source_id": row.get("id", ""),
        "doi": _doi(row.get("doi")), "title": row.get("display_name", ""),
        "abstract": _openalex_abstract(row.get("abstract_inverted_index")),
        "published": row.get("publication_date", ""), "authors": _join_names(row.get("authorships")),
        "venue": source.get("display_name", "") if isinstance(source, dict) else "",
        "record_type": row.get("type", ""), "cited_by_count": row.get("cited_by_count", ""),
        "url": primary.get("landing_page_url", "") if isinstance(primary, dict) else "",
    }


def _normalize_semantic(row: dict[str, Any]) -> dict[str, Any]:
    venue = row.get("publicationVenue") or {}
    return {
        "source": "Semantic Scholar", "source_id": row.get("paperId", ""),
        "doi": _doi((row.get("externalIds") or {}).get("DOI")), "title": row.get("title", ""),
        "abstract": row.get("abstract", "") or "", "published": row.get("publicationDate", "") or row.get("year", ""),
        "authors": _join_names(row.get("authors")),
        "venue": venue.get("name", "") if isinstance(venue, dict) else str(row.get("venue", "") or ""),
        "record_type": "; ".join(row.get("publicationTypes") or []),
        "cited_by_count": row.get("citationCount", ""), "url": row.get("url", ""),
    }


def _crossref_date(row: dict[str, Any]) -> str:
    for key in ("published-print", "published-online", "published", "issued"):
        parts = (row.get(key) or {}).get("date-parts", [])
        if parts and isinstance(parts[0], list):
            return "-".join(f"{part:02d}" if index else str(part) for index, part in enumerate(parts[0]))
    return ""


def _normalize_crossref(row: dict[str, Any]) -> dict[str, Any]:
    title = row.get("title") or []
    container = row.get("container-title") or []
    return {
        "source": "Crossref", "source_id": row.get("DOI", ""), "doi": _doi(row.get("DOI")),
        "title": title[0] if title else "", "abstract": row.get("abstract", "") or "",
        "published": _crossref_date(row), "authors": _join_names(row.get("author"), crossref=True),
        "venue": container[0] if container else "", "record_type": row.get("type", ""),
        "cited_by_count": row.get("is-referenced-by-count", ""), "url": row.get("URL", ""),
    }


def _page(source: str, payload: bytes) -> tuple[int, list[dict[str, Any]], str | None]:
    root = _json(payload)
    try:
        if source == "openalex":
            meta, rows = root["meta"], root["results"]
            total, token = int(meta["count"]), meta.get("next_cursor")
            normalizer = _normalize_openalex
        elif source == "semantic_scholar":
            rows = root["data"]
            total, token = int(root["total"]), root.get("token")
            normalizer = _normalize_semantic
        else:
            message = root["message"]
            rows = message["items"]
            total, token = int(message["total-results"]), message.get("next-cursor")
            normalizer = _normalize_crossref
    except (KeyError, TypeError, ValueError) as exc:
        raise OpenIndexExportError(f"invalid {source} pagination response") from exc
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise OpenIndexExportError(f"invalid {source} record list")
    return total, [normalizer(row) for row in rows], str(token) if token else None


def _url(source: str, query: str, *, page_size: int, cursor: str | None,
         from_date: str, to_date: str, query_mode: str = "fulltext_search",
         result_sort: str = "", api_key: str = "") -> str:
    if source == "openalex":
        date_filter = f"from_publication_date:{from_date},to_publication_date:{to_date}"
        if query_mode == "fulltext_search":
            params = {"search": query, "filter": date_filter,
                      "per-page": page_size, "cursor": cursor or "*"}
        elif query_mode == "title_abstract_filter":
            params = {"filter": f"{date_filter},title_and_abstract.search:{query}",
                      "per-page": page_size, "cursor": cursor or "*"}
        else:
            raise OpenIndexExportError(f"unsupported OpenAlex query_mode: {query_mode}")
        if result_sort:
            params["sort"] = result_sort
        if api_key:
            params["api_key"] = api_key
    elif source == "semantic_scholar":
        if query_mode != "fulltext_search":
            raise OpenIndexExportError("Semantic Scholar supports fulltext_search mode only")
        params = {"query": query, "year": f"{from_date[:4]}-{to_date[:4]}", "limit": page_size,
                  "fields": "paperId,externalIds,title,abstract,year,publicationDate,authors,venue,publicationVenue,publicationTypes,citationCount,url"}
        if cursor:
            params["token"] = cursor
    else:
        if query_mode != "fulltext_search":
            raise OpenIndexExportError("Crossref supports fulltext_search mode only")
        params = {"query.bibliographic": query, "filter": f"from-pub-date:{from_date},until-pub-date:{to_date}",
                  "rows": page_size, "cursor": cursor or "*", "select": "DOI,title,abstract,published,published-print,published-online,issued,author,container-title,type,is-referenced-by-count,URL"}
    return ENDPOINTS[source] + "?" + urlencode(params)


def export_query(*, source: str, query_id: str, query: str, output_dir: str | Path,
                 from_date: str = "2019-01-01", to_date: str = "2026-08-15",
                 page_size: int = 100, status: str = "development_pilot",
                 fetcher: Callable[[str], bytes] = _http_fetch,
                 pause_seconds: float = 1.0, registry_sha256: str = "",
                 max_pages: int | None = None,
                 query_mode: str = "fulltext_search", result_sort: str = "",
                 freeze_package_sha256: str = "", matrix_row_sha256: str = "",
                 api_key: str = "") -> dict[str, Any]:
    """Retrieve all records or publish an explicitly truncated development pilot.

    ``max_pages`` is a cost/rate-limit safety valve.  A capped result remains
    useful for query appraisal but is always marked incomplete and cannot be
    interpreted as a source result count or review-flow input.
    """
    if status not in {"development_pilot", "systematic_frozen"}:
        raise OpenIndexExportError("status must be development_pilot or systematic_frozen")
    if source not in ENDPOINTS or not query_id.strip() or not query.strip():
        raise OpenIndexExportError("known source, query_id, and query are required")
    if query_mode not in {"fulltext_search", "title_abstract_filter"}:
        raise OpenIndexExportError("query_mode is unsupported")
    if query_mode == "title_abstract_filter" and source != "openalex":
        raise OpenIndexExportError("title_abstract_filter is restricted to OpenAlex")
    if result_sort and (source != "openalex" or result_sort != "publication_date:desc"):
        raise OpenIndexExportError("result_sort supports only OpenAlex publication_date:desc")
    maximum = {"openalex": 200, "semantic_scholar": 1000, "crossref": 1000}[source]
    if page_size < 1 or page_size > maximum:
        raise OpenIndexExportError(f"page_size must be 1..{maximum} for {source}")
    if max_pages is not None and max_pages < 1:
        raise OpenIndexExportError("max_pages must be positive when provided")
    target = Path(output_dir)
    if status == "systematic_frozen":
        if max_pages is not None:
            raise OpenIndexExportError("systematic export cannot use max_pages")
        if not freeze_package_sha256 or not matrix_row_sha256 or not registry_sha256:
            raise OpenIndexExportError("systematic export requires freeze, matrix-row, and registry hashes")
        normalized = target.as_posix()
        if "gate2/output/systematic/v1.3/" not in normalized:
            raise OpenIndexExportError("systematic export target must be under gate2/output/systematic/v1.3")
        if source == "openalex" and not api_key:
            raise OpenIndexExportError("frozen OpenAlex execution requires OPENALEX_API_KEY")
    if target.exists():
        raise OpenIndexExportError(f"immutable export target already exists: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f"{source}-{status}-", dir=str(target.parent)))
    records: list[dict[str, Any]] = []
    pages: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_tokens: set[str] = set()
    expected_total: int | None = None
    cursor: str | None = None
    try:
        while expected_total is None or len(records) < expected_total:
            request_url = _url(source, query, page_size=page_size, cursor=cursor,
                               from_date=from_date, to_date=to_date,
                               query_mode=query_mode, result_sort=result_sort,
                               api_key=api_key)
            payload = fetcher(request_url)
            total, page_records, next_cursor = _page(source, payload)
            if expected_total is None:
                expected_total = total
            elif total != expected_total:
                raise OpenIndexExportError(f"volatile result total during export: {expected_total} -> {total}")
            if not page_records and len(records) < total:
                raise OpenIndexExportError("empty page before reported total was exhausted")
            for record in page_records:
                record_id = str(record["source_id"])
                if not record_id:
                    raise OpenIndexExportError("source record lacks a stable identifier")
                if record_id in seen_ids:
                    raise OpenIndexExportError(f"duplicate source identifier during pagination: {record_id}")
                seen_ids.add(record_id)
            page_name = f"page_{len(pages):05d}.json"
            (staging / page_name).write_bytes(payload)
            pages.append({"sequence": len(pages), "records": len(page_records), "file": page_name,
                          "sha256": sha256_bytes(payload), "request_url_sha256": sha256_bytes(request_url.encode())})
            records.extend(page_records)
            if len(records) > total:
                raise OpenIndexExportError("retrieved record count exceeds reported total")
            if max_pages is not None and len(pages) >= max_pages and len(records) < total:
                break
            if len(records) < total:
                if not next_cursor:
                    raise OpenIndexExportError("missing continuation token before reported total was exhausted")
                if next_cursor in seen_tokens:
                    raise OpenIndexExportError("pagination continuation token repeated")
                seen_tokens.add(next_cursor)
                cursor = next_cursor
                time.sleep(max(0.0, pause_seconds))

        csv_path = staging / "records.csv"
        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(records)
        complete = len(records) == (expected_total or 0)
        boundary = (
            "Frozen systematic discovery export; not yet screened, deduplicated, eligible, or a PRISMA inclusion count."
            if status == "systematic_frozen" else
            "Open-index development discovery export; not frozen, screened, deduplicated, eligible, or a PRISMA corpus."
        )
        if not complete:
            boundary += " Retrieval was intentionally capped; total_reported is API metadata, not an exported-record or review-flow count."
        manifest: dict[str, Any] = {
            "status": status,
            "interpretation_boundary": boundary,
            "source": source, "query_id": query_id, "query": query,
            "query_mode": query_mode,
            "result_sort": result_sort,
            "query_sha256": sha256_bytes(query.encode()), "query_registry_sha256": registry_sha256,
            "freeze_package_sha256": freeze_package_sha256,
            "acceptance_matrix_row_sha256": matrix_row_sha256,
            "endpoint": ENDPOINTS[source], "from_date": from_date, "to_date": to_date,
            "authentication": {
                "method": "api_key_environment" if source == "openalex" and api_key else "none",
                "credential_logged": False,
            },
            "page_size": page_size, "executed_at_utc": datetime.now(timezone.utc).isoformat(),
            "total_reported": expected_total or 0, "records_retrieved": len(records),
            "complete_pagination": complete,
            "retrieval_scope": "complete_systematic" if complete and status == "systematic_frozen" else ("complete" if complete else "truncated_development_pilot"),
            "max_pages": max_pages, "pages": pages,
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


def load_registry(path: str | Path) -> tuple[dict[str, Any], str]:
    payload = Path(path).read_bytes()
    registry = _json(payload)
    if registry.get("status") != "development_pilot":
        raise OpenIndexExportError("query registry must be development_pilot")
    rows = registry.get("queries")
    if not isinstance(rows, list) or not rows:
        raise OpenIndexExportError("query registry requires a non-empty queries array")
    seen: set[tuple[str, str]] = set()
    for row in rows:
        if not isinstance(row, dict) or row.get("source") not in ENDPOINTS or not row.get("query_id") or not row.get("query"):
            raise OpenIndexExportError("invalid query registry row")
        mode = row.get("query_mode", "fulltext_search")
        if mode not in {"fulltext_search", "title_abstract_filter"}:
            raise OpenIndexExportError("invalid query_mode in registry row")
        if mode == "title_abstract_filter" and row.get("source") != "openalex":
            raise OpenIndexExportError("title_abstract_filter registry rows must use OpenAlex")
        result_sort = row.get("result_sort", "")
        if result_sort and (row.get("source") != "openalex" or result_sort != "publication_date:desc"):
            raise OpenIndexExportError("invalid result_sort in registry row")
        key = (row["source"], row["query_id"])
        if key in seen:
            raise OpenIndexExportError(f"duplicate registry source/query_id: {key}")
        seen.add(key)
    return registry, sha256_bytes(payload)


def resolve_registry_query(path: str | Path, source: str, query_id: str,
                           literal_query: str | None = None) -> tuple[str, str]:
    """Resolve one exact registry query and its content hash, or fail closed."""
    registry, digest = load_registry(path)
    matches = [row for row in registry["queries"]
               if row["source"] == source and row["query_id"] == query_id]
    if len(matches) != 1:
        raise OpenIndexExportError(
            f"registry must contain exactly one {source}/{query_id} query; found {len(matches)}"
        )
    registered = str(matches[0]["query"])
    if literal_query is not None and literal_query != registered:
        raise OpenIndexExportError("literal query conflicts with the exact registered query")
    return registered, digest


def resolve_registry_entry(path: str | Path, source: str, query_id: str,
                           literal_query: str | None = None) -> tuple[dict[str, Any], str]:
    """Resolve one exact query row including its source-specific execution mode."""
    registry, digest = load_registry(path)
    matches = [row for row in registry["queries"]
               if row["source"] == source and row["query_id"] == query_id]
    if len(matches) != 1:
        raise OpenIndexExportError(
            f"registry must contain exactly one {source}/{query_id} query; found {len(matches)}"
        )
    row = dict(matches[0])
    if literal_query is not None and literal_query != row["query"]:
        raise OpenIndexExportError("literal query conflicts with the exact registered query")
    row["query_mode"] = row.get("query_mode", "fulltext_search")
    row["result_sort"] = row.get("result_sort", "")
    return row, digest


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", choices=sorted(ENDPOINTS))
    parser.add_argument("query_id")
    parser.add_argument("output_dir")
    parser.add_argument("--registry", required=True,
                        help="development query registry; its exact bytes are hashed into the manifest")
    parser.add_argument("--literal-query",
                        help="optional assertion only; must exactly equal the registered query")
    parser.add_argument("--from-date", default="2019-01-01")
    parser.add_argument("--to-date", default="2026-08-15")
    parser.add_argument("--page-size", type=int, default=100)
    parser.add_argument("--max-pages", type=int)
    args = parser.parse_args(argv)
    entry, registry_digest = resolve_registry_entry(
        args.registry, args.source, args.query_id, args.literal_query
    )
    manifest = export_query(source=args.source, query_id=args.query_id, query=entry["query"],
                            output_dir=args.output_dir, from_date=args.from_date,
                            to_date=args.to_date, page_size=args.page_size,
                            max_pages=args.max_pages, registry_sha256=registry_digest,
                            query_mode=entry["query_mode"], result_sort=entry["result_sort"])
    print(json.dumps({key: manifest[key] for key in
                      ("status", "source", "query_id", "total_reported", "records_retrieved", "complete_pagination")},
                     sort_keys=True))


if __name__ == "__main__":
    main()
