#!/usr/bin/env python3
"""Fail closed on restricted-file, secret-like, and repository-layout mistakes."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROHIBITED_NAMES = {
    "investigator_label_vault.json",
    "held_out_test_labels_v1.1.json",
    "RAER_Benchmark_Coordinator_Master_RESTRICTED_v1.1.xlsx",
    "LABEL_ACCESS_LOG.jsonl",
}
REQUIRED = {
    "README.md", "LICENSE", "CITATION.cff", "pyproject.toml",
    "studies/raer/README.md",
    "studies/raer/evaluation/test_raer_benchmark.py",
    "studies/raer/evaluation/v2/test_raer_v2_design.py",
    "studies/raer/calibration/benchmark/release_v1.1/reviewer_visible_cases.json",
}
SECRET_PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
}
TEXT_SUFFIXES = {".csv", ".json", ".md", ".py", ".toml", ".txt", ".yml", ".yaml", ".cff"}


def main() -> None:
    errors: list[str] = []
    files = [path for path in ROOT.rglob("*") if path.is_file() and ".git" not in path.parts]
    names = {path.name for path in files}
    leaked = sorted(names & PROHIBITED_NAMES)
    if leaked:
        errors.append(f"prohibited files present: {leaked}")
    missing = sorted(item for item in REQUIRED if not (ROOT / item).is_file())
    if missing:
        errors.append(f"required files missing: {missing}")
    for path in files:
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"LICENSE", "Makefile"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{label} pattern in {path.relative_to(ROOT)}")
    labels = ROOT / "studies/raer/evaluation/restricted"
    allowed = {"development_labels_v1.1.json", "validation_labels_v1.1.json"}
    unexpected = sorted(path.name for path in labels.iterdir() if path.is_file() and path.name not in allowed)
    if unexpected:
        errors.append(f"unexpected evaluator label files: {unexpected}")
    gate = json.loads((ROOT / "studies/raer/evaluation/v2/results_design_v1.0/v2_design_gate.json").read_text())
    if gate.get("decision") != "FAIL_KEEP_HELD_OUT_SEALED":
        errors.append("v2 design-gate decision is not the frozen failure decision")
    if errors:
        raise SystemExit("REPOSITORY VERIFICATION FAILED\n" + "\n".join(errors))
    print(f"PASS: {len(files)} files checked; restricted artifacts absent; frozen v2 boundary preserved")


if __name__ == "__main__":
    main()

