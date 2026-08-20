#!/usr/bin/env python3
"""Verify the RAER v2 design closure without reading held-out labels."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "evaluation/v2/V2_DESIGN_CLOSURE_MANIFEST_v1.0.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors = []
    for name, expected in data["artifacts"].items():
        path = ROOT / name
        if not path.is_file():
            errors.append(f"missing:{name}")
        elif sha256(path) != expected:
            errors.append(f"hash_mismatch:{name}")
    held_out = ROOT / "evaluation/restricted/held_out_test_labels_v1.1.json"
    if held_out.exists():
        errors.append("held_out_release_present")
    result = {
        "status": "PASS" if not errors else "FAIL",
        "artifacts": len(data["artifacts"]),
        "held_out_release": held_out.exists(),
        "errors": errors,
    }
    print(json.dumps(result, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
