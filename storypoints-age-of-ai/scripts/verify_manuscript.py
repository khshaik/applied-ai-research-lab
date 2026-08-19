#!/usr/bin/env python3
"""Fail-closed working/release checks for the THINKAI manuscript package."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gate2.frozen_paths import resolve_frozen_path

PAPER = ROOT / "papers/thinkai-2026"
MANUSCRIPT = PAPER / "manuscript/manuscript_working_draft.md"
LEDGER = PAPER / "manuscript/claim_verification_ledger.md"
ALT_TEXT = PAPER / "figures/ALT_TEXT.md"
SCOPE = ROOT / "gate2/minimum_route_scope.draft.json"
PROTOCOL = ROOT / "research-design/02_systematic_review_protocol.md"
FROZEN_PACKAGE = ROOT / "gate2/frozen_protocol_package_v1.3.json"

BLOCKED_MARKERS = ("EVIDENCE-MAP-RESULT", "CITATION-VERIFY", "VENUE-CHECK", "AUTHOR-INPUT-REQUIRED")
REQUIRED_HEADINGS = (
    "## Abstract",
    "## 1 Introduction",
    "## 2 Related-work positioning",
    "## 3 Research method",
    "## 4 Role-constrained verified delivery framework",
    "## 5 Developmental simulation",
    "## 6 Results",
    "## 7 Discussion",
    "## 8 Threats to validity and limitations",
    "## 9 Ethics and responsible use",
    "## 10 Future Route A validation",
    "## 11 Conclusion",
    "## Declarations",
    "## References",
)
REQUIRED_DECLARATIONS = (
    "declarations/AI_ASSISTANCE_DISCLOSURE.md",
    "declarations/RESEARCH_ETHICS_AND_RESPONSIBLE_USE.md",
    "declarations/DATA_CODE_AVAILABILITY.md",
)
FORBIDDEN_RELEASE_PHRASES = (
    "Story Points stopped working",
    "proves Story Points fail",
    "all relevant literature was searched",
    "no prior research exists",
    "validated human attention",
    "validated cognitive load",
    "universally superior",
)


def _claim_rows(text: str) -> list[list[str]]:
    rows = []
    for line in text.splitlines():
        if re.match(r"^\| CL-\d{3} \|", line):
            rows.append([cell.strip() for cell in line.strip().strip("|").split("|")])
    return rows


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _frozen_protocol_valid(root: Path) -> bool:
    package_path = root / "gate2/frozen_protocol_package_v1.3.json"
    if not package_path.is_file():
        return False
    try:
        package = json.loads(package_path.read_text(encoding="utf-8"))
        if package.get("status") != "frozen" or package.get("approval_decision") != "approve":
            return False
        if package.get("systematic_corpus_created") is not False:
            return False
        for key in ("approved_prefreeze_package", "approval_record"):
            row = package[key]
            path = resolve_frozen_path(root, row["path"])
            if not path.is_file() or _sha256(path) != row["sha256"]:
                return False
        prefreeze = json.loads((root / package["approved_prefreeze_package"]["path"]).read_text(encoding="utf-8"))
        for row in prefreeze["artifacts"]:
            path = resolve_frozen_path(root, row["path"])
            if not path.is_file() or _sha256(path) != row["sha256"]:
                return False
        return True
    except (KeyError, TypeError, ValueError, OSError, json.JSONDecodeError):
        return False


def validate(*, release: bool = False, root: Path = ROOT) -> dict[str, Any]:
    paper = root / "papers/thinkai-2026"
    manuscript_path = paper / "manuscript/manuscript_working_draft.md"
    ledger_path = paper / "manuscript/claim_verification_ledger.md"
    alt_path = paper / "figures/ALT_TEXT.md"
    scope_path = root / "gate2/minimum_route_scope.draft.json"
    protocol_path = root / "research-design/02_systematic_review_protocol.md"
    errors: list[str] = []
    warnings: list[str] = []

    for path in (manuscript_path, ledger_path, alt_path, scope_path, protocol_path):
        if not path.is_file():
            errors.append(f"required manuscript control missing: {path.relative_to(root)}")
    for relative in REQUIRED_DECLARATIONS:
        if not (paper / relative).is_file():
            errors.append(f"required declaration missing: papers/thinkai-2026/{relative}")
    if errors:
        return {"mode": "release" if release else "working", "ready": False,
                "errors": errors, "warnings": warnings}

    manuscript = manuscript_path.read_text(encoding="utf-8")
    ledger = ledger_path.read_text(encoding="utf-8")
    alt_text = alt_path.read_text(encoding="utf-8")
    for heading in REQUIRED_HEADINGS:
        if heading not in manuscript:
            errors.append(f"required manuscript heading missing: {heading}")

    figures = re.findall(r"!\[Figure\s+(\d+)\.[^\]]*\]\(([^)]+)\)", manuscript)
    numbers = [int(number) for number, _ in figures]
    if numbers != list(range(1, 7)):
        errors.append(f"figure numbering must be exactly 1–6; found {numbers}")
    for number, relative in figures:
        target = (manuscript_path.parent / relative).resolve()
        if not target.is_file():
            errors.append(f"Figure {number} target missing: {relative}")
        if f"## Figure {number} " not in alt_text:
            errors.append(f"Figure {number} alt text missing")

    for phrase in FORBIDDEN_RELEASE_PHRASES:
        if phrase.lower() in manuscript.lower():
            errors.append(f"prohibited unqualified manuscript phrase: {phrase}")

    markers = [marker for marker in BLOCKED_MARKERS if marker in manuscript]
    if markers:
        message = f"unresolved manuscript markers: {markers}"
        (errors if release else warnings).append(message)
    if "SIMULATION-RESULT" in manuscript:
        errors.append("simulation results marker remains despite reconciled Route B results")

    claims = _claim_rows(ledger)
    if len(claims) < 10:
        errors.append(f"claim ledger is incomplete: {len(claims)} material rows")
    unconfirmed = [row[0] for row in claims if len(row) < 6 or row[5].lower() != "confirmed"]
    if unconfirmed:
        message = f"material claims lack accountable-author confirmation: {unconfirmed}"
        (errors if release else warnings).append(message)

    ai_disclosure = (paper / REQUIRED_DECLARATIONS[0]).read_text(encoding="utf-8").lower()
    for phrase in ("accountable human author", "not treated as authors", "source", "final manuscript"):
        if phrase not in ai_disclosure:
            errors.append(f"AI disclosure lacks required accountability concept: {phrase}")

    scope = json.loads(scope_path.read_text(encoding="utf-8"))
    protocol = protocol_path.read_text(encoding="utf-8")
    scope_approved = (
        scope.get("effective") is True
        and scope.get("approval", {}).get("decision") == "approve"
    )
    protocol_frozen = _frozen_protocol_valid(root)
    if not scope_approved:
        (errors if release else warnings).append("minimum-route amendment B05 is not approved")
    if not protocol_frozen:
        (errors if release else warnings).append("evidence-map protocol is not frozen")

    return {
        "mode": "release" if release else "working",
        "ready": not errors,
        "errors": errors,
        "warnings": warnings,
        "figures": len(figures),
        "material_claims": len(claims),
        "confirmed_claims": len(claims) - len(unconfirmed),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", action="store_true", help="apply submission hard stops")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate(release=args.release)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"{result['mode']}: {'ready' if result['ready'] else 'not ready'}")
        for item in result["errors"]:
            print(f"ERROR: {item}")
        for item in result["warnings"]:
            print(f"WARN: {item}")
    return 0 if result["ready"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
