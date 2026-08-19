"""Resolve legacy paths from byte-frozen protocol packages after relocation."""

from __future__ import annotations

import json
from pathlib import Path


RELOCATION_RECORD = Path("docs/traceability/RESEARCH_DESIGN_RELOCATION_2026-08-20.json")


def resolve_frozen_path(root: Path, declared_path: str) -> Path:
    """Return the declared path or its audited relocation without mutating history."""
    direct = root / declared_path
    if direct.is_file():
        return direct
    record_path = root / RELOCATION_RECORD
    if not record_path.is_file():
        return direct
    record = json.loads(record_path.read_text(encoding="utf-8"))
    destinations = {
        item["original_path"]: item["relocated_path"]
        for item in record.get("relocations", [])
    }
    relocated = destinations.get(declared_path)
    return root / relocated if relocated else direct

