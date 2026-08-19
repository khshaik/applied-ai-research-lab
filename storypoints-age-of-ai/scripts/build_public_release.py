#!/usr/bin/env python3
"""Create a GitHub-ready, provenance-preserving VDCM project export."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXCLUDED_DIR_NAMES = {
    ".git", ".pdf-venv", ".pytest_cache", ".approval_tests_temp",
    "__pycache__", ".mypy_cache", ".ruff_cache", ".venv", "venv",
    "tmp", "qa", "renders", "similarity-reports", "submission-portal-exports",
}
EXCLUDED_FILE_NAMES = {".DS_Store", "Thumbs.db", "context.txt", "temp.txt"}
EXCLUDED_NAME_PATTERNS = {
    ".env", ".env.*", "*.pem", "*.p12", "*.pfx", "*.key",
    "*credential*", "*secret*", "production_seed_manifest*.json",
    "sealed_seed_values*.json", "held_out*.json",
}
THIRD_PARTY_BODY_PATTERNS = {
    "gate2/output/systematic/*/*/d10/pdf/**",
    "gate2/output/systematic/*/*/d11/extraction/text/**",
    "gate2/output/systematic/*/*/d14/fulltext/pdf/**",
    "gate2/output/systematic/*/*/d14/fulltext/quarantine/**",
    "gate2/output/systematic/*/*/d14/fulltext/sanitized/**",
    "gate2/output/systematic/*/*/d14/fulltext/sanitized_text/**",
    "gate2/output/systematic/*/*/d14/newly_resolved_fulltext_v2/pdf/**",
    "gate2/output/systematic/*/*/d14/newly_resolved_fulltext_v2/quarantine/**",
    "gate2/output/systematic/*/*/d14/newly_resolved_fulltext_v2/fulltext/sanitized/**",
    "gate2/output/systematic/*/*/d14/newly_resolved_fulltext_v2/fulltext/sanitized_text/**",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def classify(relative: Path) -> str | None:
    posix = relative.as_posix()
    if any(part in EXCLUDED_DIR_NAMES for part in relative.parts[:-1]):
        return "local_environment_or_temporary"
    if relative.name in EXCLUDED_FILE_NAMES:
        return "session_or_operating_system_file"
    lower_name = relative.name.lower()
    if any(fnmatch.fnmatch(lower_name, pattern.lower()) for pattern in EXCLUDED_NAME_PATTERNS):
        return "secret_restricted_or_sealed_name"
    if "participant_data" in relative.parts or "organizational_event_logs" in relative.parts:
        return "restricted_human_or_organizational_data"
    if "restricted" in relative.parts and relative.name != "README.md":
        return "restricted_study_material"
    if any(fnmatch.fnmatch(posix, pattern) for pattern in THIRD_PARTY_BODY_PATTERNS):
        return "third_party_fulltext_body"
    if relative.suffix in {".pyc", ".pyo", ".log"}:
        return "generated_cache_or_log"
    return None


def build(destination: Path) -> dict:
    if destination.exists():
        raise SystemExit(f"destination must not exist: {destination}")
    destination.mkdir(parents=True)
    included: list[dict] = []
    excluded: list[dict] = []
    for source in sorted(path for path in ROOT.rglob("*") if path.is_file()):
        relative = source.relative_to(ROOT)
        reason = classify(relative)
        record = {
            "path": relative.as_posix(),
            "size_bytes": source.stat().st_size,
            "sha256": sha256(source),
        }
        if reason:
            record["reason"] = reason
            excluded.append(record)
            continue
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        included.append(record)

    manifest = {
        "schema_version": "1.0.0",
        "project": "storypoints-age-of-ai",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_boundary": "research-owned and redistribution-safe artifacts",
        "included_file_count": len(included),
        "included_size_bytes": sum(item["size_bytes"] for item in included),
        "included_files": included,
    }
    exclusions = {
        "schema_version": "1.0.0",
        "project": "storypoints-age-of-ai",
        "excluded_file_count": len(excluded),
        "excluded_size_bytes": sum(item["size_bytes"] for item in excluded),
        "reason_counts": dict(sorted(Counter(item["reason"] for item in excluded).items())),
        "excluded_files": excluded,
        "fulltext_reproducibility_note": (
            "Third-party document bodies are not redistributed. Published metadata, lawful-location "
            "records, hashes, exact locators, short support snippets, and derived decisions preserve "
            "the audit trail."
        ),
    }
    (destination / "PUBLIC_RELEASE_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    (destination / "PUBLIC_RELEASE_EXCLUSIONS.json").write_text(
        json.dumps(exclusions, indent=2) + "\n", encoding="utf-8"
    )
    return {key: manifest[key] for key in ("included_file_count", "included_size_bytes")} | {
        key: exclusions[key] for key in ("excluded_file_count", "excluded_size_bytes", "reason_counts")
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--destination", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.destination.resolve()), indent=2))


if __name__ == "__main__":
    main()
