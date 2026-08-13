#!/usr/bin/env python3
"""Fail closed on missing artifacts, sealed-data leakage, bad links, and result drift."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "studies" / "ovar"
REQUIRED = {
    "README.md",
    "LICENSE",
    "LICENSE-DATA-DOCS.md",
    "CITATION.cff",
    "pyproject.toml",
    "studies/ovar/README.md",
    "studies/ovar/calibration/candidate_v1.1/construct_review_cases.json",
    "studies/ovar/calibration/implementation/calibration_policies_v1.0.mjs",
    "studies/ovar/calibration/results/calibration_v1.0/calibration_gate.json",
    "studies/ovar/calibration/CALIBRATION_CLOSURE_MANIFEST_v1.0.json",
    "papers/thinkai-2026/manuscript/OVAR_ThinkAI2026_CAMERA_READY_v1.0.docx",
    "papers/thinkai-2026/manuscript/OVAR_ThinkAI2026_CAMERA_READY_v1.0.pdf",
}
PROHIBITED_NAME_PATTERNS = (
    re.compile(r"held[_-]?out", re.IGNORECASE),
    re.compile(r"coordinator.*restricted", re.IGNORECASE),
    re.compile(r"label_access_log", re.IGNORECASE),
)
SECRET_PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "local_workspace_path": re.compile(r"/Users/[^/]+/(?:Library|Desktop|Documents)/"),
}
TEXT_SUFFIXES = {".cff", ".csv", ".js", ".json", ".md", ".mjs", ".py", ".toml", ".txt", ".yml", ".yaml"}
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_closure(errors: list[str]) -> None:
    path = STUDY / "calibration" / "CALIBRATION_CLOSURE_MANIFEST_v1.0.json"
    closure = json.loads(path.read_text(encoding="utf-8"))
    if closure.get("gate_decision") != "STOP_OVAR_V1_NO_HELD_OUT":
        errors.append("calibration closure does not preserve STOP_OVAR_V1_NO_HELD_OUT")
    if closure.get("held_out_created") is not False:
        errors.append("calibration closure no longer records held_out_created=false")
    for artifact in closure.get("artifacts", []):
        target = STUDY / artifact["relative_path"]
        if not target.is_file():
            errors.append(f"closure artifact missing: {target.relative_to(ROOT)}")
        elif sha256(target) != artifact["sha256"]:
            errors.append(f"closure hash mismatch: {target.relative_to(ROOT)}")


def verify_markdown_links(errors: list[str]) -> None:
    for path in ROOT.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for raw in LINK_RE.findall(text):
            target = raw.strip().split("#", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(ROOT)
            except ValueError:
                errors.append(f"markdown link escapes repository: {path.relative_to(ROOT)} -> {raw}")
                continue
            if not resolved.exists():
                errors.append(f"broken markdown link: {path.relative_to(ROOT)} -> {raw}")


def main() -> None:
    errors: list[str] = []
    files = [path for path in ROOT.rglob("*") if path.is_file() and ".git" not in path.parts]

    missing = sorted(item for item in REQUIRED if not (ROOT / item).is_file())
    if missing:
        errors.append(f"required files missing: {missing}")

    for path in files:
        relative = path.relative_to(ROOT)
        if any(pattern.search(path.name) for pattern in PROHIBITED_NAME_PATTERNS):
            errors.append(f"prohibited held-out/private artifact name: {relative}")
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"LICENSE", "Makefile"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{label} pattern in {relative}")

    gate_path = STUDY / "calibration" / "results" / "calibration_v1.0" / "calibration_gate.json"
    gate = json.loads(gate_path.read_text(encoding="utf-8"))
    if gate.get("prospective_gate", {}).get("decision") != "REVISE_OR_STOP_PER_PROTOCOL":
        errors.append("calibration gate is not the frozen negative decision")
    criteria = gate.get("prospective_gate", {}).get("criteria", {})
    if sum(bool(value) for value in criteria.values()) != 5 or len(criteria) != 9:
        errors.append("calibration gate no longer records five of nine criteria passed")

    verify_closure(errors)
    verify_markdown_links(errors)

    if errors:
        raise SystemExit("REPOSITORY VERIFICATION FAILED\n" + "\n".join(sorted(set(errors))))
    print(
        f"PASS: {len(files)} files checked; links valid; held-out artifacts absent; "
        "frozen OVAR v1.0 negative gate preserved"
    )


if __name__ == "__main__":
    main()
