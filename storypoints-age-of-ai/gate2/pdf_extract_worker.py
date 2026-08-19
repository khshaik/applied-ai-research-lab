"""Isolated, non-executing text extraction worker for one untrusted PDF."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PyPDF2 import PdfReader


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _active_content_indicators(reader: PdfReader) -> list[str]:
    indicators = []
    try:
        root = reader.trailer["/Root"]
        for key in ("/OpenAction", "/AA"):
            if key in root:
                indicators.append(key)
        names = root.get("/Names")
        if names:
            names = names.get_object()
            for key in ("/JavaScript", "/EmbeddedFiles"):
                if key in names:
                    indicators.append(f"/Names{key}")
    except Exception:
        indicators.append("catalog_indicator_check_failed")
    return indicators


def extract(pdf_path: Path, output_path: Path) -> dict:
    if pdf_path.stat().st_size > 50 * 1024 * 1024:
        raise ValueError("PDF exceeds frozen 50 MB extraction safety limit")
    reader = PdfReader(str(pdf_path), strict=False)
    if reader.is_encrypted and reader.decrypt("") == 0:
        raise ValueError("encrypted PDF cannot be opened with an empty password")
    if len(reader.pages) > 500:
        raise ValueError("PDF exceeds frozen 500-page extraction safety limit")
    pages = []
    failed_pages = []
    for index, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
            # Some malformed PDFs expose lone UTF-16 surrogate code points.
            # Replace only those unencodable code points; retain all valid text.
            text = text.encode("utf-8", errors="replace").decode("utf-8")
        except Exception as exc:
            text = ""
            failed_pages.append({"page": index, "error_type": type(exc).__name__})
        pages.append({"page": index, "char_count": len(text), "text": text})
    result = {
        "status": "text_extracted" if any(row["char_count"] for row in pages) else "no_extractable_text",
        "pdf_path": str(pdf_path), "pdf_sha256": sha256(pdf_path),
        "pdf_bytes": pdf_path.stat().st_size, "page_count": len(pages),
        "extracted_char_count": sum(row["char_count"] for row in pages),
        "failed_pages": failed_pages,
        "active_content_indicators_not_executed": _active_content_indicators(reader),
        "pages": pages,
        "security_boundary": "Static text extraction only. Embedded actions, JavaScript, attachments, links, and macros were not executed.",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(output_path)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = extract(args.pdf, args.output)
    print(json.dumps({key: result[key] for key in ("status", "page_count", "extracted_char_count")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
