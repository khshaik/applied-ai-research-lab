"""Deterministic D06 normalization and exact-report deduplication."""
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
import unicodedata
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "gate2/output/systematic/v1.3/20260816"
PLAN = ROOT / "gate2/d05_execution_manifest_v1.3.json"
RECONCILIATION = CORPUS / "d05_reconciliation.json"
OUTPUT = CORPUS / "d06"
VERSION = "d06-normalize-deduplicate/1.0.0"
DECIDED_AT = "2026-08-16T09:15:11Z"


class DeduplicationError(RuntimeError):
    pass


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def normalize_doi(value: str) -> str:
    value = clean(value).lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if value.startswith(prefix):
            value = value[len(prefix):]
    return value.rstrip(" .")


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKD", clean(value)).casefold()
    value = "".join(c for c in value if not unicodedata.combining(c))
    return " ".join(re.findall(r"[a-z0-9]+", value))


def arxiv_base(*values: str) -> str:
    patterns = (
        r"10\.48550/arxiv\.([0-9]{4}\.[0-9]{4,5}|[a-z-]+/[0-9]{7})",
        r"arxiv\.org/(?:abs|pdf)/([0-9]{4}\.[0-9]{4,5}|[a-z-]+/[0-9]{7})",
        r"^([0-9]{4}\.[0-9]{4,5}|[a-z-]+/[0-9]{7})(?:v[0-9]+)?$",
    )
    for raw in values:
        value = clean(raw).lower()
        for pattern in patterns:
            match = re.search(pattern, value)
            if match:
                return match.group(1)
    return ""


def first_author(value: str) -> str:
    first = clean(value).split(";", 1)[0]
    return normalize_text(first)


def publication_year(value: str) -> str:
    match = re.match(r"^(19|20)\d{2}", clean(value))
    return match.group(0) if match else ""


def _record_id(query_id: str, source: str, source_id: str, row_number: int) -> str:
    token = f"{query_id}|{source}|{source_id}|{row_number}".encode()
    return "REC-" + sha256_bytes(token)[:20]


def _source_rows(run: dict[str, Any]) -> list[dict[str, str]]:
    path = ROOT / run["output_dir"] / "records.csv"
    if not path.is_file():
        raise DeduplicationError(f"records CSV missing: {path.relative_to(ROOT)}")
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_occurrences() -> list[dict[str, Any]]:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    reconciliation = json.loads(RECONCILIATION.read_text(encoding="utf-8"))
    if reconciliation.get("status") != "complete" or reconciliation.get("completed_runs") != 18:
        raise DeduplicationError("D05 must reconcile all 18 runs before D06")
    occurrences: list[dict[str, Any]] = []
    for run in plan["runs"]:
        rows = _source_rows(run)
        for row_number, source_row in enumerate(rows, 1):
            if run["source_key"] == "arxiv":
                source = "arXiv"
                source_id = clean(source_row.get("arxiv_id_version"))
                url = clean(source_row.get("arxiv_url"))
                doi = ""
                record_type = "preprint"
                venue = "arXiv"
                updated = clean(source_row.get("updated"))
            else:
                source = clean(source_row.get("source"))
                source_id = clean(source_row.get("source_id"))
                url = clean(source_row.get("url"))
                doi = normalize_doi(source_row.get("doi", ""))
                record_type = clean(source_row.get("record_type"))
                venue = clean(source_row.get("venue"))
                updated = ""
            if not source_id:
                raise DeduplicationError(f"{run['query_id']} row {row_number} lacks source ID")
            title = clean(source_row.get("title"))
            authors = clean(source_row.get("authors"))
            published = clean(source_row.get("published"))
            abstract = clean(source_row.get("abstract"))
            rid = _record_id(run["query_id"], source, source_id, row_number)
            normalized_title = normalize_text(title)
            author = first_author(authors)
            year = publication_year(published)
            arxiv = arxiv_base(doi, source_id, url)
            occurrence = {
                "record_id": rid,
                "retrieval_batch_id": run["query_id"],
                "search_family": run["family_id"],
                "source": source,
                "source_id": source_id,
                "source_row_number": row_number,
                "doi": doi,
                "arxiv_id": arxiv,
                "title": title,
                "normalized_title": normalized_title,
                "authors": authors,
                "normalized_first_author": author,
                "published": published,
                "publication_year": year,
                "updated": updated,
                "abstract": abstract,
                "venue": venue,
                "record_type": record_type,
                "url": url,
                "evidence_stratum_candidate": "preprint_scholarly" if arxiv or source == "arXiv" else "scholarly_status_unverified",
            }
            occurrence["metadata_sha256"] = sha256_bytes(
                json.dumps(occurrence, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
            )
            occurrences.append(occurrence)
    expected = sum(r["records_retrieved"] for r in reconciliation["runs"])
    if len(occurrences) != expected:
        raise DeduplicationError(f"raw occurrence mismatch: {len(occurrences)} != {expected}")
    if len({r["record_id"] for r in occurrences}) != len(occurrences):
        raise DeduplicationError("record ID collision")
    return occurrences


class UnionFind:
    def __init__(self, size: int):
        self.parent = list(range(size))

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[max(ra, rb)] = min(ra, rb)


def _keys(row: dict[str, Any]) -> list[tuple[str, str]]:
    result = [("provider_id", f"{row['source']}|{row['source_id']}")]
    if row["doi"]:
        result.append(("doi", row["doi"]))
    if row["arxiv_id"]:
        result.append(("arxiv_related_doi", row["arxiv_id"]))
    if (len(row["normalized_title"]) >= 20 and row["normalized_first_author"]
            and row["publication_year"]):
        result.append(("title_author_year", "|".join((
            row["normalized_title"], row["normalized_first_author"], row["publication_year"]
        ))))
    return result


def _completeness(row: dict[str, Any]) -> tuple[Any, ...]:
    populated = sum(bool(row[k]) for k in ("doi", "arxiv_id", "title", "authors", "published", "abstract", "venue", "url"))
    source_priority = {"OpenAlex": 3, "Semantic Scholar": 2, "arXiv": 1}.get(row["source"], 0)
    return (populated, len(row["abstract"]), bool(row["doi"]), source_priority,
            row["updated"], row["published"], row["record_id"])


def deduplicate(occurrences: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    uf = UnionFind(len(occurrences))
    key_owner: dict[tuple[str, str], int] = {}
    for index, row in enumerate(occurrences):
        for key in _keys(row):
            if key in key_owner:
                uf.union(index, key_owner[key])
            else:
                key_owner[key] = index
    groups: dict[int, list[int]] = defaultdict(list)
    for index in range(len(occurrences)):
        groups[uf.find(index)].append(index)

    canonical: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    clusters: list[dict[str, Any]] = []
    basis_counter: Counter[str] = Counter()
    for cluster_number, indexes in enumerate(sorted(groups.values(), key=lambda xs: min(occurrences[i]["record_id"] for i in xs)), 1):
        representative_index = max(indexes, key=lambda i: _completeness(occurrences[i]))
        representative = occurrences[representative_index]
        members = sorted((occurrences[i] for i in indexes), key=lambda r: r["record_id"])
        family_ids = sorted({m["search_family"] for m in members})
        batch_ids = sorted({m["retrieval_batch_id"] for m in members})
        sources = sorted({m["source"] for m in members})
        canonical_id = "CAN-" + sha256_bytes("|".join(m["record_id"] for m in members).encode())[:20]
        canonical.append({
            "canonical_id": canonical_id,
            "representative_record_id": representative["record_id"],
            "member_count": len(members),
            "search_families": ";".join(family_ids),
            "retrieval_batches": ";".join(batch_ids),
            "sources": ";".join(sources),
            **{k: representative[k] for k in (
                "doi", "arxiv_id", "title", "normalized_title", "authors",
                "normalized_first_author", "published", "publication_year",
                "abstract", "venue", "record_type", "url", "evidence_stratum_candidate"
            )},
        })
        cluster_signals = sorted({kind for member in members for kind, _ in _keys(member)})
        clusters.append({
            "cluster_id": canonical_id,
            "representative_record_id": representative["record_id"],
            "member_record_ids": [m["record_id"] for m in members],
            "member_count": len(members),
            "linkage_signals": cluster_signals,
            "sources": sources,
            "search_families": family_ids,
        })
        rep_keys = set(_keys(representative))
        for member in members:
            if member["record_id"] == representative["record_id"]:
                continue
            shared = rep_keys & set(_keys(member))
            priority = ("doi", "arxiv_related_doi", "title_author_year", "provider_id")
            chosen = next((kind for kind in priority if any(key[0] == kind for key in shared)), None)
            if chosen is None:
                chosen = "manual_exact_duplicate"
                evidence = f"transitive exact-identifier cluster {canonical_id}; reviewable member linkage preserved"
            else:
                evidence_value = next(key[1] for key in shared if key[0] == chosen)
                if chosen == "provider_id":
                    chosen = "manual_exact_duplicate"
                    evidence = f"exact repeated provider record {evidence_value} across frozen query batches"
                else:
                    evidence = f"exact normalized {chosen} match: {evidence_value}"
            basis_counter[chosen] += 1
            decisions.append({
                "deduplication_id": "DEDUP-" + sha256_bytes(member["record_id"].encode())[:16],
                "removed_record_id": member["record_id"],
                "retained_record_id": representative["record_id"],
                "canonical_id": canonical_id,
                "match_basis": chosen,
                "evidence": evidence,
                "decider_id": VERSION,
                "decided_at_utc": DECIDED_AT,
            })
    if len(decisions) != len(occurrences) - len(canonical):
        raise DeduplicationError("deduplication conservation failed")
    return canonical, decisions, clusters


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise DeduplicationError(f"refusing empty output: {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def build(output_dir: Path = OUTPUT) -> dict[str, Any]:
    if output_dir.exists():
        raise DeduplicationError(f"immutable D06 output already exists: {output_dir}")
    occurrences = load_occurrences()
    canonical, decisions, clusters = deduplicate(occurrences)
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="d06-", dir=str(output_dir.parent)))
    try:
        files = {
            "normalized_occurrences.csv": occurrences,
            "canonical_records.csv": canonical,
            "deduplication_decisions.csv": decisions,
        }
        for name, rows in files.items():
            _write_csv(staging / name, rows)
        cluster_path = staging / "duplicate_clusters.jsonl"
        cluster_path.write_text("".join(json.dumps(x, sort_keys=True, ensure_ascii=False) + "\n" for x in clusters), encoding="utf-8")
        basis = Counter(row["match_basis"] for row in decisions)
        histogram = Counter(str(row["member_count"]) for row in clusters)
        manifest = {
            "status": "complete",
            "protocol_version": "1.3",
            "pipeline_version": VERSION,
            "decided_at_utc": DECIDED_AT,
            "input_reconciliation_path": str(RECONCILIATION.relative_to(ROOT)),
            "input_reconciliation_sha256": sha256(RECONCILIATION),
            "raw_occurrence_count": len(occurrences),
            "canonical_record_count": len(canonical),
            "duplicates_removed_count": len(decisions),
            "duplicate_cluster_count": sum(c["member_count"] > 1 for c in clusters),
            "singleton_count": sum(c["member_count"] == 1 for c in clusters),
            "match_basis_counts": dict(sorted(basis.items())),
            "cluster_size_histogram": dict(sorted(histogram.items(), key=lambda x: int(x[0]))),
            "conservation_pass": len(occurrences) == len(canonical) + len(decisions),
            "auto_merge_rules": ["exact provider identity", "exact normalized DOI", "exact arXiv/related DOI", "exact normalized title plus first author plus year"],
            "prohibited_auto_merges": ["fuzzy title", "semantic similarity", "shared authors without exact title/year", "preprint-to-published inference"],
            "interpretation_boundary": "Report-level exact deduplication only. Candidate study-version relationships remain for D07; no eligibility or PRISMA inclusion decision is made.",
            "files": {},
        }
        for path in sorted(staging.iterdir()):
            if path.name.startswith("d06_manifest"):
                continue
            manifest["files"][path.name] = {"sha256": sha256(path), "bytes": path.stat().st_size}
        manifest_path = staging / "d06_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (staging / "d06_manifest.json.sha256").write_text(f"{sha256(manifest_path)}  d06_manifest.json\n", encoding="utf-8")
        staging.rename(output_dir)
        return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def verify(output_dir: Path = OUTPUT) -> dict[str, Any]:
    manifest_path = output_dir / "d06_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for name, metadata in manifest["files"].items():
        path = output_dir / name
        if sha256(path) != metadata["sha256"] or path.stat().st_size != metadata["bytes"]:
            raise DeduplicationError(f"D06 file mismatch: {name}")
    if (output_dir / "d06_manifest.json.sha256").read_text().split()[0] != sha256(manifest_path):
        raise DeduplicationError("D06 manifest sidecar mismatch")
    if not manifest["conservation_pass"] or manifest["raw_occurrence_count"] != manifest["canonical_record_count"] + manifest["duplicates_removed_count"]:
        raise DeduplicationError("D06 count conservation failed")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("run", "verify"))
    args = parser.parse_args()
    result = build() if args.command == "run" else verify()
    print(json.dumps({k: result[k] for k in ("status", "raw_occurrence_count", "canonical_record_count", "duplicates_removed_count", "conservation_pass")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
