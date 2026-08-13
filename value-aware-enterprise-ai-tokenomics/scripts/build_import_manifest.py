#!/usr/bin/env python3
"""Create a deterministic SHA-256 manifest for the Git-ready OVAR package."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "REPOSITORY_IMPORT_MANIFEST.json"


def main() -> None:
    files: dict[str, str] = {}
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or ".git" in path.parts or path == OUTPUT:
            continue
        files[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    document = {
        "manifest_version": "1.0",
        "source": "ThinkAI OVAR internal workspace",
        "status": "GIT_READY_PRIVATE_UNTIL_DOUBLE_BLIND_REVIEW_ENDS",
        "study": "Outcome-Verified AI Resource Allocation v1.0",
        "held_out_benchmark_created_or_included": False,
        "calibration_result": "STOP_OVAR_V1_NO_HELD_OUT",
        "file_count_before_manifest": len(files),
        "files": files,
    }
    OUTPUT.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"WROTE {OUTPUT} with {len(files)} SHA-256 entries")


if __name__ == "__main__":
    main()
