"""Resolve legacy paths from byte-frozen protocol packages after relocation."""

from __future__ import annotations

import json
from pathlib import Path


RELOCATION_RECORD_GLOB = "*RELOCATION*2026-08-20.json"


def resolve_frozen_path(root: Path, declared_path: str) -> Path:
    """Follow audited relocation records until the declared artifact is found."""
    traceability = root / "docs/traceability"
    destinations: dict[str, str] = {}
    for record_path in sorted(traceability.glob(RELOCATION_RECORD_GLOB)):
        record = json.loads(record_path.read_text(encoding="utf-8"))
        for item in record.get("relocations", []):
            old = item.get("original_path")
            new = item.get("relocated_path", item.get("destination_path"))
            if isinstance(old, str) and isinstance(new, str):
                destinations[old] = new

    candidate = declared_path
    visited: set[str] = set()
    while candidate not in visited:
        visited.add(candidate)
        direct = root / candidate
        if direct.is_file():
            return direct
        replacement = destinations.get(candidate)
        if replacement is None:
            return direct
        candidate = replacement
    raise ValueError(f"relocation cycle detected for {declared_path}")
