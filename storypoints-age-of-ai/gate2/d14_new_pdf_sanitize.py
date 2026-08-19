"""Sanitize the bounded D14 recovery PDFs using the frozen sanitizer contract."""
from __future__ import annotations

import argparse
import json

from gate2.citation_chasing import OUTPUT
import gate2.d14_pdf_sanitize as sanitizer


ROOT = OUTPUT / "newly_resolved_fulltext_v2"
FULLTEXT = ROOT / "fulltext"


def _configure() -> None:
    sanitizer.PDFS = ROOT / "pdf"
    sanitizer.QUARANTINE = ROOT / "quarantine"
    sanitizer.FULLTEXT = FULLTEXT
    sanitizer.SANITIZED = FULLTEXT / "sanitized"
    sanitizer.TEXT = FULLTEXT / "sanitized_text"
    sanitizer.RESULTS = FULLTEXT / "sanitization_results"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("sanitize", "verify"))
    args = parser.parse_args()
    _configure()
    result = sanitizer.sanitize_quarantine(20) if args.command == "sanitize" else sanitizer.verify()
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
